"""Provider-neutral, *inference-time* orchestration around verified mistake memory.

This is not a model trainer. A model/researcher/critic can propose corrections,
but only the external verifier used by solve_with_feedback may admit a lesson.
Never use model-supplied tool approvals or make RAG/plugin text instructions.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable

from llm_mistake_learning import Lesson, MistakeMemory, SolveResult, Verification, _terms, _valid_text, solve_with_feedback


@dataclass(frozen=True)
class KnowledgeDocument:
    id: str
    scope: str
    content: str
    source: str
    version: str


@dataclass(frozen=True)
class Skill:
    name: str
    scope: str
    description: str
    procedure: tuple[str, ...]
    allowed_tools: tuple[str, ...] = ()
    version: int = 1


@dataclass(frozen=True)
class SkillRevision:
    name: str
    scope: str
    proposed_steps: tuple[str, ...]
    lesson_ids: tuple[str, ...]


@dataclass(frozen=True)
class ToolRequest:
    name: str
    payload: str


@dataclass(frozen=True)
class ToolObservation:
    tool: str
    content: str
    source: str


@dataclass(frozen=True)
class AgentContext:
    question: str
    skill: Skill | None
    documents: tuple[KnowledgeDocument, ...]
    lessons: tuple[Lesson, ...]
    observations: tuple[ToolObservation, ...]
    researcher_note: str = ""
    critic_note: str = ""


@dataclass(frozen=True)
class AgentRun:
    result: SolveResult
    skill: str | None
    citations: tuple[str, ...]
    tools_used: tuple[str, ...]
    research_calls: int
    critique_calls: int


def _score(query: str, reference: str) -> float:
    q, r = _terms(query), _terms(reference)
    return len(q & r) / len(q | r) if q and r else 0.0


class KnowledgeIndex:
    """Cited RAG documents, not learned labels. Tenant-scoped lexical baseline."""

    def __init__(self, documents: tuple[KnowledgeDocument, ...] = ()):
        self._docs: dict[tuple[str, str], KnowledgeDocument] = {}
        for item in documents:
            self._store(item)

    def _store(self, item: KnowledgeDocument) -> None:
        if not isinstance(item, KnowledgeDocument):
            raise TypeError("expected KnowledgeDocument")
        for field in ("id", "scope", "content", "source", "version"):
            _valid_text(getattr(item, field), field)
        self._docs[(item.scope, item.id)] = item

    def search(self, question: str, *, scope: str, limit: int = 3) -> tuple[KnowledgeDocument, ...]:
        _valid_text(question, "question")
        _valid_text(scope, "scope")
        if limit < 0:
            raise ValueError("limit cannot be negative")
        scored = [(_score(question, item.content), item) for item in self._docs.values() if item.scope == scope]
        scored = [(score, item) for score, item in scored if score > 0]
        scored.sort(key=lambda row: (-row[0], row[1].id))
        return tuple(item for _, item in scored[:limit])

    @staticmethod
    def propose_from_lesson(lesson_id: str, memory: MistakeMemory) -> KnowledgeDocument:
        """Draft a KB entry from verified experience; still requires independent review."""
        lesson = next((item for item in memory.lessons if item.id == lesson_id), None)
        if lesson is None:
            raise ValueError("only recorded, verified lessons can be proposed")
        return KnowledgeDocument("correction-" + lesson.id, lesson.scope, lesson.guidance,
                                 "verified-feedback:" + lesson.source, "proposal-1")

    def publish(self, item: KnowledgeDocument, *, approve: Callable[[KnowledgeDocument], bool]) -> bool:
        """External human/evidence approval, not a model-generated 'verified' flag."""
        if approve(item) is not True:
            return False
        self._store(item)
        return True


class SkillRegistry:
    """Only approved skills execute; verified mistakes yield *proposals*, not self-edits."""

    def __init__(self, skills: tuple[Skill, ...]):
        self._skills: dict[tuple[str, str], Skill] = {}
        for skill in skills:
            self._validate(skill)
            self._skills[(skill.scope, skill.name)] = skill

    @staticmethod
    def _validate(skill: Skill) -> None:
        if not isinstance(skill, Skill) or skill.version < 1:
            raise ValueError("invalid skill")
        for field in ("name", "scope", "description"):
            _valid_text(getattr(skill, field), field)
        for step in skill.procedure:
            _valid_text(step, "step")
        for tool in skill.allowed_tools:
            _valid_text(tool, "tool")

    def select(self, question: str, scope: str) -> Skill | None:
        candidates = [(score, skill) for skill in self._skills.values() if skill.scope == scope
                      if (score := _score(question, skill.description)) > 0]
        return sorted(candidates, key=lambda row: (-row[0], row[1].name))[0][1] if candidates else None

    def get(self, name: str, scope: str) -> Skill:
        return self._skills[(scope, name)]

    def propose_revision(self, name: str, scope: str, memory: MistakeMemory,
                         *, min_distinct_examples: int = 2) -> SkillRevision | None:
        """No self-promotion. Use evidence from >=2 different independently verified tasks."""
        skill = self.get(name, scope)
        matched = [lesson for lesson in memory.lessons if lesson.scope == scope
                   and _score(lesson.question, skill.description) > 0]
        seen: set[str] = set()
        distinct: list[Lesson] = []
        for lesson in matched:
            if lesson.question.casefold() not in seen:
                seen.add(lesson.question.casefold())
                distinct.append(lesson)
        if len(distinct) < max(min_distinct_examples, 2):
            return None
        return SkillRevision(name, scope, tuple(lesson.guidance for lesson in distinct),
                             tuple(lesson.id for lesson in distinct))

    def apply_revision(self, proposal: SkillRevision, *, memory: MistakeMemory,
                       approve: Callable[[SkillRevision], bool]) -> bool:
        """Call with a trusted review service; the LLM cannot supply its own approval."""
        skill = self.get(proposal.name, proposal.scope)
        if not proposal.lesson_ids or len(set(proposal.lesson_ids)) < 2:
            raise ValueError("skill revision needs >=2 distinct verified lessons")
        lessons_by_id = {lesson.id: lesson for lesson in memory.lessons}
        evidence = [lessons_by_id.get(lesson_id) for lesson_id in proposal.lesson_ids]
        if (any(lesson is None or lesson.scope != proposal.scope for lesson in evidence)
                or len({lesson.question.casefold() for lesson in evidence}) < 2
                or tuple(lesson.guidance for lesson in evidence) != proposal.proposed_steps):
            raise ValueError("proposed steps must match distinct verified lessons")
        if approve(proposal) is not True:
            return False
        steps = tuple(dict.fromkeys((*skill.procedure, *proposal.proposed_steps)))
        updated = replace(skill, procedure=steps, version=skill.version + 1)
        self._validate(updated)
        self._skills[(updated.scope, updated.name)] = updated
        return True


@dataclass(frozen=True)
class _Tool:
    handler: Callable[[str], str]
    source: str
    read_only: bool


class PluginGateway:
    """Allowlisted gateway; write actions require trusted out-of-band approval."""

    def __init__(self):
        self._tools: dict[str, _Tool] = {}

    def register(self, name: str, handler: Callable[[str], str], *, source: str, read_only: bool = True) -> None:
        _valid_text(name, "name")
        _valid_text(source, "source")
        if name in self._tools:
            raise ValueError("duplicate tool")
        self._tools[name] = _Tool(handler, source, read_only)

    def execute(self, request: ToolRequest, *, skill: Skill | None,
                approve_write: Callable[[ToolRequest], bool] | None = None) -> ToolObservation:
        if skill is None or request.name not in skill.allowed_tools:
            raise PermissionError("tool is not allowlisted for this approved skill")
        _valid_text(request.payload, "payload")
        tool = self._tools[request.name]
        if not tool.read_only and (approve_write is None or approve_write(request) is not True):
            raise PermissionError("write tool requires external authorization")
        content = tool.handler(request.payload)
        _valid_text(content, "tool output")
        return ToolObservation(request.name, content, tool.source)


Solver = Callable[[AgentContext], str]
Researcher = Callable[[AgentContext], str]
Critic = Callable[[AgentContext, str], str]


def run_agent(question: str, *, scope: str, memory: MistakeMemory, knowledge: KnowledgeIndex,
              skills: SkillRegistry, gateway: PluginGateway, solver: Solver,
              verifier: Callable[[str, str], Verification],
              tool_requests: tuple[ToolRequest, ...] = (),
              researcher: Researcher | None = None, critic: Critic | None = None,
              approve_write: Callable[[ToolRequest], bool] | None = None,
              use_memory: bool = True) -> AgentRun:
    """Bounded orchestration: RAG + skill + gated tool, then verified-learning loop.

    Researcher/critic/LLM/plugin responses are untrusted suggestions, not judges.
    Existing `solve_with_feedback` independently checks the proposed correction
    before adding it and caps retries at one.
    """
    _valid_text(question, "question")
    _valid_text(scope, "scope")
    if len(tool_requests) > 3:
        raise ValueError("tool budget is 3 calls per run")
    skill = skills.select(question, scope)
    documents = knowledge.search(question, scope=scope)
    observations = tuple(gateway.execute(req, skill=skill, approve_write=approve_write)
                         for req in tool_requests)
    research_calls = critique_calls = 0
    last_critique = ""

    def invoke(q: str, lessons: list[Lesson]) -> str:
        nonlocal research_calls, critique_calls, last_critique
        context = AgentContext(q, skill, documents, tuple(lessons) if use_memory else (),
                               observations, critic_note=last_critique)
        if researcher is not None:
            research_note = researcher(context)
            if research_note:
                _valid_text(research_note, "researcher_note")
            research_calls += 1
            context = replace(context, researcher_note=research_note)
        response = solver(context)
        _valid_text(response, "solver output")
        if critic is not None:
            last_critique = critic(context, response)
            if last_critique:
                _valid_text(last_critique, "critic_note")
            critique_calls += 1
        return response

    # Optional memory-off arm must not *learn*, even from a successful verifier.
    if use_memory:
        result = solve_with_feedback(question, invoke, verifier, memory, scope=scope)
    else:
        response = invoke(question, [])
        verdict = verifier(question, response)
        if not isinstance(verdict, Verification) or type(verdict.passed) is not bool:
            raise TypeError("verifier must return Verification")
        result = SolveResult(response, verdict.passed, 1, False)
    return AgentRun(result, skill.name if skill else None,
                    tuple(f"{doc.id}@{doc.version}" for doc in documents),
                    tuple(obs.tool for obs in observations), research_calls, critique_calls)


def _demo() -> None:
    """Deterministic integration smoke example, not an LLM benchmark."""
    skills = SkillRegistry((Skill("python-help", "demo", "Python list append", ("Check the API",),
                                  ("docs",)),))
    knowledge = KnowledgeIndex((KnowledgeDocument("kb-1", "demo", "Python list append adds one item",
                                                  "manual", "1"),))
    gateway = PluginGateway()
    gateway.register("docs", lambda query: "list.append(value) is the supported method", source="API docs")
    memory = MistakeMemory()

    def solver(ctx: AgentContext) -> str:
        return "append" if ctx.lessons else "appendleft"

    def verifier(question: str, output: str) -> Verification:
        return Verification(output == "append", "append" if output != "append" else None,
                            "For Python list addition use append", "test")

    out = run_agent("Python list append item", scope="demo", memory=memory, knowledge=knowledge,
                    skills=skills, gateway=gateway, solver=solver, verifier=verifier,
                    tool_requests=(ToolRequest("docs", "Python list append"),))
    print({"demo": "deterministic, not LLM", "passed": out.result.passed,
           "attempts": out.result.attempts, "stored_lessons": len(memory.lessons),
           "skill": out.skill, "citations": out.citations, "tools": out.tools_used})


if __name__ == "__main__":
    _demo()
