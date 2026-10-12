# Paper notes: H. Scale, neurons and dendrites

Structured notes on the sources cited by hypotheses H131-H137, generated 2026-10-12. One note rests on a local PDF (Herculano-Houzel), two on web full text (Beaulieu-Laroche and Sadtler, via PMC), one on an abstract in sources.json (Gidon), and two (Beniaguev 2021, Poirazi 2003) had no abstract and no reachable full text, so those notes say almost nothing by design. H137 cites no source.

## Herculano-Houzel 2009: The human brain in numbers: a linearly scaled-up primate brain
- **Cited for:** H131 (humans differ mainly by having more cortical neurons, not a different algorithm)
- **Link:** https://doi.org/10.3389/neuro.09.031.2009 · **Basis:** full text
- **Question:** How many neurons does the human brain have, and is it special compared with other mammals?
- **Method / model:** A review of cell counts made with the isotropic fractionator (a method that dissolves tissue and counts nuclei), across rodents, insectivores and primates. It compares power-law scaling of brain mass with neuron number.
- **Experiments:** Compilation of the author's lab data (Herculano-Houzel et al. 2006, 2007, Sarko et al. 2009), plus comparison with older estimates (about 100 billion neurons, 10x more glia).
- **Key results:**
  - Different scaling rules apply within each order, so brain size is not a proxy for neuron number.
  - The adult male human brain (1.5 kg) has about 86 billion neurons and 85 billion non-neuronal cells, close to the 93 and 112 billion expected for a generic 1.5 kg primate brain.
  - The cerebral cortex holds 16 billion neurons, about 19% of the total, and the cerebellum 69 billion. Cortical fraction is similar to other mammals.
  - Among primate-style economical brains, the human brain is the largest, so it has the most neurons.
- **Limitations / caveats:** It is about cell numbers, not computation. The linear scaling argument rests on comparison with other primates and on cell counts.
- **Bearing on H131:** partly supports. The paper supports "more neurons, ordinary primate scaling". "Not a different algorithm" is an inference it does not test.
- **Reproduce in this repo:** Train a local-rule model at several widths and check whether any abstraction measure changes smoothly or jumps. A step change would count against H131.

## Beaulieu-Laroche et al. 2018: Enhanced dendritic compartmentalization in human cortical neurons
- **Cited for:** H132 (human dendrites are more compartmentalised, giving more independent computing units per neuron)
- **Link:** https://doi.org/10.1016/j.cell.2018.08.045 · **Basis:** full text (web, first 100,000 of about 135,700 characters)
- **Question:** How does the larger size of human L5 pyramidal neurons change synaptic integration?
- **Method / model:** Whole-cell patch recordings from L5 pyramidal neurons: somatic and dendritic, multi-site and voltage clamp, plus outside-out and nucleated patches. A rat L5 model was extended to human length by "stretching" (conductances redistributed) or "scaling" (densities kept).
- **Experiments:** Human tissue from epilepsy surgery (ages 20-42), 300 um slices, versus adult rat temporal association cortex. Dendritic recordings up to about 1,834 um from the soma.
- **Key results:**
  - Distal human dendritic input resistance was about double (median 35.1 versus 15.7 MOhm).
  - Distal dendritic spikes were weaker and often failed to reach the soma. Human somas burst less.
  - The 50%-attenuation distance was similar (about 453 versus 456 um). The weaker distal coupling comes from greater length, and lower HCN current (median 4.6 versus 13.1 pA) fits the higher resistance.
  - The stretched model reproduced the human behaviour and the scaled model did not.
- **Limitations / caveats:** Epilepsy patients, anaesthesia and drugs; some datasets come from two patients; the species and regions differ; slices lack in vivo input. Compartmentalisation here means weaker distal-to-soma coupling.
- **Bearing on H132:** partly supports. It shows stronger electrical compartmentalisation. It does not show more independent computing units or higher capacity, which is the row's inference.
- **Reproduce in this repo:** Compare a lumped neuron with a multi-compartment (coupled-subunit) neuron at matched synapse count on a feature-binding task. Record capacity.

## Gidon et al. 2020: Dendritic action potentials and computation in human layer 2/3 cortical neurons
- **Cited for:** H133 (human cortical dendrites can compute XOR on their own)
- **Link:** https://doi.org/10.1126/science.aax6239 · **Basis:** abstract only
- **Question:** Do human layer 2/3 pyramidal dendrites have action potentials that give single neurons extra computational power?
- **Method / model:** Dual somatodendritic recordings in slices of surgically resected tissue from epilepsy patients.
- **Experiments:** Human layer 2/3 pyramidal neurons. The abstract gives no counts.
- **Key results:** It reports previously unknown classes of dendritic action potentials, which "allow single neurons to solve two long-standing computational problems... considered to require multilayer neural networks". XOR is by implication one of them. The abstract does not use that word.
- **Limitations / caveats:** Abstract only. I could not check how the XOR claim was derived (experiment or model), how many cells it rests on, or whether it was tested in rodents.
- **Bearing on H133:** supports as phrased, with the above gap. The row also says "can compute XOR on their own", which matches the abstract's claim.
- **Reproduce in this repo:** A single unit with a non-monotonic dendritic nonlinearity versus a point-neuron (monotonic) unit on XOR and on 8-bit parity.

