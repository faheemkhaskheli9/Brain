# Brain

A knowledge base on the human brain, covering three questions:

1. **What is it?** Anatomy: regions, neurons, synapses (`anatomy/`).
2. **How does it work?** Coding, memory, perception, learning rules (`function/`).
3. **How do we build a digital version that learns like it?** Models, simulators,
   brain-inspired learning algorithms and a build roadmap (`simulation/`, `learning/`).

Start at [guides/start-here.md](guides/start-here.md), follow a reading list for
ML engineers, neuroscience students or players in
[guides/learning-paths.md](guides/learning-paths.md), or browse [INDEX.md](INDEX.md).

## Layout

| Folder | Holds |
|---|---|
| `guides/` | Entry point, glossary, learning paths, the build roadmap, a research workflow and the open-questions register |
| `anatomy/` | Structure: regions, cell types, synapses, dendrites, glia and the energy budget, comparative and evolutionary neuroscience |
| `function/` | How the brain computes, remembers, perceives, decides and learns: coding, population dynamics, memory, sleep, rhythms, attention, prefrontal abstraction, timing, emotion, language, social cognition, development, disorders |
| `learning/` | Brain vs deep learning; brain-inspired learning algorithms with code; efficient (energy, samples) learning; hyperdimensional computing |
| `simulation/` | Levels of modeling, spiking and reservoir networks, cognitive architectures, evaluation, datasets, hardware, brain-computer interfaces, emulation projects, saving a trained brain |
| `research/` | Catalog of every paper the topics cite (`papers.md`), a script that fetches open-access PDFs, and research notes and reports |
| `game/` | Brain Lab: a playable simulation, on desktop or in the browser, where each level is one idea from the KB. See [game/README.md](game/README.md) |

Every topic file has YAML frontmatter (title, tags, use_cases, status, sources).
`python build_index.py` regenerates `INDEX.md` and checks `[[links]]`. The rules
for adding topics are in [AGENTS.md](AGENTS.md); how to send a correction or review
a draft is in [CONTRIBUTING.md](CONTRIBUTING.md).

`pip install .` installs the one dependency (numpy, Python 3.10+). `ruff check .`
lints; CI runs it with the index, code-block and game checks.

## License

Code (`*.py` and code blocks in topics) is [Apache-2.0](LICENSE); prose is
[CC BY 4.0](LICENSE-CONTENT.md). Cited papers keep their own licenses.

## An honest framing

Nobody can simulate a human brain today in a way that reproduces human learning.
We know the parts well. We know some learning rules (Hebbian plasticity, STDP,
dopamine reward-prediction errors). We know some system-level principles
(complementary memory systems, predictive processing). But we do **not** know
the full algorithm, and the largest connectomes ever mapped are a fruit fly brain
and one cubic millimetre of mouse cortex. This KB separates what is established
from what is hypothesis, and the roadmap describes what you can actually build.
