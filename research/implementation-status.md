# Implementation status vs. the issue backlog (#103)

Checked 2026-10-20 against `main` at b37dd33. Each row compares what the issue (and its comments)
says with what is in the repository: code, tests and a recorded result. "In repo" means a file on
`main`; a result counts only if the numbers are written in a topic file or a README.

## Closed issues whose work is not in the repository

The closing comments of these issues describe code and results from **local commits that were never
pushed** (they give `git log --grep` patterns, not hashes, and no such commits exist in any branch of
`origin`). The repository holds either nothing or an earlier work-in-progress script (c922e6c) with
no result. Tracked in #128.

| Issue | Comment says | In repo |
|---|---|---|
| #38 jointed legs | `GAINS.body = "cpg"`, `?body=cpg`: two antiphase oscillators drive damped hip springs; walk on seeds 1-5 in 104, 67, 164, 330, 65 episodes | A different body: `GAINS.joints` (`?legs=joints`, `brain.js:108`), hip angles with torque and damping, no CPG. No "Jointed legs" README section, no multi-seed result. #95 is written against the missing CPG body |
| #65 item 1, surprise | `world.reversed`, `sweep.mjs --arms reversal`, record saved as `brain.ctx`; seeds 1-10: no savings on return blocks (+0.026, p 0.25), false switches cost the normal rule | A different implementation: `GAINS.surprise` with fast/slow TD-error means (`brain.js:110`), `REVERSE` stage and `game/world/reversal.mjs`. No result recorded, not in `test_brain.mjs`, no README "Surprise" section |
| #65 item 3, forward model | `GAINS.fm`, `curiosity`, `surpriseFm`; curiosity 0.05: 10/10 graduate; 0.25: 5/10; model error did not detect reversals | Nothing: no forward model, no curiosity bonus, no README section |
| #86 spike timing vs count | `research/timing_vs_count.py`; result section in `function/neural-coding-and-computation.md` (LGN gratings +13.9 points, CI [5.9, 21.5]) | `research/spike_timing_areas.py` (WIP, `--synthetic` only verified); no result in the topic; register row 10 still "open" |
| #87 co-tuned inputs (MICrONS) | `research/microns_clustering.py`; RF distance 5.5% below shuffle within 10 µm; section in `anatomy/dendritic-computation.md` | `research/cotuned_inputs.py` (WIP, different data versions: v661 meshworks); no result in the topic; register row 11 "open". #96 builds on the missing result and script |
| #89 LLM-brain match | `research/llm_brain_match.py`; GPT-2 adds unique r² +0.042 over word statistics; result in `function/language-and-llms.md` | No script, no result; register row 13 "open" |
| #90 WM capacity | `research/wm_capacity.py`; TCC and VP beat slot models in cross-validated likelihood; section in `function/attention-and-working-memory.md` | `research/wm_capacity_models.py` (WIP); no result; register row 14 "open" |

Until the commits are found and pushed, or the analyses are re-run, **none of these numbers is a
result of this repository**. Do not cite them. The register rows correctly say "open".

## Open issues

| Issue | Implemented (with evidence) | Not done or not tested |
|---|---|---|
| #6 Brain Lab M5 | Linked from `guides/start-here.md:63` | Playtest with two non-experts; difficulty tuning |
| #34 Brain World purpose | Intro dialog (`game/world/index.html:173`), narration caption (`index.html:352`), milestone toasts (`index.html:430`), hover help on every panel label | Entry points (learn a mechanism / watch a learner / run an experiment). The intro says the creature "starts knowing nothing", but the curriculum, rewards, sensory encoding, action sets and gait reflex are designed; that and "reading is glyph recognition of 3-6 letters" are not said on the page. New-user comprehension test not done |
| #65 research threads | Item 1 partly (see above, no result). Context slots it builds on are tested (`test_brain.mjs`, README "Inferred context") | Item 1 result; item 2 (gated recurrent WM); item 3 (see above); item 4 (Hebbian features). README "New letters" (#37) points to item 4 as the next test of transfer |
| #94 richer vision | Nothing beyond the 15-ray retina | All |
| #95 CPG body | Depends on #38's missing CPG body | All; the `GAINS.joints` body has no later-stage measurement |
| #96 MICrONS follow-up | Depends on #87's missing result | All |
| #104 result schema | `brain-result/1` in `research/result_schema.py` (validator, summary with bootstrap CIs and paired sign-flip p), `game/world/result.mjs`; `sweep.mjs`, `reversal.mjs` and `transfer.mjs --out` write it; fixture test in CI | Not yet written by `h101_transfer.mjs` or `research/*.py`; no checkpoint references |
| #106 reversal benchmark | `reversal.mjs` measures adaptation, retention, false switches, detection; arms ablate surprise, replay, free slots; 10-seed result in `game/world/README.md` "Reversal" and `research/results/reversal-2026-10-24.json` | Noisy cues (#135) |
| #105, #108, #110-#116 | Nothing specific | All |
| #107 dashboard, #109 browser tests | Nothing | All (no browser test of any page) |
| #117 claim tracking | `build_index.py` checks frontmatter and links only | All |
| #118 baselines | H101 has a backprop arm in `research/h101_transfer.mjs` | No heuristic or conventional-RL baseline for Brain World |
| #119 release, #120 roadmap, #124 external repos | Planning issues | - |

## Closed issues checked and present

#37 (new letters: `transfer.mjs`, README "New letters", no transfer measured), #54, #56, #60-#64
(README sections and `test_brain.mjs`), #82, #83, #84, #85, #88, #92, #125 (scripts in `research/`
or `game/world/`, results in the topic files listed in `research/README.md`).
