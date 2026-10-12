---
title: Comparative and evolutionary neuroscience (which brain features are necessary)
category: anatomy
tags: [comparative, evolution, brain-scaling, neuron-count, allometry, birds, corvids, parrots, pallium, octopus, honeybee, mushroom-body, cerebellum-like, convergent-evolution, expansion-layer]
use_cases:
  - how do neuron counts scale with brain size across species
  - why do crows and parrots get primate-like intelligence from small brains
  - which brain features does a brain-like AI actually need to copy
  - can intelligence evolve without a neocortex
  - what do insect mushroom bodies and the cerebellum have in common
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1073/pnas.0604911103
  - https://doi.org/10.1073/pnas.0611396104
  - https://doi.org/10.1073/pnas.1517131113
  - https://doi.org/10.3389/neuro.09.031.2009
  - https://doi.org/10.1002/cne.21974
  - https://doi.org/10.1038/nrn1606
  - https://doi.org/10.1126/science.abc5534
  - https://doi.org/10.1126/science.1098410
  - https://doi.org/10.1016/j.cub.2012.09.001
  - https://doi.org/10.3389/fphys.2017.00164
  - https://doi.org/10.1038/nrn3357
  - https://doi.org/10.1016/s1364-6613(00)01601-6
  - https://doi.org/10.1016/j.asd.2011.02.004
  - https://doi.org/10.1016/j.neuron.2017.01.030
  - https://doi.org/10.1126/science.aam9868
---

# Comparative and evolutionary neuroscience (which brain features are necessary)

## Summary
Comparing brains across species is the closest thing neuroscience has to an ablation
study run by evolution. Three results matter for anyone copying the brain. First,
brain mass is a poor proxy for neuron count: primate and bird brains pack far more
neurons per gram than rodent brains. Second, flexible intelligence has evolved in
animals with no neocortex at all (corvids, parrots, octopuses, bees). Third, unrelated
animals have converged on the same few circuit motifs, such as the sparse, expanded
"granule cell" layer of the cerebellum and the insect mushroom body. Features that
keep reappearing are better candidates for "necessary" than features unique to us.

## How it works

### Brain scaling: neurons are not proportional to grams (established)
Herculano-Houzel and colleagues counted neurons by dissolving brain tissue into a
suspension of nuclei (the isotropic fractionator) and fitted power laws
`brain mass ~ N^b` across species of one order:

| Order (species) | Exponent b | What it means | Source |
|---|---|---|---|
| Rodents (6, mouse to capybara) | 1.587 | neurons get bigger as brains grow; 10x neurons costs ~39x mass | Herculano-Houzel, Mota & Lent 2006 |
| Primates (6, marmoset to macaque) | 1.054, not different from 1 | neuron size roughly constant; mass grows linearly with neurons | Herculano-Houzel et al. 2007 |
| Parrots and songbirds (28 bird species in all) | similar power functions in both groups | about twice the neurons of a primate brain of the same mass, 2-4x a rodent's | Olkowicz et al. 2016 |

Consequences, all from these papers:
- A generic rodent brain of 1.5 kg would hold about 12 billion neurons; a generic
  primate brain of that mass about 93 billion. The human brain (1508 g) holds about
  86 billion (Azevedo et al. 2009), close to the primate rule, so the human brain is
  a scaled-up primate brain rather than an outlier (Herculano-Houzel 2009). That it
  is "not exceptional" in cell composition is **supported**; whether absolute neuron
  count is what drives cognition, as she argues, is debated.
- A blue-and-yellow macaw has 3.14 billion neurons in a 20.7 g brain; a raven 2.17
  billion in 14.1 g. A macaque has 6.38 billion in 87 g (Olkowicz 2016 Table 1;
  Herculano-Houzel 2007 Table 1). Birds reach monkey-scale neuron counts in a brain
  a fraction of the size, because their neurons are packed at higher densities.

