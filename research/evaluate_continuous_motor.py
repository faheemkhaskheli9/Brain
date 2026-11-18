"""Persistent-body, delayed-reward motor context benchmark (backprop-free).

Pretraining of two sparse policies still uses labelled motor regimes. During
scoring, the controller sees only public 24-channel sensory observations and
past, possibly delayed action rewards. The body and its velocities persist
across all target and hidden actuator-rule changes. Privileged labels are
ONLY read by the environment and verifier, not the learned selector.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import platform
import random
import struct
import time
from dataclasses import asdict
from pathlib import Path

from closed_loop_reach import HORIZON, reach_trials
from continuous_motor import ContinuousReachBody, DelayedRewardSelector
from evaluate_online_context import (BLIND_INTERVAL, DEFAULT_SELECTOR, NOISE,
                                     seeded_phase_steps, make_phases, train_checkpoints)
from online_context import OnlineConfig
from result_schema import bootstrap_ci, make_result, sign_flip, validate
from context_memory import SparseContextMemory

ARMS = ('online_immediate', 'online_delay3', 'delay3_shuffled', 'blind_periodic',
        'blind_random', 'latest', 'oldest', 'privileged_oracle')
SEEDS = tuple(range(601, 611))
TRAIN_EPISODES = 120
ADAPT_EPISODES = 40
PHASE_STEPS = (137, 155, 149, 167)


def run_stream(memory: SparseContextMemory, arm: str, seed: int, *,
               phase_steps: tuple[int, ...] = PHASE_STEPS,
               noise: float = NOISE, selector_config: OnlineConfig = DEFAULT_SELECTOR) -> dict:
    if (not isinstance(memory, SparseContextMemory) or memory.size != 2
            or arm not in ARMS or type(seed) is not int or seed < 0
            or isinstance(noise, bool) or not isinstance(noise, (int, float))
            or not math.isfinite(noise) or not 0 <= noise <= 0.5
            or not isinstance(selector_config, OnlineConfig)):
        raise ValueError('Invalid continuous-body context experiment')
    phases = make_phases(seed, phase_steps)
    total = len(phases)
    # Arm-independent visual targets and independent, pre-generated noise.
    trials = reach_trials('eval', seed + 175000, (total + HORIZON - 1) // HORIZON)
    rand = random.Random(seed * 50317 + 1907)
    flips = tuple(rand.random() < noise for _ in range(total))
    sham = tuple(1.0 if rand.random() < 0.5 else -1.0 for _ in range(total))
    blind_coin = tuple(rand.randrange(2) for _ in range((total + BLIND_INTERVAL - 1) // BLIND_INTERVAL))
    policies = (memory.policy(0), memory.policy(1))
    frozen_digest = memory.digest()
    frozen_fps = tuple(p.fingerprint() for p in policies)
    delay = 3 if arm in ('online_delay3', 'delay3_shuffled') else 1
    selector = DelayedRewardSelector(selector_config, delay=delay)
    body = ContinuousReachBody(trials[0])
    physical_body_id = id(body.loop.body)
    selected, actions, true_reward, public_reward, positions = [], [], [], [], []
    goal_hits = 0
    switch_count = 0
    for t, inverted in enumerate(phases):
        if t and t % HORIZON == 0:
            goal_hits += body.set_target(trials[t // HORIZON])
            if id(body.loop.body) != physical_body_id:
                raise RuntimeError('Body reset during continuous task')
        if arm in ('online_immediate', 'online_delay3', 'delay3_shuffled'):
            chosen = selector.choose()
        elif arm == 'blind_periodic':
            chosen = (t // BLIND_INTERVAL) % 2
        elif arm == 'blind_random':
            chosen = blind_coin[t // BLIND_INTERVAL]
        elif arm == 'latest':
            chosen = 1
        elif arm == 'oldest':
            chosen = 0
        else:
            chosen = int(inverted)  # verifier-only privileged oracle.
        action = policies[chosen].act(body.observe(), explore=False)
        reward = body.act(action, inverted_motor=inverted)
        observed = -reward if flips[t] else reward
        if arm in ('online_immediate', 'online_delay3', 'delay3_shuffled'):
            selector.feedback(sham[t] if arm == 'delay3_shuffled' else observed)
        selected.append(chosen)
        actions.append(action)
        true_reward.append(reward)
        public_reward.append(observed)
        positions.append(int(round(body.loop.body.positions['L_hip'] * 10000)))
        if t and selected[-1] != selected[-2]:
            switch_count += 1
    goal_hits += body.first_hit is not None
    if body.physical_steps != total or body.targets_seen != len(trials) or id(body.loop.body) != physical_body_id:
        raise RuntimeError('Violation of continuous body state invariant')
    if memory.digest() != frozen_digest or tuple(p.fingerprint() for p in policies) != frozen_fps:
        raise RuntimeError('Frozen evaluation altered checkpoint weights or RNG')
    correct = [int(selected[t] == int(phases[t])) for t in range(total)]
    bounds = [0]
    for phase_len in phase_steps:
        bounds.append(bounds[-1] + phase_len)
    phase_accuracy = [sum(correct[a:b]) / (b - a) for a, b in zip(bounds[:-1], bounds[1:])]
    latencies = [next((t - a for t in range(a, b) if correct[t]), b - a)
                 for a, b in zip(bounds[1:-1], bounds[2:])]
    delivery = selector.stats() if arm in ('online_immediate', 'online_delay3', 'delay3_shuffled') else None
    return {
        'rewardPerAction': sum(true_reward) / total,
        'contextAccuracy': sum(correct) / total,
        'goalHitRate': goal_hits / len(trials),
        'returnContextAccuracy': phase_accuracy[2],
        'meanPostSwitchDelay': sum(latencies) / len(latencies),
        'switches': switch_count, 'extraProbeActions': 0,
        'physicalActions': total, 'generatedRewards': total,
        'deliveredRewards': delivery.rewards_delivered if delivery else 0,
        'pendingRewards': delivery.pending_rewards if delivery else 0,
        'bodyResets': 0, 'targetChanges': len(trials) - 1,
        'checkpointBytes': memory.checkpoint_bytes,
        'synapticProducts': sum(p.synaptic_products for p in policies),
        'trace': {
            'phaseLengths': list(phase_steps),
            'selected': ''.join(map(str, selected)),
            'motorActions': ''.join(map(str, actions)),
            'actualRewardSign': ''.join('+' if x > 0 else '-' for x in true_reward),
            'publicRewardSign': ''.join('+' if x > 0 else '-' for x in public_reward),
            'positionsScale': 10000,
            'positionsInt16Base64': base64.b64encode(struct.pack(f'<{len(positions)}h', *positions)).decode('ascii'),
            'targetKeysSha256': hashlib.sha256(json.dumps([x.key for x in trials]).encode()).hexdigest(),
            'targetValues': [round(x.target, 8) for x in trials],
            'postSwitchDelays': latencies,
            'feedbackLagActions': delay if delivery else None,
        }
    }


def run_seed(seed: int, *, train_episodes: int = TRAIN_EPISODES,
             adapt_episodes: int = ADAPT_EPISODES,
             phase_steps: tuple[int, ...] = PHASE_STEPS, noise: float = NOISE,
             selector_config: OnlineConfig = DEFAULT_SELECTOR) -> list[dict]:
    if (type(seed) is not int or seed < 0
            or any(type(x) is not int or not 1 <= x <= 10000 for x in (train_episodes, adapt_episodes))):
        raise ValueError('Invalid seed / training budget')
    start = time.perf_counter()
    memory = train_checkpoints(seed, train_episodes=train_episodes, adapt_episodes=adapt_episodes)
    training_s = time.perf_counter() - start
    before = memory.digest()
    schedule = seeded_phase_steps(seed, phase_steps)
    rows = []
    for arm in ARMS:
        ts = time.perf_counter()
        try:
            stats = run_stream(memory, arm, seed, phase_steps=schedule, noise=noise,
                               selector_config=selector_config)
            trace = stats.pop('trace')
            rows.append({'arm': arm, 'seed': seed, 'split': 'eval', 'status': 'ok',
                         'scores': stats, 'trace': trace, 'checkpoint': before,
                         'trainingSecondsShared': training_s,
                         'seconds': time.perf_counter() - ts})
        except Exception as e:
            rows.append({'arm': arm, 'seed': seed, 'split': 'eval', 'status': 'error',
                         'scores': {}, 'checkpoint': before, 'seconds': time.perf_counter() - ts,
                         'reason': f'{type(e).__name__}: {e}'})
    if memory.digest() != before:
        raise RuntimeError('Policy memory changed during frozen stream')
    return rows


def experiment(seeds: tuple[int, ...] = SEEDS, *, train_episodes: int = TRAIN_EPISODES,
               adapt_episodes: int = ADAPT_EPISODES, phase_steps: tuple[int, ...] = PHASE_STEPS,
               noise: float = NOISE, selector_config: OnlineConfig = DEFAULT_SELECTOR,
               commit: str | None = None) -> dict:
    if not seeds or any(type(s) is not int or s < 0 for s in seeds) or len(set(seeds)) != len(seeds):
        raise ValueError('Invalid unique seed set')
    if len(phase_steps) != 4 or any(type(x) is not int or x < 32 for x in phase_steps):
        raise ValueError('Four valid phase lengths required')
    all_runs = [r for s in seeds for r in run_seed(s, train_episodes=train_episodes,
        adapt_episodes=adapt_episodes, phase_steps=phase_steps, noise=noise,
        selector_config=selector_config)]
    record = make_result('brain/continuous-context-delayed',
        f'python research/evaluate_continuous_motor.py --seeds {" ".join(map(str, seeds))} '
        f'--train-episodes {train_episodes} --adapt-episodes {adapt_episodes} '
        f'--phase-steps {" ".join(map(str, phase_steps))} --noise {noise}',
        {'seeds': list(seeds), 'arms': list(ARMS), 'selector': asdict(selector_config),
         'phaseStepsBase': list(phase_steps), 'phaseStepJitter': 8,
         'trainCheckpoint': 'both policies independently learned with labelled regimes before scoring',
         'stream': 'persistent motor body; target changes every 16 actions without resetting positions or velocities',
         'rewardLatency': 'immediate means available BEFORE next choice (1 action), delayed means 3 actions',
         'noise': noise, 'blindInterval': BLIND_INTERVAL,
         'limitations': 'engineered target-error observations and reward, only two known motor regimes, toy single joint'},
        {'trainPhysicalActionsPerSeed': train_episodes * HORIZON,
         'reversalAdaptPhysicalActionsPerSeed': adapt_episodes * HORIZON,
         'streamActionsPerArm': sum(phase_steps), 'extraProbeActions': 0,
         'maxMemoryContexts': 2, 'synapsesPerContext': 4,
         'rewardDeliveredByLastAction': 'actions - delay; remaining outcomes reported as pending, no hidden future delivery'},
        {'rewardPerAction': 'higher', 'contextAccuracy': 'higher',
         'goalHitRate': 'higher', 'returnContextAccuracy': 'higher',
         'meanPostSwitchDelay': 'lower', 'switches': 'lower',
         'extraProbeActions': 'lower', 'bodyResets': 'lower'},
        all_runs, baseline='blind_periodic',
        environment={'runtime': platform.python_version(), 'world': 'SimpleJointBody; persistent positions/velocities'},
        commit=commit)
    problems = validate(record)
    if problems:
        raise ValueError('Result schema errors: ' + '; '.join(problems))
    return record


def summarize(record: dict) -> dict:
    seeds = record['config']['seeds']
    idx = {(r['seed'], r['arm']): r for r in record['runs'] if r['status'] == 'ok'}
    if len(idx) != len(seeds) * len(ARMS):
        return {'complete': False, 'ok': len(idx), 'started': len(seeds) * len(ARMS)}
    avg = lambda arm, key: sum(idx[seed, arm]['scores'][key] for seed in seeds) / len(seeds)
    paired = [idx[seed, 'online_delay3']['scores']['rewardPerAction'] -
              idx[seed, 'blind_periodic']['scores']['rewardPerAction'] for seed in seeds]
    shuffled = [idx[seed, 'online_delay3']['scores']['rewardPerAction'] -
                idx[seed, 'delay3_shuffled']['scores']['rewardPerAction'] for seed in seeds]
    return {'complete': True,
            'arms': {arm: {key: avg(arm, key) for key in ('rewardPerAction', 'contextAccuracy',
                     'goalHitRate', 'returnContextAccuracy', 'switches')} for arm in ARMS},
            'primary': {'difference': sum(paired) / len(paired),
                        'ci95': bootstrap_ci(paired, rng=random.Random(236), samples=5000),
                        'signFlipP': sign_flip(paired)},
            'versusShuffled': {'difference': sum(shuffled) / len(shuffled),
                              'ci95': bootstrap_ci(shuffled, rng=random.Random(236), samples=5000),
                              'signFlipP': sign_flip(shuffled)}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', type=int, nargs='+', default=list(SEEDS))
    parser.add_argument('--train-episodes', type=int, default=TRAIN_EPISODES)
    parser.add_argument('--adapt-episodes', type=int, default=ADAPT_EPISODES)
    parser.add_argument('--phase-steps', type=int, nargs='+', default=list(PHASE_STEPS))
    parser.add_argument('--noise', type=float, default=NOISE)
    parser.add_argument('--commit')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    data = experiment(tuple(args.seeds), train_episodes=args.train_episodes,
                      adapt_episodes=args.adapt_episodes, phase_steps=tuple(args.phase_steps),
                      noise=args.noise, commit=args.commit)
    print(json.dumps(summarize(data), indent=2))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')