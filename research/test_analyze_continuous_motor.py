"""Defend scientific claims against fabricated feedback, physics and splits."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from analyze_continuous_motor import audit

RESULT = Path(__file__).with_name('results') / 'continuous-motor-2026-11-12.json'


class ContinuousEvidenceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(RESULT.read_text(encoding='utf-8'))

    def test_complete_frozen_evidence_and_preregistered_gates(self):
        x = audit(self.record)
        self.assertEqual(x['runs'], 80)
        self.assertTrue(x['passesPrimary'])
        self.assertTrue(x['passesShuffled'])
        self.assertLess(x['goalHitVsPeriodic']['difference'], 0)

    def test_missing_seed_or_changed_source_rejected(self):
        for mutate in (lambda r: r['runs'].pop(),
                       lambda r: r.update(commit='wrong'),
                       lambda r: r['config']['seeds'].reverse()):
            bad = copy.deepcopy(self.record)
            mutate(bad)
            with self.assertRaises(ValueError):
                audit(bad)

    def test_forged_body_position_and_reversed_action_rejected(self):
        for key in ('positionsInt16Base64', 'motorActions', 'actualRewardSign',
                    'publicRewardSign', 'selected'):
            bad = copy.deepcopy(self.record)
            trace = bad['runs'][0]['trace']
            value = trace[key]
            trace[key] = ('X' if key == 'positionsInt16Base64' else ('0' if value[0] == '1' else '1')) + value[1:]
            with self.subTest(key=key), self.assertRaises(ValueError):
                audit(bad)

    def test_fake_rewards_budgets_and_checkpoints_rejected(self):
        for key, val in [('rewardPerAction', 0.99), ('bodyResets', 1), ('physicalActions', 10),
                         ('goalHitRate', 1), ('deliveredRewards', 1)]:
            bad = copy.deepcopy(self.record)
            bad['runs'][0]['scores'][key] = val
            with self.subTest(key=key), self.assertRaises(ValueError):
                audit(bad)
        bad = copy.deepcopy(self.record)
        bad['runs'][0]['checkpoint'] = 'forged'
        with self.assertRaises(ValueError):
            audit(bad)


if __name__ == '__main__':
    unittest.main()