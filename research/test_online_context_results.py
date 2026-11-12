"""Audit lossless committed traces against per-run reward and selector metrics.

This verification runs only once a measured artifact is committed. The
pre-registered selector algorithm and frozen test seeds are not retuned here.
"""
from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

from evaluate_online_context import ARMS, SEEDS
from result_schema import validate

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / 'results' / 'online-context-2026-11-12.json'


class OnlineResultsTests(unittest.TestCase):
    def test_all_frozen_seeds_and_lossless_reward_traces(self):
        record = json.loads(EVIDENCE.read_text(encoding='utf-8'))
        self.assertEqual(validate(record), [])
        self.assertEqual(record['experiment'], 'brain/online-context-stream')
        self.assertEqual(record['config']['seeds'], list(SEEDS))
        self.assertEqual(len(record['runs']), len(SEEDS) * len(ARMS))
        self.assertEqual(record['traceEncoding'].split(':')[0], 'bitstring/1')
        by_seed: dict[int, list] = {}
        for run in record['runs']:
            self.assertEqual(run['status'], 'ok')
            self.assertEqual(run['split'], 'eval')
            self.assertIn(run['arm'], ARMS)
            by_seed.setdefault(run['seed'], []).append(run)
            score = run['scores']
            trace = run['trace']
            selected, actual, noisy = (trace['policySlot'], trace['actualReward'], trace['publicReward'])
            lengths = trace['phaseLengths']
            n = score['actions']
            self.assertEqual(n, sum(lengths))
            self.assertEqual(n, score['rewardCalls'])
            self.assertEqual(score['extraProbeActions'], 0)
            self.assertEqual(len(selected), len(actual))
            self.assertEqual(len(selected), len(noisy))
            self.assertEqual(len(selected), n)
            self.assertLessEqual(sum(ch != '+' for ch in actual), n)
            self.assertLessEqual(sum(ch != '+' for ch in noisy), n)
            self.assertLessEqual(set(selected), set('01'))
            self.assertLessEqual(set(actual), set('+-'))
            self.assertLessEqual(set(noisy), set('+-'))
            self.assertTrue(math.isclose((actual.count('+') - actual.count('-')) / n,
                                         score['rewardPerAction'], abs_tol=1e-12))
            self.assertTrue(math.isclose((noisy.count('+') - noisy.count('-')) / n,
                                         score['observedRewardPerAction'], abs_tol=1e-12))
            flags = ''.join(str(i % 2) * count for i, count in enumerate(lengths))
            self.assertEqual(len(flags), n)
            context_accuracy = sum(slot == context for slot, context in zip(selected, flags)) / n
            self.assertTrue(math.isclose(context_accuracy, score['contextAccuracy'], abs_tol=1e-12))
            self.assertEqual(sum(selected[i] != selected[i-1] for i in range(1, n)), score['switches'])
            start = lengths[0] + lengths[1]
            stop = start + lengths[2]
            accuracy_return = sum(selected[i] == '0' for i in range(start, stop)) / lengths[2]
            self.assertTrue(math.isclose(accuracy_return, score['returnContextAccuracy'], abs_tol=1e-12))
            self.assertEqual(len(trace['switchDelays']), 3)
            self.assertLessEqual(score['switches'], 32 if run['arm'] == 'online_reward' else 1000)
        self.assertEqual(set(by_seed), set(SEEDS))
        for seed, rows in by_seed.items():
            self.assertEqual({r['arm'] for r in rows}, set(ARMS))
            self.assertEqual(len({tuple(r['trace']['phaseLengths']) for r in rows}), 1)
            self.assertEqual(len({r['checkpoint'] for r in rows}), 1)


if __name__ == '__main__':
    unittest.main()