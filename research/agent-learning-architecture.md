# Learning agents: skills + RAG + subagents + knowledge + plugins

**Classification:** proposed architecture and runnable integration baseline, **not** proof that an LLM changed its parameters, generalized to unseen tasks or improved real-world accuracy. This is an LLM-agent *interface* experiment, separate from Brain World's backprop-free creature. The working prototype uses deterministic callbacks, not a deployed model or third-party API.

Follow root `AGENTS.md` for repository policy and the Brain World backprop-free constraint.
For a hands-on setup with **Claude Code, ChatGPT/Codex, GitHub Copilot, Cursor, Gemini CLI and OpenCode**, see the [practical agent-learning guide](agent-learning-user-guide.md). It covers skill installation/discovery, reusable prompts, a verifiable error-correction loop, and tests. A checked-in skill is an instruction workflow, not a persistent model update.

## Problem and falsifiable hypothesis

An LLM agent frequently repeats **tool-choice**, **retrieval**, **workflow**, **reasoning**, and **outdated-knowledge** mistakes. A model's reflection alone is not reliable feedback. The hypothesis to test: *on held-out but related tasks, externally verified corrections, when retrieved through a scoped memory and an approved skill, reduce repeated-error rate relative to an otherwise identical agent with memory disabled, at matched call/token budgets.* A stronger hypothesis, not yet tested, is that promoting recurrent verified lessons into reviewed skills/knowledge or applying offline fine-tuning improves transfer while preserving old-task performance.

## End-to-end architecture

```text
User goal -> skill router (approved, versioned procedures)
             -> scoped RAG over cited, versioned knowledge
             -> least-privilege plugin gateway (read-only default)
             -> researcher subagent (suggests evidence; untrusted)
             -> solver/model (uses evidence, skill, episodic lessons)
             -> critic subagent (suggests defects; untrusted)
             -> INDEPENDENT verifier (tests, signed external data, human review)
                   PASS: answer + trace, no automatic model training
                   FAIL: verify proposed correction independently
                        -> if VALID: scoped episodic mistake memory
                        -> optional bounded retry + re-verification
                        -> repeated verified lessons -> skill revision proposal
                        -> cited new fact -> KB correction proposal
                        -> each promotion gated by human/external approval
            Offline/optional: curated, consented dataset -> SFT/DPO/LoRA
                    -> held-out regression gates -> checkpoint release or rollback
```

**Trust ordering:** instructions and tool permissions come from the application; approved skill procedures are configuration; RAG/plugin/subagent content is untrusted input; a verifier is independent from the generator. Even a tool response is not automatically a ground-truth correction. Distinguish *grounded content* from *authorized commands*.

## How each component makes mistakes less repetitive

| Component | Observe a failure | Reuse the correction | Cannot do by itself |
|---|---|---|---|
| **Skills** | Procedure or routing step consistently causes failure. | Draft an evidence-linked `SKILL.md` change after **at least two distinct verified mistakes**; review, test, version and approve before activation. | Automatically install procedures, permissions or binaries from an LLM reflection. |
| **RAG** | Retrieved document is stale, irrelevant, or lacks evidence. | Keep source ID, version, scope; propose document correction and re-index only after source/human verification. | Treat retrieved text as a command or guaranteed truth. |
| **Subagents** | Researcher catches missing source; critic catches contradiction. | Produce review suggestions and evidence *for independent checking*; use role-specialized traces to locate the error. | Self-certify answers or independently promote self-generated corrections. |
| **Knowledge** | Repeated validated rule or fact was absent from shared store. | Convert a verified private episode into a **reviewable** versioned KB proposal; expire/supersede stale facts. | Turn a single unreviewed observation into global policy. |
| **Plugins / tools** | Wrong tool, incorrect schema, stale API, permission error, or unexpected output. | Save tested tool usage pattern in a reviewed skill; add contract tests or a verified example. Allowlist tool and require external write approval. | Grant its own permissions, run irreversible actions without authorization, trust plugin text as instructions. |
| **Episodic memory** | An attempted response fails an independent test. | Store verified failed answer, corrected answer, generalizable guidance, scope; retrieve for later tasks. | Change the model's weights. |
| **SFT / DPO (future)** | Recurrent verified, consented examples show a systematic model weakness. | Train a model adapter/checkpoint offline, replay older tasks, benchmark held-out performance, roll back regressions. | Guarantee a better model without measured evaluation. |

## Implemented in this repository

- [`agent_learning.py`](agent_learning.py) implements a **standard-library** provider-neutral integration wrapper around [`llm_mistake_learning.py`](llm_mistake_learning.py).
- `SkillRegistry`: deterministic scoped routing, a proposed revision from *two distinct stored verified lessons*, review-gated promotion/versioning; no automatic tool-permission growth.
- `KnowledgeIndex`: lexical, scoped citation + version retrieval; a verified-memory-to-KB proposal; review-gated publishing.
- `PluginGateway`: allowlist by skill, read-only tools by default, explicit external authorization callback for writes, bounded call count. Outputs are data, not privileged instructions.
- `run_agent`: optional researcher and critic callbacks, selected skill, cited RAG snippets, plugin observations, and the existing **externally checked** correction/retry flow. The existing verifier checks a correction *again* before it becomes memory.
- [`test_agent_learning.py`](test_agent_learning.py): offline verification, tenant isolation, write approval, spoofed plugin text, review gates, refused unverified corrections, cross-session memory and memory-off baseline.
- [Agent skill example](../.claude/skills/verified-agent-learning/SKILL.md): a procedural guide for agents working **on this repository**. It is a documented skill template, not a capability automatically discovered by the Python module.

