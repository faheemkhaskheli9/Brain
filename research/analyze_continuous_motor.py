"""Adversarial audit of frozen continuous-joint/3-step delayed-reward evidence.

Reconstruct joint physics, task schedule, action rewards, public reward noise,
selected contexts and feedback delivery from stored per-action trajectories.
No model weights or training dynamics are inferred from the resulting scores.
"""
from __future__ import annotations

import base64
import hashlib
import json
import math
import random
import struct
from pathlib import Path

from closed_loop_reach import HORIZON, TOLERANCE, reach_trials
from continuous_motor import DelayedRewardSelector
from evaluate_continuous_motor import ARMS
from evaluate_online_context import (BLIND_INTERVAL, DEFAULT_SELECTOR, seeded_phase_steps,
                                     make_phases)
from result_schema import bootstrap_ci, sign_flip, validate

SEEDS = tuple(range(601, 611))
SOURCE_SHA = '4fe342e487eb9da213e2482e158fa3ae8c332be2'
EXPECTED_PHASE_STEPS = (137, 155, 149, 167)


def audit(record: dict) -> dict:
    """Raise ValueError on any invalid/missing run or inconsistent action log."""
    errors = validate(record)
    if errors:
        raise ValueError('Schema failed: ' + '; '.join(errors))
    if record['experiment'] != 'brain/continuous-context-delayed' or record['commit'] != SOURCE_SHA:
        raise ValueError('Unexpected experiment or unregistered source revision')
    cfg, budgets = record['config'], record['budgets']
    if (cfg.get('seeds') != list(SEEDS) or cfg.get('arms') != list(ARMS)
            or cfg.get('phaseStepsBase') != list(EXPECTED_PHASE_STEPS)
            or cfg.get('noise') != 0.1
            or cfg.get('selector') != {
                'window': DEFAULT_SELECTOR.window, 'low_mean': DEFAULT_SELECTOR.low_mean,
                'min_dwell': DEFAULT_SELECTOR.min_dwell,
                'max_switches': DEFAULT_SELECTOR.max_switches}
            or budgets.get('trainPhysicalActionsPerSeed') != 120 * HORIZON
            or budgets.get('reversalAdaptPhysicalActionsPerSeed') != 40 * HORIZON
            or budgets.get('streamActionsPerArm') != sum(EXPECTED_PHASE_STEPS)
            or budgets.get('extraProbeActions') != 0):
        raise ValueError('Confirmatory protocol/configuration mismatch')
    expected = {(seed, arm) for seed in SEEDS for arm in ARMS}
    actual = {(row.get('seed'), row.get('arm')) for row in record['runs']}
    if actual != expected or len(record['runs']) != len(expected):
        raise ValueError('Missing or extra arm/seed rows')
    index = {(row['seed'], row['arm']): row for row in record['runs']}
    for seed in SEEDS:
        digests = {index[seed, arm].get('checkpoint') for arm in ARMS}
        if len(digests) != 1 or next(iter(digests)) is None:
            raise ValueError(f'Mismatched pretrained checkpoint for seed {seed}')
        phase_steps = seeded_phase_steps(seed, EXPECTED_PHASE_STEPS)
        phases = make_phases(seed, phase_steps)
        total = len(phases)
        trials = reach_trials('eval', seed + 175000, (total + HORIZON - 1) // HORIZON)
        target_sha = hashlib.sha256(json.dumps([x.key for x in trials]).encode()).hexdigest()
        noise_rng = random.Random(seed * 50317 + 1907)
        flips = [noise_rng.random() < 0.1 for _ in phases]
        sham = [1 if noise_rng.random() < 0.5 else -1 for _ in phases]
        blind_coin = [noise_rng.randrange(2) for _ in range((total + BLIND_INTERVAL - 1) // BLIND_INTERVAL)]
        for arm in ARMS:
            row = index[seed, arm]
            if row['status'] != 'ok':
                raise ValueError(f'Failed run must remain reported: {seed}/{arm}: {row.get("reason")}')
            score = row['scores']
            trace = row.get('trace', {})
            if (trace.get('phaseLengths') != list(phase_steps)
                    or trace.get('positionsScale') != 10000
                    or trace.get('targetKeysSha256') != target_sha
                    or trace.get('targetValues') != [round(x.target, 8) for x in trials]):
                raise ValueError(f'Altered phase or target schedule: {seed}/{arm}')
            bits = [trace.get(x) for x in ('selected', 'motorActions', 'actualRewardSign', 'publicRewardSign')]
            if any(not isinstance(x, str) or len(x) != total for x in bits):
                raise ValueError(f'Missing action/reward trace: {seed}/{arm}')
            chosen, actions, true_rewards, public_rewards = bits
            if any(ch not in '01' for ch in chosen + actions) or any(ch not in '+-' for ch in true_rewards + public_rewards):
                raise ValueError(f'Illegal encoded action/reward: {seed}/{arm}')
            try:
                raw_positions = base64.b64decode(trace.get('positionsInt16Base64', ''), validate=True)
                if len(raw_positions) != 2 * total:
                    raise ValueError('Wrong physical position trace length')
                positions = struct.unpack(f'<{total}h', raw_positions)
            except (ValueError, TypeError, struct.error) as e:
                raise ValueError('Malformed physical position trace') from e
            online = arm in ('online_immediate', 'online_delay3', 'delay3_shuffled')
            delay = 3 if arm in ('online_delay3', 'delay3_shuffled') else 1
            selector = DelayedRewardSelector(DEFAULT_SELECTOR, delay=delay) if online else None
            pos = vel = 0.0
            hits = 0
            current_hit = False
            regenerated_rewards = []
            correct = []
            for t, inverted in enumerate(phases):
                if t % HORIZON == 0:
                    target = trials[t // HORIZON].target
                    # Initial contact with new target counts; physical state persists.
                    current_hit = abs(target - pos) <= TOLERANCE
                pred_choice = (selector.choose() if selector else
                               (t // BLIND_INTERVAL) % 2 if arm == 'blind_periodic' else
                               blind_coin[t // BLIND_INTERVAL] if arm == 'blind_random' else
                               1 if arm == 'latest' else 0 if arm == 'oldest' else int(inverted))
                if int(chosen[t]) != pred_choice:
                    raise ValueError(f'Non-causal or incorrect selector choice: {seed}/{arm}/{t}')
                correct.append(int(pred_choice == int(inverted)))
                old_err = abs(target - pos)
                direction = -1.0 if actions[t] == '0' else 1.0
                if inverted:
                    direction *= -1
                # Reconstruct the actual SimpleJointBody L hip dynamics; neither
                # this verifier nor the policy can reset position mid-stream.
                vel = max(-1.0, min(1.0, 0.85 * vel + 0.1 * direction))
                pos = max(-1.0, min(1.0, pos + 0.1 * vel))
                if abs(positions[t] - int(round(pos * 10000))) > 0:
                    raise ValueError(f'Body reset/teleportation or false actuator trace: {seed}/{arm}/{t}')
                reward = 1 if abs(target - pos) < old_err - 1e-8 else -1
                if true_rewards[t] != ('+' if reward > 0 else '-'):
                    raise ValueError(f'Claimed reward incompatible with movement: {seed}/{arm}/{t}')
                observed = -reward if flips[t] else reward
                if public_rewards[t] != ('+' if observed > 0 else '-'):
                    raise ValueError(f'Incorrect public reward/noise trace: {seed}/{arm}/{t}')
                if selector:
                    selector.feedback(sham[t] if arm == 'delay3_shuffled' else observed)
                regenerated_rewards.append(reward)
                current_hit |= abs(target - pos) <= TOLERANCE
                if t % HORIZON == HORIZON - 1 or t == total - 1:
                    hits += int(current_hit)
            n_goals = len(trials)
            context = sum(correct) / total
            reward_mean = sum(regenerated_rewards) / total
            hit_rate = hits / n_goals
            return_start = phase_steps[0] + phase_steps[1]
            return_end = return_start + phase_steps[2]
            return_accuracy = sum(correct[return_start:return_end]) / phase_steps[2]
            switches = sum(chosen[i] != chosen[i-1] for i in range(1, total))
            delivery = selector.stats() if selector else None
            observed = delivery.rewards_delivered if delivery else 0
            pending = delivery.pending_rewards if delivery else 0
            expected_scores = {'physicalActions': total, 'generatedRewards': total,
                               'deliveredRewards': observed, 'pendingRewards': pending,
                               'bodyResets': 0, 'targetChanges': len(trials)-1,
                               'extraProbeActions': 0, 'switches': switches,
                               'contextAccuracy': context, 'rewardPerAction': reward_mean,
                               'goalHitRate': hit_rate, 'returnContextAccuracy': return_accuracy}
            for key, actual_value in expected_scores.items():
                claimed = score.get(key)
                if (isinstance(claimed, bool) or not isinstance(claimed, (int, float))
                        or not math.isfinite(claimed) or abs(claimed - actual_value) > 1e-10):
                    raise ValueError(f'Incorrect {key} for {seed}/{arm}: {claimed} vs {actual_value}')
            if trace.get('feedbackLagActions') != (delay if online else None):
                raise ValueError(f'Incorrect feedback lag for {seed}/{arm}')
    def paired(arm: str, comparator: str, metric: str) -> dict:
        delta = [index[s, arm]['scores'][metric] - index[s, comparator]['scores'][metric] for s in SEEDS]
        ci = bootstrap_ci(delta, rng=random.Random(236), samples=5000)
        return {'difference': sum(delta) / len(delta), 'ci95': list(ci), 'signFlipP': sign_flip(delta)}
    primary = paired('online_delay3', 'blind_periodic', 'rewardPerAction')
    negative_feedback = paired('online_delay3', 'delay3_shuffled', 'rewardPerAction')
    target = paired('online_delay3', 'blind_periodic', 'goalHitRate')
    immediate = paired('online_delay3', 'online_immediate', 'rewardPerAction')
    gate = lambda v: v['difference'] >= 0.10 and v['ci95'][0] > 0 and v['signFlipP'] <= 0.05
    return {'complete': True, 'source': record['commit'], 'runs': len(record['runs']),
            'primary': primary, 'passesPrimary': gate(primary),
            'shuffledFeedback': negative_feedback, 'passesShuffled': gate(negative_feedback),
            'goalHitVsPeriodic': target, 'delayCostVsImmediate': immediate}


def main(path: str) -> int:
    record = json.loads(Path(path).read_text(encoding='utf-8'))
    info = audit(record)
    print(json.dumps(info, indent=2))
    # Research gate: do not cause a validation/CI failure for a genuine negative result.
    return 0


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('result_file')
    args = p.parse_args()
    raise SystemExit(main(args.result_file))