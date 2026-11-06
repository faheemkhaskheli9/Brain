"""Mutation tests for continual-learning result integrity; no long training in CI."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from continual_guard import MANIFEST, ROOT, check_checkpoint, check_files, check_record


class ContinualGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.specs = json.loads(MANIFEST.read_text(encoding="utf-8"))["fixtures"]
        cls.records = {spec["kind"]: json.loads((ROOT / spec["path"]).read_text(encoding="utf-8"))
                       for spec in cls.specs}
        cls.by_kind = {spec["kind"]: spec for spec in cls.specs}

    def test_pinned_fixtures(self):
        self.assertEqual(check_files(), [])

    def test_missing_failed_seed_is_detected(self):
        record = copy.deepcopy(self.records["heldout"])
        record["runs"] = [r for r in record["runs"] if r["seed"] != 5]
        self.assertTrue(any("coverage" in x for x in check_record(record, self.by_kind["heldout"])))

    def test_failed_seed_cannot_be_laundered_as_success(self):
        record = copy.deepcopy(self.records["heldout"])
        next(r for r in record["runs"] if r["seed"] == 5)["status"] = "ok"
        self.assertTrue(check_record(record, self.by_kind["heldout"]))

    def test_split_leakage_and_forgetting_mutations(self):
        record = copy.deepcopy(self.records["heldout"])
        record["config"]["splits"]["layout"]["eval"] = [1]
        self.assertTrue(any("layout" in x for x in check_record(record, self.by_kind["heldout"])))
        record = copy.deepcopy(self.records["heldout"])
        next(r for r in record["runs"] if r["status"] == "ok" and r["arm"] == "pretrained")["scores"]["tone"]["forgetting"] += 0.2
        self.assertTrue(any("forgetting" in x for x in check_record(record, self.by_kind["heldout"])))

    def test_reversal_retention_mutation(self):
        record = copy.deepcopy(self.records["reversal"])
        record["runs"][0]["scores"]["retention"] = 0.99
        self.assertTrue(any("retention" in x for x in check_record(record, self.by_kind["reversal"])))

    def test_incorrect_schema(self):
        record = copy.deepcopy(self.records["reversal"])
        record["schema"] = "brain-result/0"
        self.assertTrue(any("schema" in x for x in check_record(record, self.by_kind["reversal"])))

    def test_corrupted_checkpoint_and_path_traversal(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            model = root / "model.json"
            model.write_text('{"ok":true}', encoding="utf-8")
            import hashlib
            digest = hashlib.sha256(model.read_bytes()).hexdigest()
            ref = {"checkpoint": {"path": "model.json", "sha256": digest}}
            self.assertEqual(check_checkpoint(ref, root), [])
            model.write_text('{"ok":false}', encoding="utf-8")
            self.assertTrue(any("mismatch" in e for e in check_checkpoint(ref, root)))
            ref["checkpoint"]["path"] = "../model.json"
            self.assertTrue(any("inside repository" in e for e in check_checkpoint(ref, root)))


if __name__ == "__main__":
    unittest.main()
