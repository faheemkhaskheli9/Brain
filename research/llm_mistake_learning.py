"""Small, provider-neutral verified-feedback memory for LLM applications.

This changes *inference context*, not the LLM's parameters. The caller supplies
both the model and an independent verifier; model self-criticism is not truth.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Iterable

FORMAT = "brain-mistake-memory/1"
SOURCES = frozenset({"human", "test", "tool"})
MAX_LESSONS = 500
MAX_FIELD = 2000
_TOKEN = re.compile(r"[\w]+", re.UNICODE)


def _terms(text: str) -> set[str]:
    return set(_TOKEN.findall(text.casefold()))


def _valid_text(value: str, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > MAX_FIELD:
        raise ValueError(f"{label} must contain 1-{MAX_FIELD} characters")
    return value.strip()


@dataclass(frozen=True)
class Lesson:
    id: str
    scope: str
    question: str
    wrong_answer: str
    corrected_answer: str
    guidance: str
    source: str


class MistakeMemory:
    """Store only externally checked corrections, isolated by caller-provided scope."""

    def __init__(self, lessons: Iterable[Lesson] = (), capacity: int = MAX_LESSONS):
        if not isinstance(capacity, int) or capacity < 1:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.lessons: list[Lesson] = []
        for lesson in lessons:
            self._append(lesson)

    def _append(self, lesson: Lesson) -> bool:
        if not isinstance(lesson, Lesson):
            raise TypeError("expected Lesson")
        for label in ("scope", "question", "wrong_answer", "corrected_answer", "guidance"):
            _valid_text(getattr(lesson, label), label)
        if lesson.source not in SOURCES:
            raise ValueError("source must be human, test, or tool")
        if lesson.wrong_answer == lesson.corrected_answer:
            raise ValueError("a correction must differ from the wrong answer")
        if any(old.id == lesson.id for old in self.lessons):
            return False
        # Prevent silently learning mutually contradictory labels for the same task.
        if any(old.scope == lesson.scope and old.question.casefold() == lesson.question.casefold()
               and old.corrected_answer != lesson.corrected_answer for old in self.lessons):
            raise ValueError("conflicting correction: explicitly remove or review the old lesson")
        self.lessons.append(lesson)
        if len(self.lessons) > self.capacity:
            self.lessons.pop(0)
        return True

    def record(self, *, scope: str, question: str, wrong_answer: str, corrected_answer: str,
               guidance: str, source: str, verified: bool = False) -> bool:
        """The caller, not the LLM, must attest that correction was verified."""
        if verified is not True:
            raise ValueError("unverified feedback cannot enter learning memory")
        if source not in SOURCES:
            raise ValueError("source must be human, test, or tool")
        fields = {key: _valid_text(value, key) for key, value in {
            "scope": scope, "question": question, "wrong_answer": wrong_answer,
            "corrected_answer": corrected_answer, "guidance": guidance,
        }.items()}
        digest = hashlib.sha256(json.dumps([fields[k] for k in sorted(fields)],
                                          ensure_ascii=False).encode("utf-8")).hexdigest()[:20]
        return self._append(Lesson(id=digest, source=source, **fields))

    def retrieve(self, question: str, *, scope: str, limit: int = 3, min_score: float = 0.22) -> list[Lesson]:
        """Lexical retrieval is an explicit, intentionally simple baseline."""
        _valid_text(question, "question")
        _valid_text(scope, "scope")
        if limit < 0 or not 0 <= min_score <= 1:
            raise ValueError("invalid retrieval settings")
        words = _terms(question)
        ranked = []
        for lesson in self.lessons:
            if lesson.scope != scope:
                continue
            overlap = len(words & _terms(lesson.question))
            union = len(words | _terms(lesson.question))
            score = (overlap / union) if union else 0.0
            if question.casefold() == lesson.question.casefold():
                score = 1.0
            if score >= min_score:
                ranked.append((score, lesson))
        ranked.sort(key=lambda pair: (-pair[0], pair[1].id))
        return [lesson for _, lesson in ranked[:limit]]

    def remove(self, lesson_id: str) -> bool:
        before = len(self.lessons)
        self.lessons = [lesson for lesson in self.lessons if lesson.id != lesson_id]
        return len(self.lessons) < before

    def save(self, path: str | Path) -> None:
        """Atomic snapshot; no raw prompts sent to a service by this module."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        data = {"format": FORMAT, "capacity": self.capacity,
                "lessons": [asdict(lesson) for lesson in self.lessons]}
        tmp = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=target.parent,
                                             prefix=".mistakes-", delete=False) as handle:
                tmp = Path(handle.name)
                os.chmod(tmp, 0o600)
                json.dump(data, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
            os.replace(tmp, target)
        finally:
            if tmp is not None and tmp.exists():
                tmp.unlink()

    @classmethod
    def load(cls, path: str | Path) -> MistakeMemory:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("format") != FORMAT or not isinstance(data.get("lessons"), list):
            raise ValueError("unsupported mistake-memory format")
        return cls([Lesson(**item) for item in data["lessons"]], capacity=data["capacity"])


Model = Callable[[str, list[Lesson]], str]


@dataclass(frozen=True)
class Verification:
    """Verdict from an independent, trusted test/tool/human (not the generator)."""

    passed: bool
    corrected_answer: str | None = None
    guidance: str | None = None
    source: str = "test"


@dataclass(frozen=True)
class SolveResult:
    response: str
    passed: bool
    attempts: int
    recorded_lesson: bool


def answer(question: str, model: Model, memory: MistakeMemory, *, scope: str,
           use_memory: bool = True) -> str:
    """Caller wraps its LLM API; the second argument is *data*, not a system instruction."""
    hints = memory.retrieve(question, scope=scope) if use_memory else []
    return model(question, hints)


def solve_with_feedback(question: str, model: Model,
                        verifier: Callable[[str, str], Verification],
                        memory: MistakeMemory, *, scope: str) -> SolveResult:
    """Try once, learn ONLY from a trusted correction, retry once, verify again.

    The verifier is provided by the application. Do not connect it to the same
    model's ungrounded self-rating; use executable tests, a tool, or a human.
    """
    first = answer(question, model, memory, scope=scope)
    verdict = verifier(question, first)
    if not isinstance(verdict, Verification) or type(verdict.passed) is not bool:
        raise TypeError("verifier must return Verification with a boolean passed")
    if verdict.passed:
        return SolveResult(first, True, 1, False)
    if verdict.corrected_answer is None or verdict.guidance is None:
        return SolveResult(first, False, 1, False)  # no validated target: do not learn
    learned = memory.record(scope=scope, question=question, wrong_answer=first,
                            corrected_answer=verdict.corrected_answer,
                            guidance=verdict.guidance, source=verdict.source, verified=True)
    retry = answer(question, model, memory, scope=scope)
    checked_retry = verifier(question, retry)
    if not isinstance(checked_retry, Verification) or type(checked_retry.passed) is not bool:
        raise TypeError("verifier must return Verification with a boolean passed")
    return SolveResult(retry, checked_retry.passed, 2, learned)


def evaluate_heldout(cases: Iterable[tuple[str, str]], model: Model, memory: MistakeMemory,
                     *, scope: str, use_memory: bool) -> dict[str, int | float]:
    """Frozen exact-match evaluation; reject memorized training questions."""
    seen = {(lesson.scope, lesson.question.casefold()) for lesson in memory.lessons}
    correct = total = 0
    for question, expected in cases:
        if (scope, question.casefold()) in seen:
            raise ValueError("evaluation leakage: a held-out question exists in memory")
        correct += answer(question, model, memory, scope=scope, use_memory=use_memory).strip() == expected.strip()
        total += 1
    return {"correct": correct, "total": total, "accuracy": correct / total if total else 0.0}


def _demo() -> None:
    # Deterministic stand-in: NOT an actual LLM or evidence of LLM accuracy.
    def toy_model(question: str, lessons: list[Lesson]) -> str:
        words = question.partition(":")[2].strip().split()
        use_last = any("choose the last word" in lesson.guidance.lower() for lesson in lessons)
        return words[-1] if use_last else words[0]

    memory = MistakeMemory()
    cases = [("Reply with the last word: cyan orange", "orange"),
             ("Reply with the last word: gold silver", "silver")]
    before = evaluate_heldout(cases, toy_model, memory, scope="demo", use_memory=False)
    memory.record(scope="demo", question="Reply with the last word: green purple",
                  wrong_answer="green", corrected_answer="purple",
                  guidance="Choose the last word, not the first word.", source="test", verified=True)
    after = evaluate_heldout(cases, toy_model, memory, scope="demo", use_memory=True)
    print(json.dumps({"model": "deterministic toy (not an LLM)", "memory_off": before,
                      "memory_on": after}, indent=2))


if __name__ == "__main__":
    _demo()
