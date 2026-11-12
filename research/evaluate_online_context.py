"""Boundary-blind evaluation of a sparse checkpoint selector on one lived stream.

Pretraining uses labeled motor regimes (engineered), but at evaluation there
are NO phase/boundary signals, no policy resets and no simulator probes. The
simulator knows the hidden invert flag solely to execute physical actions.
"""

from __future__ import annotations

import argparse
import json
import platform
import random
import time
from dataclasses import asdict
from pathlib import Path

from closed_loop_reach import HORIZON, ReachBody, reach_trials, run_episodes
from context_memory import SparseContextMemory
from learn_reach import policy_for
from online_context import OnlineConfig, OnlineRewardSelector
from result_schema import bootstrap_ci, make_result, sign_flip, validate
from structural_plasticity import SparsePlasticPolicy

ARMS = ('online_reward', 'online_shuffled_feedback', 'blind_periodic', 'blind_random',
        'latest', 'oldest', 'privileged_oracle')
SEEDS = tuple(range(501, 511))
TRAIN_EPISODES = 120
ADAPT_EPISODES = 40
# Phase changes occur in the middle of normal 16-action reaching episodes.
PHASE_STEPS = (137, 155, 149, 167)
NOISE = 0.1
BLIND_INTERVAL = 48  # chosen on exploratory seeds 0-5; ~online switch count
DEFAULT_SELECTOR = OnlineConfig(window=8, low_mean=-0.75, min_dwell=16, max_switches=32)


def train_checkpoints(seed: int, *, train_episodes: int, adapt_episodes: int) -> SparseContextMemory:
    old = policy_for('evidence', seed)
    run_episodes(old, reach_trials('train', seed, train_episodes), learn=True)
    new = SparsePlasticPolicy.from_state(old.export_state())
    run_episodes(new, reach_trials('dev', seed + 50100, adapt_episodes),
                 learn=True, inverted_motor=True)
    memory = SparseContextMemory(capacity=2)
    memory.add(old)
    memory.add(new)
    return memory


def seeded_phase_steps(seed: int, base: tuple[int, ...] = PHASE_STEPS) -> tuple[int, ...]:
    """Fresh deterministic mid-episode transitions, hidden from selectors."""
    if type(seed) is not int or seed < 0 or len(base) != 4 or any(
            type(x) is not int or x < 32 for x in base):
        raise ValueError('Invalid phase-duration parameters')
    rng = random.Random(seed * 39047 + 197)
    lengths = []
    for index, nominal in enumerate(base):
        length = nominal + rng.randint(-8, 8)
        if index < 3 and (sum(lengths) + length) % HORIZON == 0:
            length += 1  # source motor-rule change is never a natural reset
        lengths.append(length)
    return tuple(lengths)


def make_phases(seed: int, phase_steps: tuple[int, ...] = PHASE_STEPS) -> tuple[bool, ...]:
    if type(seed) is not int or seed < 0 or len(phase_steps) < 3 or any(
            type(x) is not int or x < 24 for x in phase_steps):
        raise ValueError('Invalid streaming phase configuration')
    # A-B-A-B stream. Labels here are environment-only and are never passed
    # to the online selector or the reward-only baselines.
    return tuple(bool(index % 2) for index, length in enumerate(phase_steps) for _ in range(length))


