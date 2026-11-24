"""Mutation tests on a tiny real run (not a Brain performance result)."""
import copy
import json
import os
import subprocess
import tempfile
import unittest

from analyze_m0c_own_step_transfer import summarize, validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fixture():
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "smoke.json")
        subprocess.run(["node", "game/world/own_step_transfer_protocol.mjs", "--budget", "15",
                        "--wide-budget", "15", "--repeats", "1", "--dev-seeds", "101",
                        "--etas", "0.004,0.064", "--wide-etas", "0.004,0.008",
                        "--out", out, "1", "2"],
                       cwd=ROOT, check=True, capture_output=True)
        with open(out, encoding="utf-8") as stream:
            return json.load(stream)


def first(record, split, prefix):
    return next(x for x in record["runs"] if x["split"] == split and x["arm"].startswith(prefix))


class ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = fixture()

    def mutated(self):
        return copy.deepcopy(self.record)

    def test_valid_and_five_tests(self):
        report = summarize(self.record)
        self.assertEqual(len(report["tests"]), 5)
        self.assertEqual(report["wide"]["goalBlindCeiling"]["heldout"], 1 / 5)

    def test_rejects_tampered_own_eta(self):
        r = self.mutated()
        own = r["config"]["own"]
        other = next(e for e in own["etaGrid"] if e != own["ownEta"]["no-hidden"])
        own["ownEta"]["no-hidden"] = other
        with self.assertRaises(ValueError):
            validate(r)

    def test_rejects_eval_at_other_arms_step(self):
        r = self.mutated()
        row = first(r, "own-eval", "no-hidden@")
        eta = r["config"]["own"]["ownEta"]["no-hidden"]
        other = next(e for e in r["config"]["own"]["etaGrid"] if e != eta)
        row["arm"] = f"no-hidden@eta{other}"
        with self.assertRaises(ValueError):
            validate(r)

    def test_rejects_tampered_wide_eta(self):
        r = self.mutated()
        w = r["config"]["wide"]
        w["selected"] = next(e for e in w["etaGrid"] if e != w["selected"])
        with self.assertRaises(ValueError):
            validate(r)

    def test_rejects_heldout_leak_into_wide_train(self):
        r = self.mutated()
        r["config"]["wideGoals"]["train"][0] = r["config"]["wideGoals"]["heldout"][0]
        with self.assertRaises(ValueError):
            validate(r)

    def test_rejects_non_interior_heldout(self):
        r = self.mutated()
        g = r["config"]["wideGoals"]
        g["train"][0], g["heldout"][0] = g["heldout"][0], g["train"][0]
        with self.assertRaises(ValueError):
            validate(r)

    def test_rejects_wide_goal_blind_breach(self):
        r = self.mutated()
        first(r, "wide-eval", "mask-goal@")["scores"]["after"]["heldout"]["maxGoalsPerRepeat"] = 2
        with self.assertRaises(ValueError):
            validate(r)

    def test_rejects_unmatched_step(self):
        r = self.mutated()
        first(r, "wide-eval", "flag-only@")["scores"]["training"]["meanActorStep"] *= 2
        with self.assertRaises(ValueError):
            validate(r)

    def test_rejects_missing_eval_row(self):
        r = self.mutated()
        r["runs"] = [x for x in r["runs"]
                     if not (x["split"] == "wide-eval" and x["arm"].startswith("flag-only@"))]
        with self.assertRaises(ValueError):
            validate(r)

    def test_rejects_dev_eval_overlap_and_oracle(self):
        r = self.mutated()
        r["config"]["devSeeds"] = [1]
        with self.assertRaises(ValueError):
            validate(r)
        r = self.mutated()
        first(r, "own-eval", "native@")["scores"]["onlineOracleQueries"] = 1
        with self.assertRaises(ValueError):
            validate(r)

    def test_error_rows_score_zero_not_dropped(self):
        r = self.mutated()
        row = first(r, "wide-eval", "native@")
        row["status"], row["scores"] = "error", {}
        arm = summarize(r)["wide"]["arms"]["native"]
        self.assertEqual(arm["errors"], 1)
        self.assertEqual(len(arm["perSeedHeldout"]), 2)

    def test_grid_edge_is_inconclusive(self):
        r = self.mutated()
        top = max(r["config"]["own"]["etaGrid"])
        if r["config"]["own"]["ownEta"]["no-hidden"] == top:
            self.assertEqual(summarize(r)["falsifier"]["hiddenLayerAtOwnStep"],
                             "inconclusive (grid edge)")
        t = next(x for x in summarize(r)["tests"] if x["contrast"] == "hidden-layer")
        self.assertIn("gridEdge", t)


if __name__ == "__main__":
    unittest.main()