### Intelligence without a neocortex
- **Corvids and parrots (established that the pallium does the work).** Birds lack a
  six-layered cortex. The avian pallium is a set of nuclei derived from the same
  embryonic pallium as mammalian cortex, which led to the renaming of bird brain areas
  in 2005 (Jarvis et al. 2005). Stacho et al. (2020) traced fibre architecture and
  found repeated, column-like circuits running across the nuclear boundaries of the
  pallium, similar to the mammalian canonical cortical circuit. Corvids make tools,
  plan for the future and track what others know; Emery & Clayton (2004) argue these
  abilities evolved independently in corvids and apes (a **supported** convergence).
- **Octopus (established anatomy, hypothesis on its meaning).** Octopus nervous
  systems hold about 500 million nerve cells, split between the central brain, the
  optic lobes and the arm nerve cords, with relatively few fibres connecting these
  compartments (Levy & Hochner 2017, from counts by Young 1963). Much arm control is
  local, and the higher motor centres do not hold a body map. Hochner (2012) proposes
  that octopus intelligence is "embodied": control emerges from body mechanics plus
  distributed circuits rather than a central planner (**hypothesis**).
- **Honeybee (established behaviour).** A brain of about 1 million neurons (Menzel
  2012) supports social life, navigation, dance communication and learning that goes
  beyond elementary associations. Menzel & Giurfa (2001) argue this needs
  integration across modules in a central state, not only separate reflex modules.

### Convergent circuits: the expansion layer
Insect mushroom bodies and vertebrate cerebellum-like structures (cerebellum,
electrosensory lobe of fish, dorsal cochlear nucleus) share an architecture: masses of
tiny granule (Kenyon) cells that receive a few inputs each, send thin parallel fibres
onto a smaller set of output neurons, and learn at those output synapses (Farris
2011). The two lineages diverged long before either structure existed, so this is
convergence, not inheritance (**supported**; homology is still argued for some
structures). Theory explains why: a sparse, random expansion to many more units raises
the dimension of the representation, and the observed number of inputs per granule
or Kenyon cell is close to the value that maximises it (Litwin-Kumar et al. 2017).
Dasgupta et al. (2017) showed the fly olfactory version works as a locality-sensitive
hash for similarity search.

## Relevance to building brain-like AI
- **Count units, not volume.** Comparisons of "brain size" between models or species
  are meaningless without the scaling rule; the bird data show that dense packing,
  not size, delivers capacity. For hardware this is the energy and wiring cost per
  unit ([[glia-and-energy-budget]]).
- **The six-layered neocortex is probably not necessary (hypothesis, strongly
  suggested).** Birds reach ape-like cognition with a nuclear pallium, and octopuses
  with a wholly separate design. What the successful designs share is many neurons in
  a pallium-like associative region, recurrent loops, and modulated plasticity. Copy
  those properties, not the laminar layout.
- **Expansion plus a learned readout recurs.** Random sparse expansion followed by
  a trained linear readout is cheap, fast to learn and found in insects and
  vertebrates alike; reservoir computing and random-feature models are the AI
  versions ([[reservoir-computing]]).
- **Distributed control is a real option.** The octopus suggests that a body (or a
  robot) can offload control to local controllers with a thin central link.
- **Small can be enough for a lot.** A bee does flexible learning with about a
  million neurons, a useful sanity bound for what a compact model should manage.

## Code
Fit `brain mass ~ N^b` on real species means, check the exponents against the papers,
predict the human brain out of sample, and measure how many more neurons parrots and
corvids have than a primate brain of the same mass. All numbers are copied from the
cited tables (Herculano-Houzel 2006 and 2007 Table 1; Olkowicz 2016 Table 1;
Azevedo 2009). Six species per mammal order is all those papers measured; the bird
set is the 9 parrots and corvids of the 28 bird species in Olkowicz 2016. The code
has no randomness; a leave-one-out check stands in for resampling.

