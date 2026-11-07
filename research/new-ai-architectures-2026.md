# Recent AI learning architectures: Google Hope, Hope-1 and alternatives (2025–2026)

**Reviewed:** 2026-11-07. **Evidence status:** primary-source literature review, **not** a Brain reproduction or experimental result. Findings below are author-reported unless explicitly marked as repo-reproduced (none are). This is an engineering comparison, not evidence about what biology implements.

## Why this matters

Brain aims to learn from mistakes, remember, adapt, transfer skills, plan and create. Research on online neural memories, multi-timescale updates, local credit assignment and agent skill reuse offers **testable ideas**, not a ready-made human-level learner. Preserve Brain World's **backprop-free** constraint. Gradient-trained LLMs, SEAL, Titans, Hope, test-time training and V-JEPA are **separate reference systems or baselines**, not capabilities already learned by the creature.

## Two different projects named Hope

1. **Google Research's Hope (capitalization also written HOPE), from Nested Learning:** [Google's announcement, 2025-11-07](https://research.google/blog/introducing-nested-learning-a-new-ml-paradigm-for-continual-learning/) and [Behrouz et al., *Nested Learning: The Illusion of Deep Learning Architectures*, arXiv:2512.24695](https://arxiv.org/abs/2512.24695) (arXiv submitted **2025-12-31**). Nested Learning describes a model as interacting optimization problems with different update frequencies. The paper combines a self-modifying learning module with a **Continuum Memory System** and reports selected language modeling, knowledge incorporation, few-shot and long-context results. **Limits:** this is gradient-based architecture research, not a proven cure for catastrophic forgetting and not a backprop-free Brain World implementation.
2. **Blankline Research's Hope-1:** [*Introducing Hope*, 2026-05-07](https://www.blankline.org/research/hope/paper). A separate, developer-described program using discrete latent program codes, search and verifiers for abstract reasoning. It reports toy ARC-style experiments (about 0.69M–3M parameters) **and failed/partial milestones**; the authors explicitly say weights, implementation and detailed data are proprietary. **Evidence grade:** non-reproducible developer report; do not pool or confuse these results with Google's Hope.

## Primary-source research matrix

| Work (publication or announcement) | Mechanism and evidence | What Brain can test | Key limitation |
|---|---|---|---|
| [Titans, NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/hash/a4ca07aa108036f80cbb5b82285fd4b1-Abstract-Conference.html) / [MIRAS, Google Research 2025](https://research.google/blog/titans-miras-helping-ai-have-long-term-memory/) | Online neural memory; memory-update 'surprise', forgetting and momentum; author-reported language/long-context results. | Priority-weighted episodic replay (#152). | Surprise is not automatically usefulness or verified error. Neural fast-weight updates are not plain database retrieval. |
| [Nested Learning / Hope, 2025](https://arxiv.org/abs/2512.24695) | Self-modifying learned update mechanism plus frequency-separated continuum memory; evaluated by authors. | Multiple memory lifetimes and retention gates (#150, #65). | Learned optimizer and memory are not evidence of biological learning; gradient mechanisms would violate the creature's constraint if copied directly. |
| [Sleep framework, Google Research, 2026-10-27](https://research.google/blog/the-sleep-framework-a-new-way-for-llms-to-retain-knowledge-in-continual-learning/) | Alternates interaction ('wake') and offline parameter consolidation ('sleep'), with MoE capacity, distillation, generated practice and RL; authors report long-context tests up to 10M tokens. | Stage replay/consolidation and measure retention (#150, #152). | Results are Google-reported and use offline **weight** updates; 'sleep' is an analogy, not neuroscience evidence. |
| [PC-ALM, Seely & Gould, 2026](https://arxiv.org/abs/2605.31022) / [official code](https://github.com/SakanaAI/pc-alm) | Augmented-Lagrangian predictive coding, local dual-variable dynamics; authors demonstrate deep residual networks (including a 1,000-layer setup in later reported experiments). | Toy matched-budget local learning comparison (#65). | Local communication can approximate backprop credit; not proof of gradient-free training in the mathematical sense or of a brain mechanism. |
| [Universal Test-Time Training, 2026-10-04](https://arxiv.org/abs/2610.05484) | Shares online-updated neural memory across layers; author-reported language and view-synthesis results. | Study memory-sharing versus isolated stores, if justified by existing benchmarks (#65). | Gradient-based TTT, significant complexity, and no published Brain-World result. |
| [ParaTTT, 2026-10-28](https://arxiv.org/abs/2610.38255) | Parallelizes nonlinear test-time training; authors report speedups on particular language-model configurations. | Consider only as an **LLM reference** when online-weight-update cost is the bottleneck (#151). | Training-efficiency work, not a demonstrated solution to embodied continual learning. |
| [SEAL, NeurIPS 2025](https://papers.neurips.cc/paper_files/paper/2025/hash/6b41e04c41726e2a60e456d0a2b961ab-Abstract-Conference.html) | Model-generated self-edits and fine-tuning directives, scored through downstream performance. | Audited SFT/LoRA update against persistent retrieval (#151, #156). | Changes model weights using gradient training; independent test and rollback required. |
| [Skill-Pro, ICML 2026](https://proceedings.mlr.press/v306/mi26d.html) | Derives executable, reusable agent skills with initiation/execution/termination conditions and evaluation gates, without model-weight updates. | Skill composition and reviewed skill promotion (#112, #149). | Procedural reuse is **not** parameter learning or proof of unseen-task generalization. |
| [ProactAgent, EMNLP Findings 2026](https://aclanthology.org/2026.findings-emnlp.775/) | Learns *when* and *what* to retrieve from experience/skills; authors report gains on evaluated agent worlds. | Retrieval-vs-no-retrieval paired continuations (#114, #115). | Retrieval can create overhead and leakage; the reported gains are benchmark-specific. |
| [V-JEPA 2, Meta, 2025](https://ai.meta.com/research/publications/v-jepa-2-self-supervised-video-models-enable-understanding-prediction-and-planning/) | Video-trained predictive representations with planning experiments. | Small locally learned forward model plus bounded action rollouts (#113). | Backprop-trained visual model and large data regime; not a backprop-free drop-in. |
| [Hyperagents, 2026](https://arxiv.org/abs/2603.19461) | Editable task/meta-agent programs with selection based on evaluations. | Separate sandboxed software-improvement track, after independent verification (#155, #156). | Search over code changes can overfit tests or introduce unsafe behavior; no automatic permission elevation. |
| [Blankline Hope-1, 2026](https://www.blankline.org/research/hope/paper) | Verifier-guided discrete-latent program search. | Verifier-closed compositional reasoning toy tasks (#110, #111), if independently specified. | Source, models and datasets unavailable; results cannot be independently reproduced. |

**Interpretation:** these studies do not constitute a head-to-head benchmark and none validates human-level intelligence, creativity, durable forgetting resistance across arbitrary tasks or an actual biological learning algorithm. Distinguish *neural weight updates* from *retrieval of stored experience* and *handwritten procedural skills* in all reports.

## Integrate with existing Brain work (do not duplicate issues)

- **Highest priority: failure-aware replay**: reuse [#152](https://github.com/faheemkhaskheli9/Brain/issues/152) and its implementation PR if active; compare uniform vs surprise/verified-failure weighting. Build on existing reversed-cue, held-out and retention suites [#105](https://github.com/faheemkhaskheli9/Brain/issues/105), [#106](https://github.com/faheemkhaskheli9/Brain/issues/106), [#154](https://github.com/faheemkhaskheli9/Brain/issues/154). Do not replace already-implemented replay with an unrelated demo.
- **Different-timescale memories**: connect to existing **H163** (fast/slow weights), **H168** (consolidation), **H104** (replay for reusable schemas), and [#150](https://github.com/faheemkhaskheli9/Brain/issues/150). A stack of buffers is only an **analogy** to Google's trainable Hope CMS.
- **Local credit assignment**: compare a small PC-ALM-inspired mechanism with existing predictive-coding/feedback-alignment implementations under [#65](https://github.com/faheemkhaskheli9/Brain/issues/65). Keep Brain World backprop-free; clearly isolate conventional BP comparator arms.
- **Agent learning**: reuse [agent-learning architecture](agent-learning-architecture.md), [#149](https://github.com/faheemkhaskheli9/Brain/issues/149), [#151](https://github.com/faheemkhaskheli9/Brain/issues/151) and [#156](https://github.com/faheemkhaskheli9/Brain/issues/156). Compare memory-only, reviewed skills, retrieval policy and separately audited parameter training; do not equate criticism with independent verification.
- **Reasoning and transfer**: use existing [#112](https://github.com/faheemkhaskheli9/Brain/issues/112), [#113](https://github.com/faheemkhaskheli9/Brain/issues/113), [#114](https://github.com/faheemkhaskheli9/Brain/issues/114) and [#115](https://github.com/faheemkhaskheli9/Brain/issues/115) instead of starting a parallel roadmap. Research ordering remains governed by [#120](https://github.com/faheemkhaskheli9/Brain/issues/120) and [#136](https://github.com/faheemkhaskheli9/Brain/issues/136).

## Proposed falsifiable experiment: does multi-timescale error replay actually help?

**Status:** proposed; **not executed**, with no outcome or positive claim. Register any experiment and frozen configurations in the **existing issue #152**, before measuring results. This builds on Brain World's backprop-free learner.

**Hypothesis:** compared with identical-size uniform replay, a surprise-prioritized replay strategy with periodic consolidation reduces repeated mistakes and speeds adaptation to reversals, *without* reducing retained old-task performance.

| Arm | What changes | Purpose |
|---|---|---|
| A | No replay | Lower bound |
| B | Existing uniform replay | Current baseline |
| C | Same memory/compute budget, priority = capped prediction error × independently observed failure indicator | Does error priority alone help? |
| D | C plus periodic, bounded consolidation into a slower store; fixed combined capacity | Are two retention timescales additionally useful? |
| E | C with shuffled priorities | Negative control for extra selection machinery |

**Before running:** freeze seeds **1–10 minimum** (expand when CIs are too wide), held-out layouts/cues/glyphs, reversal schedule, episode/step budget, replay samples per episode, total memory bytes, storage/retrieval overhead, policy/environment version and checkpoint hashes. Tune hyperparameters exclusively on dev environments; never tune on reported held-out rooms. Preserve the same action stream and evaluation suite wherever paired comparison is possible.

**Primary metrics:** held-out success; repeated-error rate (same verified failure class per 100 opportunities); episodes or steps to reversal recovery; old-task accuracy after new-task training. **Secondary:** false-switch rate, forgetting delta, useful skill transfer, replay retrieval hits, CPU time, peak memory, learning curves and failure cases. Report per-seed values, paired intervals and tests, not only aggregate means.

**Decision rule (to finalize in #152 before runs):** the new arm must outperform uniform replay on a pre-registered primary outcome with statistically defensible uncertainty **and** pass existing retention/transfer regression gates at matched compute and memory. If there is no gain, extra overhead, leakage, or regression, record a **negative or inconclusive** result rather than calling the mechanism validated. Explicitly test whether any improvement survives a shuffled-priority control and a held-out task-family evaluation.

**Reporting:** one reproducible `brain-result/1` result per arm × seed, with config, code commit, budget, failed seeds, exact checkpoints where supported; update `research/claims.tsv` only when actual measurements support a claim, and regenerate the dashboard. Never label offline LLM fine-tuning as Brain World's own learned intelligence.

## Reading order and evidence caveats

1. Google Hope/Nested Learning for update frequencies; Titans/MIRAS for surprise-based memory; Sleep for consolidation ideas.
2. PC-ALM for the local-credit problem, alongside the existing repo's H001–H003 tests and their documented limitations.
3. Skill-Pro/ProactAgent for retrieval and procedural skills; SEAL for the **distinct** model-weights track.
4. uTTT/ParaTTT, V-JEPA 2 and Hyperagents as higher-cost, separate reference directions.
5. Hope-1 only as an **unreplicated** example of verifier-guided program search.

**Do not confuse:** paper-reported result ≠ independent replication ≠ Brain reproduction ≠ biological finding. Latest literature review is not an implemented capability.