def run_stream(memory: SparseContextMemory, arm: str, seed: int, *,
               phase_steps: tuple[int, ...] = PHASE_STEPS,
               noise: float = NOISE, selector_config: OnlineConfig = DEFAULT_SELECTOR) -> dict:
    if (memory.size != 2 or arm not in ARMS or type(seed) is not int or seed < 0
            or isinstance(noise, bool) or not isinstance(noise, (int, float)) or not 0 <= noise <= 0.5
            or not isinstance(selector_config, OnlineConfig)):
        raise ValueError('Invalid streaming evaluation')
    phases = make_phases(seed, phase_steps)
    # Freeze all reward-noise events and target tasks *before* any arm runs.
    rng = random.Random(seed * 50317 + 71)
    reward_flip = tuple(rng.random() < noise for _ in phases)
    blind_coin = tuple(rng.randrange(2) for _ in phases)
    sham_reward = tuple(1.0 if rng.random() < 0.5 else -1.0 for _ in phases)
    tasks = reach_trials('eval', seed + 130000, (len(phases) + HORIZON - 1) // HORIZON)
    checkpoints = (memory.policy(0), memory.policy(1))
    initial_digest = memory.digest()
    initial_fp = tuple(policy.fingerprint() for policy in checkpoints)
    selector = OnlineRewardSelector(selector_config)
    body: ReachBody | None = None
    chosen_indices = []
    actual_rewards, observed_rewards = [], []
    episode_hits = 0
    switch_count = 0
    for t, inverse in enumerate(phases):
        if t % HORIZON == 0:
            if body is not None:
                episode_hits += body.first_hit is not None
            body = ReachBody(tasks[t // HORIZON])
        if arm in ('online_reward', 'online_shuffled_feedback'):
            chosen = selector.select()
        elif arm == 'blind_periodic':
            chosen = (t // BLIND_INTERVAL) % 2
        elif arm == 'blind_random':
            chosen = blind_coin[t // BLIND_INTERVAL * BLIND_INTERVAL]
        elif arm == 'latest':
            chosen = 1
        elif arm == 'oldest':
            chosen = 0
        else:  # separately labeled *privileged* simulator context oracle
            chosen = int(inverse)
        action = checkpoints[chosen].act(body.observe(), explore=False)
        real_reward = body.act(action, inverted_motor=inverse)
        public_reward = -real_reward if reward_flip[t] else real_reward
        if arm in ('online_reward', 'online_shuffled_feedback'):
            selector.feedback(sham_reward[t] if arm == 'online_shuffled_feedback' else public_reward)
        chosen_indices.append(chosen)
        actual_rewards.append(real_reward)
        observed_rewards.append(public_reward)
        if t and chosen != chosen_indices[-2]:
            switch_count += 1
    if body is not None:
        episode_hits += body.first_hit is not None
    if initial_digest != memory.digest() or initial_fp != tuple(p.fingerprint() for p in checkpoints):
        raise RuntimeError('Online inference changed learned checkpoint weights/RNG/memory')
    correctness = [int(chosen_indices[t] == int(phases[t])) for t in range(len(phases))]
    lengths = list(phase_steps)
    bounds = [0]
    for n in lengths:
        bounds.append(bounds[-1] + n)
    # First post-boundary selection of matching pre-trained motor regime.
    # Cap missed switches at the full next phase length.
    latencies = []
    per_phase_accuracy = []
    for phase_i in range(1, len(lengths)):
        start, stop = bounds[phase_i:phase_i+2]
        selected = next((t - start for t in range(start, stop) if correctness[t]), stop - start)
        latencies.append(selected)
    for start, stop in zip(bounds[:-1], bounds[1:]):
        per_phase_accuracy.append(sum(correctness[start:stop]) / (stop - start))
    return {'contextAccuracy': sum(correctness) / len(phases),
            'rewardPerAction': sum(actual_rewards) / len(actual_rewards),
            'observedRewardPerAction': sum(observed_rewards) / len(observed_rewards),
            'goalHitRate': episode_hits / len(tasks),
            'returnContextAccuracy': per_phase_accuracy[2],
            'meanPostSwitchDelay': sum(latencies) / len(latencies),
            'switches': switch_count,
            'actions': len(phases), 'rewardCalls': len(phases),
            'extraProbeActions': 0,
            'memoryBytes': memory.checkpoint_bytes,
            'synapticProducts': sum(p.synaptic_products for p in checkpoints),
            'trace': {'phaseLengths': lengths,
                      'selected': chosen_indices, 'actualReward': actual_rewards,
                      'publicReward': observed_rewards,
                      'switchDelays': latencies}}


def run_seed(seed: int, *, train_episodes: int = TRAIN_EPISODES,
             adapt_episodes: int = ADAPT_EPISODES,
             phase_steps: tuple[int, ...] = PHASE_STEPS,
             noise: float = NOISE,
             selector_config: OnlineConfig = DEFAULT_SELECTOR) -> list[dict]:
    if type(seed) is not int or seed < 0 or any(type(x) is not int or x < 1 for x in (train_episodes, adapt_episodes)):
        raise ValueError('Invalid seed or training budget')
    training_start = time.perf_counter()
    memory = train_checkpoints(seed, train_episodes=train_episodes, adapt_episodes=adapt_episodes)
    train_seconds = time.perf_counter() - training_start
    digest = memory.digest()
    actual_phase_steps = seeded_phase_steps(seed, phase_steps)
    rows = []
    for arm in ARMS:
        begin = time.perf_counter()
        try:
            scores = run_stream(memory, arm, seed, phase_steps=actual_phase_steps,
                                noise=noise, selector_config=selector_config)
            # Report constant training for all arms and trace the same stream.
            trace = scores.pop('trace')
            rows.append({'arm': arm, 'seed': seed, 'split': 'eval', 'status': 'ok',
                         'scores': scores, 'trace': trace,
                         'checkpoint': digest, 'trainingSecondsShared': train_seconds,
                         'seconds': time.perf_counter() - begin})
        except Exception as exc:
            rows.append({'arm': arm, 'seed': seed, 'split': 'eval', 'status': 'error',
                         'reason': f'{type(exc).__name__}: {exc}', 'scores': {},
                         'checkpoint': digest, 'seconds': time.perf_counter() - begin})
    return rows


def experiment(seeds: tuple[int, ...] = SEEDS, *,
               train_episodes: int = TRAIN_EPISODES, adapt_episodes: int = ADAPT_EPISODES,
               phase_steps: tuple[int, ...] = PHASE_STEPS, noise: float = NOISE,
               selector_config: OnlineConfig = DEFAULT_SELECTOR, commit: str | None = None) -> dict:
    if not seeds or any(type(s) is not int or s < 0 for s in seeds) or len(set(seeds)) != len(seeds):
        raise ValueError('Invalid unique seed set')
    runs = [r for s in seeds for r in run_seed(s, train_episodes=train_episodes,
        adapt_episodes=adapt_episodes, phase_steps=phase_steps, noise=noise,
        selector_config=selector_config)]
    rec = make_result('brain/online-context-stream',
        f'python research/evaluate_online_context.py --seeds {" ".join(map(str,seeds))} '
        f'--train-episodes {train_episodes} --adapt-episodes {adapt_episodes} '
        f'--phase-steps {" ".join(map(str,phase_steps))} --noise {noise}',
        {'seeds': list(seeds), 'arms': list(ARMS), 'selector': asdict(selector_config),
         'checkpointSource': 'shared A and B learned separately before scoring',
         'stream': 'alternating A-B-A-B; seed-jittered phase transitions mid-episode not delivered to selector',
         'phaseStepsBase': list(phase_steps), 'phaseStepJitter': 8,
         'rewardCorruptionProbability': noise,
         'blindInterval': BLIND_INTERVAL, 'shamSignal': 'unrelated seeded binary reward stream',
         'observedInputs': '24 engineered visual/S1 channels, chosen policy and previous post-action reward',
         'limitations': 'oracle pretrained B policy, externally designed progress reward, natural episode resets'},
        {'pretrainingActions': train_episodes * HORIZON,
         'reversalTrainingActions': adapt_episodes * HORIZON,
         'streamActions': sum(phase_steps),
         'rewardCalls': sum(phase_steps), 'extraProbeActions': 0,
         'checkpointCount': 2, 'synapsesPerCheckpoint': 4},
        {'contextAccuracy': 'higher', 'rewardPerAction': 'higher',
         'goalHitRate': 'higher', 'returnContextAccuracy': 'higher',
         'meanPostSwitchDelay': 'lower', 'switches': 'lower',
         'extraProbeActions': 'lower'}, runs, baseline='blind_random',
        environment={'runtime': platform.python_version(), 'world': 'SimpleJointBody',
                     'stream': 'single realized trajectory per arm, no candidate resets'}, commit=commit)
    errors = validate(rec)
    if errors:
        raise ValueError('Invalid brain-result/1: ' + '; '.join(errors))
    return rec


def summarize(result: dict) -> dict:
    seeds = result['config']['seeds']
    index = {(r['seed'], r['arm']): r for r in result['runs'] if r['status'] == 'ok'}
    if len(index) != len(seeds) * len(ARMS):
        return {'complete': False, 'ok': len(index), 'expected': len(seeds) * len(ARMS)}
    mean = lambda arm, key: sum(index[seed, arm]['scores'][key] for seed in seeds) / len(seeds)
    delta = [index[seed, 'online_reward']['scores']['rewardPerAction'] -
             index[seed, 'blind_random']['scores']['rewardPerAction'] for seed in seeds]
    return {'complete': True,
            'metrics': {arm: {name: mean(arm, name) for name in ('contextAccuracy',
                       'rewardPerAction', 'goalHitRate', 'returnContextAccuracy',
                       'meanPostSwitchDelay', 'switches')} for arm in ARMS},
            'primary': {'difference': sum(delta) / len(delta),
                        'ci95': list(bootstrap_ci(delta, rng=random.Random(136), samples=5000))
                        if len(delta) > 1 else None, 'pairedP': sign_flip(delta)}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', type=int, nargs='+', default=list(SEEDS))
    parser.add_argument('--train-episodes', type=int, default=TRAIN_EPISODES)
    parser.add_argument('--adapt-episodes', type=int, default=ADAPT_EPISODES)
    parser.add_argument('--phase-steps', type=int, nargs='+', default=list(PHASE_STEPS))
    parser.add_argument('--noise', type=float, default=NOISE)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--commit')
    args = parser.parse_args()
    data = experiment(tuple(args.seeds), train_episodes=args.train_episodes,
                      adapt_episodes=args.adapt_episodes, phase_steps=tuple(args.phase_steps),
                      noise=args.noise, commit=args.commit)
    print(json.dumps(summarize(data), indent=2))
    if args.out:
        args.out.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')