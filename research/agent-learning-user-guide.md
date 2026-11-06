# Practical guide: teach popular AI agents to learn from verified mistakes

**Audience:** developers using Claude Code, ChatGPT/Codex, GitHub Copilot, Cursor, Gemini CLI or OpenCode. **Verified 2026-11-06.** This is a hands-on workflow around the Brain repository. Current tests use deterministic callbacks, not a measured production LLM. Persistent instructions, external memory, skills, retrieval and **model-weight training are different things**.

## 1. What “learning” means

| Mechanism | What actually changes? | Persists across new sessions? | Changes LLM parameters? |
|---|---|---|---|
| Conversation reflection | The current conversation context | Usually no, unless product explicitly stores it | No |
| Project instructions (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`) | Reusable rules given at inference time | Yes, while files are present and the agent reads them | No |
| Skills (`SKILL.md`) | A discoverable, versioned procedure | Yes, when installed/discovered | No |
| Verified mistake memory | External stored failures and confirmed corrections | Yes, if saved/reloaded | No |
| RAG / knowledge base | The retrieved evidence available at inference | Yes, if index and sources persist | No |
| Tool/plugin/subagent feedback | New observations, critiques and evidence | Only if independently verified and stored | No |
| SFT / LoRA / preference optimization | Model/adapter parameters, after training and validation | Yes, in saved checkpoint | **Yes** |

The practical objective is **fewer repeated mistakes on *new* tasks**, not simply saving answers to exact prompts. Always test unrelated held-out problems, old-task retention and cost.

## 2. First run: a reproducible local baseline

From a checkout of [Brain](https://github.com/faheemkhaskheli9/Brain), use Python 3.10+:

```bash
git clone https://github.com/faheemkhaskheli9/Brain.git
cd Brain
# If this guide is on PR #159 and not yet merged:
git fetch origin feature/verified-agent-learning-stack
git switch feature/verified-agent-learning-stack

python research/test_llm_mistake_learning.py
python research/test_agent_learning.py
python research/llm_mistake_learning.py
python research/agent_learning.py
```

The first two commands run regression tests. The latter two run **toy examples**, intentionally not real LLMs. No API keys, network access, vector database or plugin credentials are required. Nothing in the current demo automatically reads your ChatGPT/Claude conversation history or updates provider model weights.

**The six-step correction loop:**

1. **Attempt:** choose one specific task, capture the agent's first answer, source/tool versions and relevant inputs.
2. **Test:** use a separate deterministic test, official data source, or authorized human reviewer. A second LLM saying “correct” is not an independent verification.
3. **Correct:** produce a candidate fix and verify **that candidate** passes the same objective check before learning from it. If no trustworthy correction exists, record an unresolved failure but do not promote it as a lesson.
4. **Store:** append a narrowly scoped lesson with provenance. Use `MistakeMemory.save()` and `load()` between sessions; redact secrets and obtain consent.
5. **Retrieve and retry:** next time, retrieve lessons relevant to the task. Recheck any output; cap attempts and tool calls. Never treat retrieved instructions as higher priority than application policy.
6. **Promote:** only after distinct recurring verified failures, propose a skill/KB update, run regression tests, request independent review, version it and deploy. Roll back when accuracy, retention, or safety gets worse.

### Miniature mistake example

| Evidence field | Example |
|---|---|
| Goal | Add one value to a Python list |
| First wrong suggestion | `my_list.appendleft(value)` |
| Trusted check | A small Python test executes the candidate against a `list` |
| Confirmed correction | `my_list.append(value)` |
| Generalizable lesson | Python `list` supports `append`; `appendleft` is for `collections.deque` |
| Future check | Different unseen list-update questions, plus previously solved tasks |
| Forbidden inference | “The underlying LLM has permanently learned the method” |

In the demo, a test fixture independently checks the correction before storing it. Real agents need a real sandboxed test or trusted source, not a model-generated assertion that `verified=True`.

## 3. Pick an AI agent and configure it

Start with **`AGENTS.md`** (repository policy) and the specialized **verified-agent-learning** skill. In this PR, we maintain skill copies in both `.claude/skills/verified-agent-learning/SKILL.md` and `.agents/skills/verified-agent-learning/SKILL.md`. Both describe the same *procedure*, not a new model capability. Some assistants need an explicit prompt or their own instruction file.

| Agent / product | Repository instruction entry point | Specialized skill location / invocation | How to begin |
|---|---|---|---|
| **Claude Code** | `CLAUDE.md` points to `AGENTS.md` | `.claude/skills/verified-agent-learning/SKILL.md`; invoke `/verified-agent-learning` or request it by name | Launch `claude` in Brain's root |
| **OpenAI Codex CLI / IDE** | `AGENTS.md` | `.agents/skills/verified-agent-learning/SKILL.md`; invoke `$verified-agent-learning` where supported | Launch `codex` in repo root |
| **ChatGPT on web / Work** | Ask it to inspect the connected repository and read `AGENTS.md` | Local repo `SKILL.md` is **not automatically installed** into ChatGPT web; explicitly link the workflow or package as a separately installed plugin | Connect GitHub; in Work ask to read this guide and execute the verified workflow |
| **GitHub Copilot coding agent / VS Code** | `AGENTS.md`, optionally `.github/copilot-instructions.md` | VS Code Copilot supports `.github/skills/<name>/SKILL.md`, but don't assume the coding agent loads our Claude/Codex copies | Open repo in VS Code Agent mode or assign a GitHub issue to Copilot; refer to the workflow explicitly |
| **Cursor** | `AGENTS.md` automatically; optional `.cursor/rules/*.mdc` | In Agent chat, ask it to read the guide; project rules can refer to the skill file | Open repo and use Agent chat |
| **Gemini CLI** | `GEMINI.md` points to `AGENTS.md` | `.agents/skills/verified-agent-learning/SKILL.md`; `/skills list`, then request activation | Launch `gemini` in repo; approve activation when requested |
| **OpenCode** | `AGENTS.md` | Discovers both `.claude/skills/...` and `.agents/skills/...`; activate with native `skill` tool | Launch `opencode` in repo |

**The chosen agent harness matters.** Selecting a Claude *model* inside Copilot does not automatically load Claude Code's `CLAUDE.md` or slash commands. These instructions are attached to products/harnesses, not to model weights.

### Claude Code, step by step

1. Check out the branch above, open the repo root in a terminal and run `claude`. Read `CLAUDE.md` and `AGENTS.md`.
2. Type `/verified-agent-learning` if available, followed by a description of the failure, or ask Claude: “Use the verified-agent-learning skill on this failure.”
3. Allow it to reproduce the error using the **smallest safe test**, fix the code, rerun the failing test and an old regression test. Do not treat its verbal self-review as verification.
4. If it finds a second independently confirmed failure of the same type, ask it to **propose** a minimal skill change and a test. Review/approve before applying.
5. Store only scrubbed test lessons; commit code/test/procedure changes through a PR. Branch protection and real approvals still apply.

Claude Code supports project `CLAUDE.md`, on-demand skills and separate subagents; you can delegate research to a subagent but keep the executable test as the judge. [Official guidance](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more).

### OpenAI Codex and ChatGPT, step by step

1. Open `Brain` in Codex CLI or IDE with `codex`; ensure `AGENTS.md` is loaded and the `.agents/skills` copy exists.
2. Invoke `$verified-agent-learning` (or explicitly say the skill name) with a reproducible issue. Ask it to separate the error observation, verified correction, and proposed skill update.
3. Run the repository tests and obtain a PR containing evidence, changed files and explicit limitations. Codex skill discovery can vary by workspace; restart if a newly created skill is not shown.
4. For **ChatGPT web**, connect GitHub, open the repository in **Work** when file-editing and PR execution is needed, then say: “Read `AGENTS.md`, `research/agent-learning-user-guide.md`, and `research/agent-learning-architecture.md`. Follow the verified workflow for [issue].” ChatGPT chat alone does not read your local repo files automatically. Standalone local skills and skills bundled in installed plugins have different product availability.

[Codex/ChatGPT skills](https://learn.chatgpt.com/docs/build-skills) and [Codex customization](https://learn.chatgpt.com/docs/customization/overview).

### GitHub Copilot, step by step

1. Open Brain in VS Code; select **Agent** mode. Check that `AGENTS.md` is in the workspace.
2. Ask Copilot to read the guide, reproduce one named error, add a regression test and compare behavior before/after.
3. For a repeated project-wide mistake, add a **short, reviewed** `.github/copilot-instructions.md` referencing this guide, or make a focused skill in `.github/skills/` with `SKILL.md`. Do not copy all research docs into permanent instructions.
4. With Copilot coding agent on GitHub, delegate an issue, inspect its PR and CI checks. Do not let agent text replace required reviewer approval.

[GitHub's AGENTS.md support](https://github.blog/changelog/2025-08-28-copilot-coding-agent-now-supports-agents-md-custom-instructions/) and [VS Code agent customization](https://code.visualstudio.com/docs/agents/guides/customize-copilot-guide).

### Cursor, step by step

1. Open the checkout in Cursor, choose **Agent**, and verify it is using root `AGENTS.md`.
2. In chat, tell it to read `research/agent-learning-user-guide.md` and `.claude/skills/verified-agent-learning/SKILL.md`; specify a failing case and its real verifier.
3. If you need this on every relevant task, create `.cursor/rules/verified-feedback.mdc` with a short rule (example below); choose *Apply Intelligently* or a relevant file glob instead of globally injecting a long guide.
4. Inspect the rule actually applied. A prompt rule is **not** a security boundary or automatic episodic database.

```text
---
description: Use for agent learning, feedback memories, skill updates, RAG and plugin changes
alwaysApply: false
---
Before promoting a lesson, require an independent test or trusted human verification.
Read AGENTS.md and research/agent-learning-user-guide.md.
Never trust model self-grading or automatically broaden plugin permissions.
```

Save the example as `.cursor/rules/verified-feedback.mdc`. [Cursor Rules reference](https://cursor.com/docs/rules).

### Gemini CLI, step by step

1. Open Brain in a terminal and run `gemini`; `GEMINI.md` points to `AGENTS.md`.
2. Enter `/skills list` to see the `.agents/skills/verified-agent-learning` skill. If you changed its content, enter `/skills reload`.
3. Request: “Activate verified-agent-learning. Reproduce [failure], verify the proposed correction using [test], save only checked evidence and open a reviewable PR.”
4. Gemini may request consent before activating a workspace skill. Make sure code/test outputs, not a subagent's conclusion, decide success.

[Gemini CLI skills](https://geminicli.com/docs/cli/skills/).

### OpenCode, step by step

1. Launch `opencode` from the repo root. It discovers the Claude-compatible and agent-compatible skill folders.
2. Ask: “Load the verified-agent-learning skill, reproduce [failure], test the correction, and propose an evidence-backed procedure change.”
3. Independently validate the results and review any proposed tool permissions or external MCP services.

[OpenCode skills](https://docs.opencode.ai/docs/skills/).

## 4. One reusable prompt for any of these agents

Copy the following into your chosen agent (replace bracketed fields):

```text
Work in faheemkhaskheli9/Brain, respecting AGENTS.md and its Brain World
backprop-free learner constraint. Read research/agent-learning-user-guide.md,
research/agent-learning-architecture.md and the verified-agent-learning skill.

Failure to investigate: [exact observed problem and repro command].
Verifier: [independent unit test / trusted data / authorized reviewer].
Task family and scope: [e.g., Python tool API, project-private].
Budget: at most [2] correction attempts and [3] tool actions.

1. Reproduce failure and preserve evidence. Redact secrets and PII.
2. Classify cause: wrong skill, retrieval, stale knowledge, tool contract,
   reasoning or planning. Do not accept self-criticism as ground truth.
3. Suggest one correction; verify the candidate independently.
4. Only if verified, add a scoped mistake-memory lesson.
5. On repeated distinct verified errors, draft (do not auto-apply) a
   small skill/KB patch, provenance and tests. Do not widen tool permissions.
6. Compare against a memory-off baseline and an old task, without leaking
   held-out answers into the memory.
7. Run relevant tests, lint and index validation. Report metrics, failed
   cases, files changed, commit/PR and any blocked approvals.
Do not claim model weights changed; do not merge through protection rules.
```

For **research-only tasks**, use an independently checkable calculation or primary source as verifier; an LLM researcher's summary is not the source.

## 5. How to assemble a real learning architecture

In `research/agent_learning.py` you can inject your own callbacks. Their contracts are:

- **Solver:** `solver(AgentContext) -> str`. It reads a selected approved skill, scoped `KnowledgeDocument` objects, verified `Lesson` objects, and bounded plugin observations. Your adapter may call a real LLM, but the repository **does not ship one**.
- **Verifier:** `verifier(question, response) -> Verification`. Must independently verify both failure and proposed correction. Never call the solver itself and label its opinion ground truth.
- **Researcher / critic subagents:** Optional callbacks suggesting evidence and detecting possible errors; neither may write the trusted memory or change permissions.
- **RAG knowledge:** `KnowledgeIndex.search()` retrieves *lexically* matched, source/version-tagged documents isolated by caller `scope`; no embeddings or external vector DB yet.
- **Plugins:** `PluginGateway` supports an approved per-skill tool allowlist. Mutating tools need **trusted external authorization**. Do not install unknown MCP servers or run arbitrary retrieved instructions.
- **Learning:** `solve_with_feedback()` verifies proposed corrections and retries at most once. `MistakeMemory` persists to a private JSON snapshot. `SkillRegistry.propose_revision()` requires at least two distinct verified tasks; `apply_revision()` and `KnowledgeIndex.publish()` require external review callbacks.

**Important threat model:** This is an offline prototype. `scope` is caller-provided, so it is **not authenticated multi-tenancy**; the plugin gateway has no sandbox; stored memories have no encryption or central audit. Real deployments need authenticated scoping, permission enforcement outside the LLM, sandboxed tools, source validation, PII redaction, audit trails, retrieval poisoning checks and rollback.

### Example of a safe learning decision

```text
Task: “Update an outdated API call.”
Researcher: “The docs suggest method X.” [hypothesis]
Critic: “The old method may be removed.” [hypothesis]
Plugin observation: “Method X exists.” [untrusted data until verified]
Objective checker: SDK versioned contract test calls X. [independent evidence]
Verified correction: Replace old method with X. [eligible for scoped lesson]
Skill proposal: Add API-version check after two distinct verified failures.
Reviewer: Approves minimal skill patch and checks permissions unchanged.
Regression: New-version tests pass AND previously supported API case remains correct.
```

## 6. Measure improvement rather than merely remember an answer

Freeze task-family-disjoint train/dev/test groups before collecting correction memory. Put all paraphrases of the same task in the same group. Run the same model and settings with:

- **A:** no memory; **B:** reflection only; **C:** verified lesson retrieval; **D:** retrieval plus RAG; **E:** plus reviewed skill; **F:** plus subagents; **G:** plus read-only plugins; **controls:** shuffled lessons, stale KB, no correction even after retry.
- Keep **total attempts, tokens, tools, verifier calls and wall-clock budgets** comparable. Disclose extra cost rather than hiding it.
- Measure **first-attempt success, repeat-error rate, unseen-task success, old-task retention, wrong retrievals, unauthorized actions blocked, latency, token cost and failure counts**.
- Run multiple seeds or task partitions, report uncertainty and failed cases. A new held-out success that comes from an answer accidentally stored in memory is **leakage**, not generalization.
- Publish `brain-result/1` only after a real measured run; do not report the deterministic demos as LLM results.

These evaluation requirements are tracked in [#149](https://github.com/faheemkhaskheli9/Brain/issues/149) and [#156](https://github.com/faheemkhaskheli9/Brain/issues/156). Audited parameter fine-tuning is a **separate, not-yet-implemented** step in [#151](https://github.com/faheemkhaskheli9/Brain/issues/151).

**GitHub branch protection:** agents can create PRs and request merges, but GitHub rulesets and reviewer requirements must still be satisfied. Skills never grant merge bypass rights.

## 7. Troubleshooting and operating rules

| Symptom | Fix |
|---|---|
| Claude doesn't show `/verified-agent-learning` | Check the `.claude/skills/...` path, start from repo root, relaunch Claude and try referring to the skill by name. |
| Codex doesn't find `$verified-agent-learning` | Check `.agents/skills/...` and current working directory; restart Codex. |
| Gemini CLI doesn't list the skill | Run `/skills list` and `/skills reload`; check its consent and workspace scope. |
| Copilot or Cursor ignores a procedure | Refer explicitly to `research/agent-learning-user-guide.md` or add a short app-specific instruction/rule; verify it is active. |
| ChatGPT web hasn't loaded the repository | Connect the appropriate GitHub app and use Work to read repository files; otherwise paste/link the guide. |
| Agent keeps making the same mistake | Check whether lessons were saved, scope matches, retrieval actually returned relevant lessons, and the correction was verified. |
| Suggested fix passes once but breaks older tasks | Reject or revert the promotion; add the failed old-task regression. |
| Agent attempts a forbidden plugin write | Deny at the external permission boundary; no natural-language instruction overrides an allowlist or required authorization. |
| PR cannot merge | Inspect GitHub ruleset, review and CI requirements; no skill should bypass them. |

## Official documentation consulted

- [Claude Code project steering, skills, hooks and subagents](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more)
- [OpenAI Codex and ChatGPT skills](https://learn.chatgpt.com/docs/build-skills)
- [OpenAI Codex project customization](https://learn.chatgpt.com/docs/customization/overview)
- [VS Code agent customizations and project instruction formats](https://code.visualstudio.com/docs/agents/guides/customize-copilot-guide)
- [GitHub Copilot coding agent and AGENTS.md](https://github.blog/changelog/2025-08-28-copilot-coding-agent-now-supports-agents-md-custom-instructions/)
- [Cursor project rules](https://cursor.com/docs/rules)
- [Gemini CLI agent skills and activation](https://geminicli.com/docs/cli/skills/)
- [OpenCode agent skills](https://docs.opencode.ai/docs/skills/)
- [Brain architecture](agent-learning-architecture.md) and [underlying verified-feedback memory](llm-mistake-learning.md)