```python
import numpy as np

# (brain mass g, total neurons x10^6), species means copied from the papers' Table 1
rodents = {  # Herculano-Houzel, Mota & Lent 2006, Table 1
    "mouse": (0.416, 70.89), "hamster": (1.020, 89.97), "rat": (1.802, 200.13),
    "guinea pig": (3.759, 239.62), "agouti": (18.365, 856.74), "capybara": (76.036, 1601.12)}
primates = {  # Herculano-Houzel, Collins, Wong & Kaas 2007, Table 1 (tree shrew left out: not a primate)
    "marmoset": (7.780, 635.80), "galago": (10.150, 936.00), "owl monkey": (15.730, 1468.41),
    "squirrel monkey": (30.216, 3246.43), "capuchin": (52.208, 3690.52), "macaque": (87.346, 6376.16)}
birds = {  # Olkowicz et al. 2016, Table 1: parrots and corvids
    "budgerigar": (1.317, 321.82), "gray parrot": (8.827, 1565.93), "kea": (13.593, 2148.67),
    "macaw": (20.731, 3135.79), "jay": (4.597, 1085.42), "magpie": (5.425, 897.27),
    "jackdaw": (6.023, 967.99), "rook": (8.357, 1508.72), "raven": (14.135, 2170.68)}

def fit(d):
    """log10(brain mass) = a + b*log10(neurons); returns (b, a)."""
    m, n = np.array(list(d.values())).T
    return np.polyfit(np.log10(n * 1e6), np.log10(m), 1)

def neurons_at(mass, coef):
    b, a = coef
    return 10 ** ((np.log10(mass) - a) / b)

b_rod, b_pri = fit(rodents)[0], fit(primates)[0]
print(f"mass ~ N^{b_rod:.2f} in rodents (paper: 1.587), N^{b_pri:.2f} in primates (paper: 1.054)")
assert 1.45 < b_rod < 1.75 and 0.9 < b_pri < 1.2 and b_rod > b_pri

# Jackknife: the ordering survives dropping any one species from either group
for d in (rodents, primates):
    for k in d:
        sub = {s: v for s, v in d.items() if s != k}
        assert (fit(sub)[0] > b_pri - 0.25) if d is rodents else (fit(sub)[0] < b_rod - 0.25)

# Out-of-sample check: human brain 1508 g, 86 billion neurons (Azevedo et al. 2009)
pri, rod = neurons_at(1508, fit(primates)), neurons_at(1508, fit(rodents))
print(f"a 1508 g brain: primate rule {pri/1e9:.0f} bn neurons, rodent rule {rod/1e9:.0f} bn (human: 86 bn)")
assert abs(pri / 86e9 - 1) < 0.3 and rod < 0.25 * 86e9

# Birds pack more neurons per gram than a primate brain of the same mass
ratios = {s: n * 1e6 / neurons_at(m, fit(primates)) for s, (m, n) in birds.items()}
print("bird neurons / primate-rule neurons at the same mass:",
      ", ".join(f"{s} {r:.1f}" for s, r in ratios.items()))
assert all(r > 1.2 for r in ratios.values())
assert 1.5 < np.median(list(ratios.values())) < 3.5   # paper: "about twice as many"
```

The fit gives exponents of about 1.55 (rodents) and 1.06 (primates), close to the
published 1.587 and 1.054; the small rodent gap comes from fitting species means
rather than the papers' exact procedure. The primate rule predicts about 103 billion
neurons for a 1508 g brain, the rodent rule about 13 billion, against a measured 86
billion. Parrots and corvids come out at 1.7-2.5 times the primate rule.

## Open questions
- Whether absolute neuron count (especially in pallium or cortex) explains cognition
  across species, or whether connectivity and neuron type matter as much.
- How far the avian pallium is homologous to specific cortical layers versus only to
  the pallium as a whole; the 2020 column finding sharpened, not settled, this.
