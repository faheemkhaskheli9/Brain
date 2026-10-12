# Paper notes for the learning-algorithm hypotheses

One file per hypothesis family in
[../learning-algorithm-hypotheses.md](../learning-algorithm-hypotheses.md). Each note
covers one cited paper: the question, the method or model, the experiments, the key
results (with the paper's numbers), the caveats, whether the paper really supports its
row, and the smallest numpy experiment that would check it here.

| File | Hypotheses |
|---|---|
| [A-credit-assignment.md](A-credit-assignment.md) | H001-H020: local approximations of backprop |
| [B-reward-neuromodulators.md](B-reward-neuromodulators.md) | H021-H038: reward, neuromodulators, three-factor rules |
| [C-self-supervised.md](C-self-supervised.md) | H039-H054: self-supervised objectives |
| [D-structure-abstraction.md](D-structure-abstraction.md) | H055-H080: structure, maps and abstraction |
| [E-priors-development.md](E-priors-development.md) | H081-H092: innate priors and development |
| [F-memory-consolidation.md](F-memory-consolidation.md) | H093-H108: memory, consolidation, forgetting |
| [G-language-reasoning.md](G-language-reasoning.md) | H109-H130: language and reasoning |
| [H-scale-dendrites.md](H-scale-dendrites.md) | H131-H137: scale, neurons, dendrites |
| [I-dynamics.md](I-dynamics.md) | H138-H151: dynamics and other computing primitives |
| [J-control-meta.md](J-control-meta.md) | H152-H161: control, attention, meta-learning |

Family K (H162-H170) has no published sources, so it has no notes.

## How far to trust a note
Every note says its **Basis**:
- **full text**: read from the paper (local PDF, arXiv, PMC or the publisher page).
  About 80 notes.
- **abstract only**: the paper body was paywalled or blocked scripted access (Cell,
  Science, Nature, PNAS, bioRxiv often answer 403). About 100 notes. Some sources have no
  abstract in the databases either; their notes give only the citation and say
  "unverified". Read those papers in a browser before relying on them.

The notes were written by AI agents on 2026-10-12 from the texts above and have not been
reviewed by a person. Each file ends with **Corrections to the hypotheses file**. The
corrections that the text supported have been applied to the rows (see the Log entry of
2026-10-12). The ones that rest on an abstract are left as flags in the notes.

## Re-checking
- Sources, links and PDFs: `python research/verify_sources.py` (see
  [../learning-algorithm-sources.md](../learning-algorithm-sources.md)).
- To upgrade an abstract-only note, open the paper's link, read the methods and results,
  and replace the note's fields and Basis.
