"""Frozen outcome-based sparse context retrieval versus matched retention controls.

The hidden motor inversion only configures the simulated environment. Policies
and the checkpoint selector see public senses, actions and post-action reward.
Two context checkpoints are intentionally trained after an explicit change
boundary; autonomous change-point detection is NOT implemented.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import time
from dataclasses import asdict
from pathlib import Path

from closed_loop_reach import HORIZON, ReachBody, reach_trials, run_episodes
from context_memory import SparseContextMemory
from learn_reach import policy_for
from result_schema import bootstrap_ci, make_result, sign_flip, validate
from structural_plasticity import SparsePlasticPolicy

ARMS = ('single', 'bank_latest', 'bank_random', 'bank_probe', 'bank_oracle')
SEEDS = tuple(range(401, 411))
TRAIN_EPISODES = 120
ADAPT_EPISODES = 40
EVAL_EPISODES = 80
PROBE_TRIALS = 6
PROBE_STEPS = 3


class InvertedReachBody(ReachBody):
    """Environment-only motor inversion; neither memory nor policy reads it."""

    def act(self, action: int, *, inverted_motor: bool = False) -> float:
        return super().act(action, inverted_motor=True)


def _checkpoint_sha(checkpoint: dict) -> str:
    return hashlib.sha256(json.dumps(checkpoint, sort_keys=True).encode()).hexdigest()


def run_seed(seed: int, *, train_episodes: int = TRAIN_EPISODES,
             adapt_episodes: int = ADAPT_EPISODES, eval_episodes: int = EVAL_EPISODES,
             probe_trials: int = PROBE_TRIALS, probe_steps: int = PROBE_STEPS) -> list[dict]:
    if (type(seed) is not int or seed < 0 or any(type(v) is not int or not 1 <= v <= 10000
        for v in (train_episodes, adapt_episodes, eval_episodes, probe_trials, probe_steps))
        or probe_trials > 32 or probe_steps > 8):
        raise ValueError('Invalid context retrieval experiment configuration')
    started = time.perf_counter()
    # All arms use IDENTICAL pretrained and reversal-adapted checkpoints.
    prior = policy_for('evidence', seed)
    run_episodes(prior, reach_trials('train', seed, train_episodes), learn=True)
    prior_state = prior.export_state()
    changed = SparsePlasticPolicy.from_state(prior_state)
    run_episodes(changed, reach_trials('dev', seed + 50100, adapt_episodes),
                 learn=True, inverted_motor=True)
    new_state = changed.export_state()
    training_seconds = time.perf_counter() - started
    training_synaptic_products = prior.synaptic_products + changed.synaptic_products
    training_candidate_products = prior.candidate_products + changed.candidate_products
    memory = SparseContextMemory(capacity=2)
    memory.add(prior)
    memory.add(changed)
    if memory.policy(0).fingerprint() != prior.fingerprint():
        raise RuntimeError('Stored old policy changed during adaptation')
    prior_hash = _checkpoint_sha(prior_state)
    new_hash = _checkpoint_sha(new_state)
    before_digest = memory.digest()
    source_eval = reach_trials('train', seed + 90000, eval_episodes)
    reverse_eval = reach_trials('eval', seed + 120000, eval_episodes)
    reverse_probe = reach_trials('dev', seed + 80100, probe_trials)
    return_probe = reach_trials('dev', seed + 80200, probe_trials)
    assert {t.key for t in reverse_probe}.isdisjoint(t.key for t in return_probe)
    assert {t.key for t in source_eval}.isdisjoint(t.key for t in reverse_probe)
    assert {t.key for t in reverse_eval}.isdisjoint(t.key for t in return_probe)
    source_before = run_episodes(memory.policy(0), source_eval)
    reversed_baseline = run_episodes(memory.policy(1), reverse_eval, inverted_motor=True)
    rng = random.Random(seed * 16737 + 19)
    rows = []
    for arm in ARMS:
        begin = time.perf_counter()
        try:
            if arm == 'single':
                # Smaller memory, smaller interaction budget; baseline showing
                # what happens if the original policy is overwritten in place.
                reverse_idx = return_idx = 1
                probe_actions = 0
                reverse_scores = return_scores = None
                memory_bytes = len(json.dumps(new_state, separators=(',', ':')))
            else:
                # Run exact same reward probes for all bank arms, including
                # selectors that ignore probe evidence. No evaluation leakage.
                rev = memory.retrieve(reverse_probe, InvertedReachBody, steps=probe_steps)
                ret = memory.retrieve(return_probe, ReachBody, steps=probe_steps)
                probe_actions = rev.probe_actions + ret.probe_actions
                reverse_scores, return_scores = rev.scores, ret.scores
                memory_bytes = memory.checkpoint_bytes
                if arm == 'bank_probe':
                    reverse_idx, return_idx = rev.index, ret.index
                elif arm == 'bank_random':
                    reverse_idx = rng.randrange(2)
                    return_idx = rng.randrange(2)
                elif arm == 'bank_latest':
                    reverse_idx = return_idx = 1
                else:  # privileged context-label upper bound
                    reverse_idx, return_idx = 1, 0
            reversal = run_episodes(memory.policy(reverse_idx), reverse_eval, inverted_motor=True)
            returned = run_episodes(memory.policy(return_idx), source_eval)
            if memory.digest() != before_digest or prior.fingerprint() != memory.policy(0).fingerprint():
                raise RuntimeError('Frozen scoring or retrieval mutated learned memories')
            scores = {'reversedSuccess': reversal.success,
                      'returnSuccess': returned.success,
                      'sourceBefore': source_before.success,
                      'reversedTrainedReference': reversed_baseline.success,
                      'retentionDelta': returned.success - source_before.success,
                      'correctReverseSelection': float(reverse_idx == 1),
                      'correctReturnSelection': float(return_idx == 0),
                      'probeActions': probe_actions, 'probeRewardCalls': probe_actions,
                      'memoryBytes': memory_bytes,
                      'storedModels': 1 if arm == 'single' else memory.size,
                      'firstHitStep': returned.mean_time_to_hit,
                      'returnFinalError': returned.final_error,
                      'trainingSynapticProducts': training_synaptic_products,
                      'trainingCandidateProducts': training_candidate_products}
            rows.append({'arm': arm, 'seed': seed, 'split': 'eval', 'status': 'ok',
                         'seconds': time.perf_counter() - begin, 'scores': scores,
                         'checkpoint': new_hash,
                         'sourceCheckpoint': prior_hash,
                         'selected': [reverse_idx, return_idx],
                         'probeScores': {'reverse': reverse_scores, 'return': return_scores}})
        except Exception as exc:
            rows.append({'arm': arm, 'seed': seed, 'split': 'eval', 'status': 'error',
                         'reason': f'{type(exc).__name__}: {exc}', 'scores': {},
                         'checkpoint': new_hash, 'seconds': time.perf_counter() - begin})
    if memory.digest() != before_digest:
        raise RuntimeError('Global context memory was modified')
    for row in rows:
        row['trainingSecondsShared'] = training_seconds
    return rows


def experiment(seeds: tuple[int, ...] = SEEDS, *, train_episodes: int = TRAIN_EPISODES,
               adapt_episodes: int = ADAPT_EPISODES, eval_episodes: int = EVAL_EPISODES,
               probe_trials: int = PROBE_TRIALS, probe_steps: int = PROBE_STEPS,
               commit: str | None = None) -> dict:
    if not seeds or len(set(seeds)) != len(seeds) or any(type(s) is not int or s < 0 for s in seeds):
        raise ValueError('Invalid seeds')
    rows = [row for seed in seeds for row in run_seed(seed, train_episodes=train_episodes,
            adapt_episodes=adapt_episodes, eval_episodes=eval_episodes,
            probe_trials=probe_trials, probe_steps=probe_steps)]
    record = make_result('brain/context-checkpoint-retrieval',
        f'python research/evaluate_context_memory.py --seeds {" ".join(map(str, seeds))} '
        f'--train-episodes {train_episodes} --adapt-episodes {adapt_episodes} '
        f'--eval-episodes {eval_episodes} --probe-trials {probe_trials} --probe-steps {probe_steps}',
        {'seeds': list(seeds), 'arms': list(ARMS),
         'policyConfig': asdict(policy_for('evidence', seeds[0]).cfg),
         'selector': 'detached checkpoint candidates scored with DEV motor progress rewards; no hidden motor sign',
         'contextTiming': 'training and adaptation regime boundaries supplied by experimenter; not autonomously detected',
         'policyTraining': 'one shared base and changed-motor checkpoint per seed for all arms',
         'evaluation': 'held-out source/reversed tasks, independent of probe tasks',
         'limitations': 'engineered target delta, two trained contexts, extra probes/restarts, no neuronal memory simulation'},
        {'trainBodyActionsPerArm': train_episodes * HORIZON,
         'adaptBodyActionsPerArm': adapt_episodes * HORIZON,
         'frozenReverseActionsPerArm': eval_episodes * HORIZON,
         'frozenReturnActionsPerArm': eval_episodes * HORIZON,
         'probeActionsPerBankArm': 2 * 2 * probe_trials * probe_steps,
         'probeActionsSingleArm': 0,
         'maxSavedContexts': 2, 'synapsesPerContext': 4},
        {'returnSuccess': 'higher', 'reversedSuccess': 'higher',
         'retentionDelta': 'higher', 'probeActions': 'lower', 'memoryBytes': 'lower'},
        rows, baseline='bank_latest', environment={'runtime': platform.python_version(),
                                                   'world': 'SimpleJointBody'}, commit=commit)
    errors = validate(record)
    if errors:
        raise ValueError('Invalid brain-result/1: ' + '; '.join(errors))
    return record


def summarize(record: dict) -> dict:
    seeds, arms = record['config']['seeds'], record['config']['arms']
    index = {(row['seed'], row['arm']): row for row in record['runs'] if row['status'] == 'ok'}
    if len(index) != len(seeds) * len(arms):
        return {'complete': False, 'ok': len(index), 'total': len(seeds) * len(arms)}
    mean = lambda arm, key: sum(index[s, arm]['scores'][key] for s in seeds) / len(seeds)
    paired = [index[s, 'bank_probe']['scores']['returnSuccess'] -
              index[s, 'bank_latest']['scores']['returnSuccess'] for s in seeds]
    return {'complete': True,
            'arms': {a: {k: mean(a, k) for k in ('returnSuccess', 'reversedSuccess', 'retentionDelta',
                                                 'probeActions', 'memoryBytes')} for a in arms},
            'probeVsLatest': {'difference': sum(paired) / len(paired),
                              'ci95': list(bootstrap_ci(paired, rng=random.Random(136), samples=5000))
                              if len(seeds) > 1 else None,
                              'exactSignFlipP': sign_flip(paired)}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', type=int, nargs='+', default=list(SEEDS))
    parser.add_argument('--train-episodes', type=int, default=TRAIN_EPISODES)
    parser.add_argument('--adapt-episodes', type=int, default=ADAPT_EPISODES)
    parser.add_argument('--eval-episodes', type=int, default=EVAL_EPISODES)
    parser.add_argument('--probe-trials', type=int, default=PROBE_TRIALS)
    parser.add_argument('--probe-steps', type=int, default=PROBE_STEPS)
    parser.add_argument('--commit')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    data = experiment(tuple(args.seeds), train_episodes=args.train_episodes,
                      adapt_episodes=args.adapt_episodes,
                      eval_episodes=args.eval_episodes,
                      probe_trials=args.probe_trials, probe_steps=args.probe_steps, commit=args.commit)
    print(json.dumps(summarize(data), indent=2))
    if args.out:
        args.out.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')