- What octopus learning circuits (the vertical lobe) share with vertebrate memory
  systems, given how long the two lineages have evolved apart.
- Whether whales and elephants, with much bigger brains, follow primate-like or
  rodent-like scaling; counts exist for few species.

## Related
- [[brain-structure-overview]] - the human regions these comparisons are measured against.
- [[glia-and-energy-budget]] - the energy cost per neuron that scaling rules imply.
- [[neurons-and-synapses]] - neuron size and density, the variable that differs between orders.
- [[whole-brain-emulation-projects]] - fly and other small-animal connectomes as emulation targets.
- [[memory-systems]] - hippocampus and cerebellum, the vertebrate side of the convergence.
- [[brain-vs-deep-learning]] - which brain features AI already copies or lacks.
- [[efficient-brain-like-learning]] - doing more with fewer units, as birds and bees do.
- [[reservoir-computing]] - random expansion with a trained readout, the AI form of the mushroom body.
- [[innate-priors-and-infant-learning]] - evolved structure as a prior.

## References
- Herculano-Houzel, Mota & Lent (2006) "Cellular scaling rules for rodent brains", *PNAS* 103:12138. doi:10.1073/pnas.0604911103 (Table 1: rodent data)
- Herculano-Houzel, Collins, Wong & Kaas (2007) "Cellular scaling rules for primate brains", *PNAS* 104:3562. doi:10.1073/pnas.0611396104 (Table 1: primate data)
- Olkowicz et al. (2016) "Birds have primate-like numbers of neurons in the forebrain", *PNAS* 113:7255. doi:10.1073/pnas.1517131113 (Table 1: 28 bird species)
- Herculano-Houzel (2009) "The human brain in numbers: a linearly scaled-up primate brain", *Front Hum Neurosci* 3:31. doi:10.3389/neuro.09.031.2009
- Azevedo et al. (2009) "Equal numbers of neuronal and nonneuronal cells make the human brain an isometrically scaled-up primate brain", *J Comp Neurol* 513:532. doi:10.1002/cne.21974
- Jarvis et al. (2005) "Avian brains and a new understanding of vertebrate brain evolution", *Nat Rev Neurosci* 6:151. doi:10.1038/nrn1606
- Stacho et al. (2020) "A cortex-like canonical circuit in the avian forebrain", *Science* 369:eabc5534. doi:10.1126/science.abc5534
- Emery & Clayton (2004) "The mentality of crows: convergent evolution of intelligence in corvids and apes", *Science* 306:1903. doi:10.1126/science.1098410
- Hochner (2012) "An embodied view of octopus neurobiology", *Curr Biol* 22:R887. doi:10.1016/j.cub.2012.09.001
- Levy & Hochner (2017) "Embodied organization of *Octopus vulgaris* morphology, vision, and locomotion", *Front Physiol* 8:164. doi:10.3389/fphys.2017.00164
- Young (1963) "The number and sizes of nerve cells in *Octopus*", *Proc Zool Soc Lond* 140:229 (cited via Levy & Hochner 2017).
- Menzel (2012) "The honeybee as a model for understanding the basis of cognition", *Nat Rev Neurosci* 13:758. doi:10.1038/nrn3357
- Menzel & Giurfa (2001) "Cognitive architecture of a mini-brain: the honeybee", *Trends Cogn Sci* 5:62. doi:10.1016/S1364-6613(00)01601-6
- Farris (2011) "Are mushroom bodies cerebellum-like structures?", *Arthropod Struct Dev* 40:368. doi:10.1016/j.asd.2011.02.004
- Litwin-Kumar et al. (2017) "Optimal degrees of synaptic connectivity", *Neuron* 93:1153. doi:10.1016/j.neuron.2017.01.030
- Dasgupta, Stevens & Navlakha (2017) "A neural algorithm for a fundamental computing problem", *Science* 358:793. doi:10.1126/science.aam9868