**Run from repository root:**

```bash
python research/test_agent_learning.py
python research/test_llm_mistake_learning.py
python research/agent_learning.py  # deterministic toy, not a real LLM benchmark
```

**Integration contract:** applications provide `solver(AgentContext) -> str`, `verifier(question, answer) -> Verification`, optional `researcher` and `critic`, and register externally controlled plugin handlers. Give each tenant/user a separately authenticated `scope`. Use `MistakeMemory.save()/load()` for private episodic persistence; skill/KB registry persistence, encryption, secrets redaction and authentication are **not** implemented. RAG is lexical and doesn't execute arbitrary search, embedding models or network calls. Don't pass personal data or API secrets into this demo.

## Worked scenarios

1. **Coding agent:** an LLM suggests `list.appendleft()`. An executable test rejects it, and verifies `list.append()` works. The experience is stored; a later related task can retrieve the lesson. After multiple *distinct* verified failures, propose a corrected procedure step. The code test, not the critic, determines success.
2. **Documentation RAG:** an API migration makes a retrieved page obsolete. A verified API response plus reviewer produces a **versioned knowledge correction**, so subsequent retrieval uses a newer document. A stale doc should remain available for audit; the prototype only supports explicit replacement, not temporal decay.
3. **Plugin workflow:** an agent asks to create a ticket. A plugin returns `success`, but the application requires authorized write permission and independently checks the resulting ticket. A false-positive plugin message is **not** a license to store a correct-answer label.
4. **Research subagents:** one finds sources, one critiques an experimental claim, and a separate test runner recomputes metrics. Subagent disagreement can trigger verification; consensus alone is not ground truth.

## Pre-registered evaluation protocol for #149 and #156

- **Unit of analysis:** 10+ reproducible seed/partition settings or as many as feasible, and task-family-disjoint train/dev/test splits; keep paraphrases in the same split, prevent retrieval/fine-tune contamination. Record failures and timeouts.
- **Arms:** (A) baseline solver, (B) self-reflection without persistent memory, (C) verified memory retrieval, (D) verified memory + RAG, (E) + approved skills, (F) + researcher/critic, (G) + read-only tools, plus **shuffled memory** and **stale KB** negative controls; optional separate SFT/LoRA arm after privacy review. Use matched retrieval limits, total token and attempt budgets; account for verifier and subagent calls.
- **Metrics:** first-attempt and bounded-retry success, recurrence of the same mistake class, novel-task success, source correctness/precision@k, policy/tool violations, skill routing precision, unauthorized-write attempts blocked, cross-session retention, old-task regressions, latency, token/call cost, bytes stored.
- **Failure criteria:** no reliable held-out gain vs matched controls, worse safety/retention, leakage, unaudited provenance, or any unauthorized tool action. A positive deterministic toy test is a *software test*, not evidence for the hypothesis.
- **Evidence:** write each arm × seed with its failures to `brain-result/1` and update the claims register only if a measured real-model result is actually available.

## Known limitations and hardening backlog

This prototype has no authenticated multi-tenant storage; `scope` is a string supplied by the caller, so a server **must derive scope from its authenticated principal**, never the model. No sandbox for plugin handlers; no embedding/reranking or adversarial semantic-duplicate detection; no provenance signatures, KB TTL, PII redaction, transactional audit log, approval UI, or real LLM adapter. Model-visible documents, notes and plugin payloads are untrusted; the model adapter must quote/delimit them, put them below application instructions and never convert their contents to privileged tool calls. Any write approval callback must be issued by an independent application authorization system, never by the agent itself. Pre-registered trials, not intuition, decide whether the extra components help.

## Primary sources and further reading

- [Lewis et al., Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (NeurIPS 2020)](https://arxiv.org/abs/2005.11401) — combines parametric and retrieved non-parametric memory; doesn't establish that retrieving documents changes weights.
- [Shinn et al., Reflexion: Language Agents with Verbal Reinforcement Learning (NeurIPS 2023)](https://papers.nips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html) — external feedback and episodic verbal memory.
- [Yao et al., ReAct: Synergizing Reasoning and Acting in Language Models (ICLR 2023)](https://openreview.net/forum?id=WE_vluYUL-X) — interleaved actions/observations, not proof of continual parameter learning.
- [Anthropic, Equipping Agents for the Real World with Agent Skills](https://www.anthropic.com/research/equipping-agents-for-the-real-world-with-agent-skills) — packaged `SKILL.md` workflows and progressive disclosure.
- [OpenAI Agents SDK: tools, handoffs and guardrails](https://developers.openai.com/api/docs/guides/agents/sdk) and [agent workflow evaluation](https://developers.openai.com/api/docs/guides/agent-evals) — provider-specific examples of orchestration and tracing, not dependencies of the prototype.
- [Rafailov et al., Direct Preference Optimization (NeurIPS 2023)](https://arxiv.org/abs/2305.18290) — optional future preference fine-tuning from verified chosen/rejected pairs.

Related backlog: [#120](https://github.com/faheemkhaskheli9/Brain/issues/120), [#149](https://github.com/faheemkhaskheli9/Brain/issues/149), [#156](https://github.com/faheemkhaskheli9/Brain/issues/156). See also [`llm-mistake-learning.md`](llm-mistake-learning.md) for strict verifier requirements and the original inference-memory/weight-learning distinction.