## Beniaguev, Segev & London 2021: Single cortical neurons as deep artificial neural networks
- **Cited for:** H134 (a single cortical neuron is as powerful as a 5-8 layer deep net)
- **Link:** https://doi.org/10.1016/j.neuron.2021.07.002 · **Basis:** abstract only (sources.json holds no abstract, so this is from title and metadata)
- **Question:** I could not read the paper. The title states the claim.
- **Method / model:** Not verified. The "5-8 layers" figure comes from the row, and I could not check it against the paper.
- **Experiments:** n/a
- **Key results:** None verified.
- **Limitations / caveats:** I did not see how the paper fits the neuron model, what it needs (for example whether the result depends on NMDA synapses), or how it measures "as powerful".
- **Bearing on H134:** cannot verify. The row's headline claim and layer count are unchecked.
- **Reproduce in this repo:** Fit a small convolutional or shallow net to the input-output relation of a simulated multi-compartment neuron model and compare depth against fit error.

## Poirazi, Brannon & Mel 2003: Pyramidal neuron as two-layer neural network
- **Cited for:** H135 (each dendritic branch is a separate learning unit, a two-layer neuron)
- **Link:** https://doi.org/10.1016/s0896-6273(03)00149-1 · **Basis:** abstract only (sources.json holds no abstract, so this is from title and metadata)
- **Question:** I could not read the paper. The title says the pyramidal neuron can be modelled as a two-layer network.
- **Method / model:** Not verified.
- **Experiments:** n/a
- **Key results:** None verified.
- **Limitations / caveats:** The title speaks of a two-layer description of the neuron's input-output function. The row adds "each branch is a separate learning unit", and the "learning" part may come from a different paper by Poirazi and Mel (2001, memory capacity with active dendrites). I have not verified that attribution.
- **Bearing on H135:** cannot verify. The two-layer structure matches the title. Branch-local plasticity and storage gain are unchecked.
- **Reproduce in this repo:** Branch-local plasticity versus neuron-global plasticity on a fixed number of stored associations in a two-layer neuron model. Count storage.

## Sadtler et al. 2014: Neural constraints on learning
- **Cited for:** H136 (learning is confined to the existing low-dimensional manifold of activity)
- **Link:** https://doi.org/10.1038/nature13665 · **Basis:** full text (web)
- **Question:** Does an existing network constrain which activity patterns a subset of its neurons can produce, and by what principle?
- **Method / model:** A closed-loop BCI. Population activity from M1 is mapped through a 10-dimensional factor-analysis "intrinsic manifold" (IM) and a Kalman filter to cursor velocity. A within-manifold perturbation permutes the 10 factors, and an outside-manifold perturbation permutes the neural units before the FA stage.
- **Experiments:** Two rhesus monkeys, 85-91 recorded units, an eight-target centre-out task, 400 or 250 baseline trials and 600 perturbation trials. Monkey J: 78 sessions (30 within, 48 outside). Monkey L: 31 sessions (16 within, 15 outside).
- **Key results:**
  - Within-manifold perturbations were learned. Outside-manifold perturbations were not, within a session.
  - Initial impairment, principal angles between control spaces, and required preferred-direction changes were matched across the two types.
  - The estimated intrinsic dimensionality was 9.81 +/- 0.31 across days.
- **Limitations / caveats:** The finding holds on a timescale of hours (single sessions), and the manifold is defined by factor analysis over a calibration block. The paper does not show that off-manifold patterns can never be learned.
- **Bearing on H136:** supports. The row's "confined" is stronger than "difficult on a timescale of hours" in the abstract.
- **Reproduce in this repo:** Train a recurrent net, estimate the principal subspace of its activity, then train readout perturbations inside it and outside it, and compare learning speed.

## H137 (no source, marked "new")
- **Cited for:** H137 (synapses are the real budget: more synapses per neuron matter more than more neurons)
- **Basis:** n/a. The row cites nothing. Herculano-Houzel 2009 and the dendrite papers above do not test synapses against neurons.
- **Reproduce in this repo:** Equal-synapse versus equal-neuron scaling in a local-rule net on the same task. Compare accuracy and any abstraction measure.

## Corrections to the hypotheses file
- H131: the cited paper gives cell counts and scaling rules. "Not a different algorithm" is the row's inference, so mark it as such.
- H132: Beaulieu-Laroche et al. show weaker distal-dendrite-to-soma coupling in longer human neurons. They do not show "more independent computing units".
- H134, H135: Beniaguev 2021 and Poirazi 2003 could not be read here, so the 5-8 layers claim and the "separate learning unit" claim are unchecked. For H135, consider whether Poirazi & Mel 2001 is the learning/storage source (unverified).
- H136: "confined" overstates. Sadtler et al. report that outside-manifold mappings were not learned in single sessions (hours).
- H137: no citation. Add one or label the row as the repo's own idea.
