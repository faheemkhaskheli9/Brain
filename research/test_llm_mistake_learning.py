"""Regression tests for verified correction memory and leakage boundaries."""

import json
import tempfile
import unittest
from pathlib import Path

from llm_mistake_learning import MistakeMemory, Verification, answer, evaluate_heldout, solve_with_feedback


class MistakeLearningTests(unittest.TestCase):
    def setUp(self):
        self.memory = MistakeMemory(capacity=2)
        self.input = dict(scope="coding", question="Python list add item", wrong_answer="use appendleft",
                          corrected_answer="use append", guidance="Use list.append for Python lists",
                          source="test", verified=True)

    def test_verification_required(self):
        for invalid in (False, None, 1, "yes"):
            with self.assertRaises(ValueError):
                self.memory.record(**{**self.input, "verified": invalid})
        self.assertEqual(self.memory.lessons, [])
        with self.assertRaises(ValueError):
            self.memory.record(**{**self.input, "source": "self_critique"})

    def test_dedupe_conflict_and_delete(self):
        self.assertTrue(self.memory.record(**self.input))
        self.assertFalse(self.memory.record(**self.input))
        with self.assertRaisesRegex(ValueError, "conflicting"):
            self.memory.record(**{**self.input, "corrected_answer": "use extend"})
        self.assertTrue(self.memory.remove(self.memory.lessons[0].id))
        self.assertTrue(self.memory.record(**{**self.input, "corrected_answer": "use extend"}))

    def test_scope_ranking_and_eviction(self):
        self.memory.record(**self.input)
        self.assertEqual(len(self.memory.retrieve("Python list add item", scope="coding")), 1)
        self.assertEqual(self.memory.retrieve("Python list add item", scope="different"), [])
        self.assertEqual(self.memory.retrieve("marine biology", scope="coding"), [])
        self.memory.record(**{**self.input, "question": "Python tuple indexing"})
        self.memory.record(**{**self.input, "question": "Python set insert"})
        self.assertEqual(len(self.memory.lessons), 2)
        self.assertEqual(self.memory.retrieve("Python list add item", scope="coding", min_score=1), [])

    def test_roundtrip_and_bad_schema(self):
        self.memory.record(**self.input)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memory.json"
            self.memory.save(path)
            loaded = MistakeMemory.load(path)
            self.assertEqual(loaded.lessons, self.memory.lessons)
            self.assertEqual(loaded.capacity, 2)
            path.write_text(json.dumps({"format": "brain-mistake-memory/0", "lessons": []}))
            with self.assertRaises(ValueError):
                MistakeMemory.load(path)

    def test_retrieval_changes_outcome_without_weight_update(self):
        def model(prompt, lessons):
            return "corrected" if lessons else "wrong"

        query = "Python list add item example"
        self.assertEqual(answer(query, model, self.memory, scope="coding"), "wrong")
        self.memory.record(**self.input)
        self.assertEqual(answer(query, model, self.memory, scope="coding"), "corrected")
        self.assertEqual(answer(query, model, self.memory, scope="coding", use_memory=False), "wrong")

    def test_frozen_holdout_and_leakage(self):
        def model(question, lessons):
            return "right" if lessons else "wrong"

        cases = [("Python list add item example", "right")]
        self.memory.record(**self.input)
        self.assertEqual(evaluate_heldout(cases, model, self.memory, scope="coding", use_memory=False)["accuracy"], 0)
        self.assertEqual(evaluate_heldout(cases, model, self.memory, scope="coding", use_memory=True)["accuracy"], 1)
        self.assertEqual(len(self.memory.lessons), 1)  # scoring did not train
        with self.assertRaisesRegex(ValueError, "leakage"):
            evaluate_heldout([("Python list add item", "right")], model, self.memory,
                             scope="coding", use_memory=True)

    def test_trusted_verifier_loop_and_recheck(self):
        def model(question, lessons):
            return "fixed" if lessons else "broken"

        def verifier(question, response):
            if response == "fixed":
                return Verification(passed=True)
            return Verification(passed=False, corrected_answer="fixed", guidance="Repair the response", source="test")

        result = solve_with_feedback("Python list add item", model, verifier, self.memory, scope="coding")
        self.assertTrue(result.passed)
        self.assertEqual(result.attempts, 2)
        self.assertTrue(result.recorded_lesson)
        self.assertEqual(len(self.memory.lessons), 1)

    def test_no_learning_when_correction_unavailable(self):
        result = solve_with_feedback("fail", lambda question, lessons: "wrong",
                                     lambda question, response: Verification(passed=False),
                                     self.memory, scope="coding")
        self.assertFalse(result.passed)
        self.assertEqual(result.attempts, 1)
        self.assertEqual(len(self.memory.lessons), 0)

    def test_invalid_fields(self):
        for key, value in (("guidance", ""), ("question", "x" * 2001),
                           ("corrected_answer", self.input["wrong_answer"])):
            with self.assertRaises(ValueError):
                self.memory.record(**{**self.input, key: value})
        with self.assertRaises(ValueError):
            self.memory.retrieve("Python list", scope="coding", limit=-1)


if __name__ == "__main__":
    unittest.main()
