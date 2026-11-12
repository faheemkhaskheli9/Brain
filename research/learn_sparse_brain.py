"""Reproducible no-backprop reward learning and structural-growth diagnostic.

Run the confirmatory seed split once after preregistration; failed runs are
recorded explicitly. This task is intentionally tiny and artificially biased
against fixed topology: its initial edges omit the only predictive input.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import sys
import time
from pathlib import Path

from result_schema import bootstrap_ci, make_result, sign_flip, validate
from sparse_brain_tasks import trials
from structural_plasticity import PlasticityConfig, SparsePlasticPolicy

ARMS = ('evidence', 'random_growth', 'fixed', 'frozen', 'shuffled_feedback', 'privileged_topology')
INITIAL_EDGES = ((1, 0), (1, 1), (2, 0), (2, 1))  # intentionally nonpredictive
PRIVILEGED_EDGES = ((0, 0), (0, 1), (1, 0), (1, 1))  # label-aware architectural comparator
PRECOMMITTED_SEEDS = tuple(range(101, 111))  # fresh after tuning on exploratory 0..9
TRAIN_STEPS = 1000
EVAL_TRIALS = 400


def run_seed(seed: int, train_steps: int, eval_trials: int) -> list[dict]:
    """Same training/evaluation environments for each arm, no hidden labels in act()."""
    if type(seed) is not int or type(train_steps) is not int or type(eval_trials) is not int or seed < 0 or train_steps < 1 or eval_trials < 1:
        raise ValueError('Invalid seed or budget')
    config = PlasticityConfig()
    train = trials('train', seed, train_steps)
    source_check = trials('train', seed + 20000, eval_trials)
    heldout = trials('eval', seed + 10000, eval_trials)
    # Independent verifier-only shuffled reward stream; no current trial labels.
    feedback_random = random.Random(seed * 10007 + 97)
    shuffled_rewards = [feedback_random.choice((-1, 1)) for _ in range(train_steps)]
    result = []
    for arm in ARMS:
        mode = {'evidence': 'evidence', 'random_growth': 'random',
                'shuffled_feedback': 'evidence'}.get(arm, 'off')
        model = SparsePlasticPolicy(config, seed + 11, growth_mode=mode,
                                    learn=arm != 'frozen',
                                    initial_edges=PRIVILEGED_EDGES if arm == 'privileged_topology' else INITIAL_EDGES)
        started = time.perf_counter()
        early, late = [], []
        try:
            for t, task in enumerate(train):
                action = model.act(task.observe(), explore=True)
                observed_reward = task.reward(action)
                if t < min(100, train_steps):
                    early.append(observed_reward > 0)
                if t >= max(0, train_steps - 100):
                    late.append(observed_reward > 0)
                if model.learn:
                    model.feedback(shuffled_rewards[t] if arm == 'shuffled_feedback' else observed_reward)
            checkpoint_before = model.fingerprint()
            source_hits = sum(t.reward(model.act(t.observe(), explore=False)) > 0 for t in source_check)
            eval_hits = sum(t.reward(model.act(t.observe(), explore=False)) > 0 for t in heldout)
            if model.fingerprint() != checkpoint_before:
                raise RuntimeError('Frozen testing changed learning or random state')
            state = model.export_state()
            state_hash = hashlib.sha256(json.dumps(state, sort_keys=True).encode('utf-8')).hexdigest()
            seconds = time.perf_counter() - started
            scores = {'heldoutSuccess': eval_hits / eval_trials,
                      'sourceSuccess': source_hits / eval_trials,
                      'trainEarlySuccess': sum(early) / len(early),
                      'trainLateSuccess': sum(late) / len(late),
                      'synapses': len(model.edges), 'newSynapses': model.new_edges,
                      'prunedSynapses': model.removed_edges,
                      'weightedProducts': model.synaptic_products,
                      'candidateProducts': model.candidate_products,
                      'candidateEvictions': model.candidate_evictions}
            result.append({'arm': arm, 'seed': seed, 'split': 'eval', 'status': 'ok',
                           'seconds': seconds, 'scores': scores,
                           'checkpoint': state_hash,
                           'connectionTopology': [[i,j] for i,j in sorted(model.edges)]})
        except Exception as exc:
            result.append({'arm': arm, 'seed': seed, 'split': 'eval', 'status': 'error',
                           'reason': f'{type(exc).__name__}: {exc}', 'scores': {},
                           'seconds': time.perf_counter() - started, 'checkpoint': None})
    return result


def experiment(seeds: tuple[int, ...] = PRECOMMITTED_SEEDS, *,
               train_steps: int = TRAIN_STEPS, eval_trials: int = EVAL_TRIALS,
               commit: str | None = None) -> dict:
    if not seeds or len(set(seeds)) != len(seeds) or any(type(s) is not int or s < 0 for s in seeds):
        raise ValueError('Seeds must be unique nonnegative integers')
    rows = [row for seed in seeds for row in run_seed(seed, train_steps, eval_trials)]
    record = make_result(
        'brain/sparse-microcircuit-structural-plasticity',
        f'python research/learn_sparse_brain.py --seeds {" ".join(map(str, seeds))} --train-steps {train_steps} --eval-trials {eval_trials}',
        {'seeds': list(seeds), 'initialEdges': [list(edge) for edge in INITIAL_EDGES],
         'learner': vars(PlasticityConfig()), 'growthModes': list(ARMS), 'privilegedTopology': [list(e) for e in PRIVILEGED_EDGES],
         'prespecification': 'confirmatory seeds 101-110; exploratory seeds 0-9 excluded',
         'caveat': 'Synthetic 24-feature association: initial edges deliberately omit informative cue; no human biology claims'},
        {'trainEnvironmentActions': train_steps, 'sourceEvaluationTrials': eval_trials,
         'frozenHeldoutTrials': eval_trials, 'learningRewardCalls': train_steps,
         'maxSynapses': PlasticityConfig().max_edges},
        {'heldoutSuccess': 'higher', 'sourceSuccess': 'higher',
         'trainLateSuccess': 'higher', 'weightedProducts': 'lower',
         'newSynapses': 'lower'},
        rows, baseline='fixed', environment={'device': platform.platform()}, commit=commit)
    problems = validate(record)
    if problems:
        raise ValueError('Result schema invalid: ' + '; '.join(problems))
    return record


def paired_summary(record: dict) -> dict:
    indexed = {(row['seed'], row['arm']): row for row in record['runs'] if row['status'] == 'ok'}
    seeds = record['config']['seeds']
    if len(indexed) != len(seeds) * len(ARMS):
        return {'status': 'incomplete', 'missingRuns': len(seeds) * len(ARMS) - len(indexed)}
    means = {arm: sum(indexed[s, arm]['scores']['heldoutSuccess'] for s in seeds) / len(seeds)
             for arm in ARMS}
    compares = {}
    for arm in ARMS[1:]:
        diff = [indexed[s, 'evidence']['scores']['heldoutSuccess'] - indexed[s, arm]['scores']['heldoutSuccess']
                for s in seeds]
        compares[arm] = {'pairedDelta': sum(diff) / len(diff),
                         'ci95': list(bootstrap_ci(diff, rng=random.Random(112), samples=5000)),
                         'signFlipP': sign_flip(diff)}
    return {'status': 'complete', 'meanHeldoutSuccess': means,
            'pairedEvidenceMinusControls': compares,
            'meanNewSynapses': {arm: sum(indexed[s,arm]['scores']['newSynapses'] for s in seeds) / len(seeds)
                                for arm in ARMS},
            'disclaimer': 'Task is biased against initial fixed topology; not an AGI, anatomy, or true embodied-learning result'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', nargs='+', type=int, default=list(PRECOMMITTED_SEEDS))
    parser.add_argument('--train-steps', type=int, default=TRAIN_STEPS)
    parser.add_argument('--eval-trials', type=int, default=EVAL_TRIALS)
    parser.add_argument('--commit', help='Git SHA of the frozen experiment code')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = experiment(tuple(args.seeds), train_steps=args.train_steps,
                        eval_trials=args.eval_trials, commit=args.commit)
    summary = paired_summary(result)
    print(json.dumps(summary, indent=2))
    if args.out:
        args.out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')