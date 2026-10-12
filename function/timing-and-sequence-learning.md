---
title: Timing and sequence learning (time cells, interval timing, chunking)
category: function
tags: [timing, interval-timing, time-cells, scalar-timing, weber-law, sequence-learning, chunking, theta-sequences, population-clock, temporal-context-model, striatum, cerebellum, positional-encoding]
use_cases:
  - how does the brain keep track of elapsed time without a clock
  - what are hippocampal time cells
  - why does timing error grow with the interval (scalar timing, Weber's law for time)
  - how are motor sequences learned and chunked
  - compare transformer positional encodings with how brains represent time
  - build a population clock that decodes elapsed time in numpy
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1037/0033-295X.84.3.279
  - https://doi.org/10.1038/nrn1764
  - https://doi.org/10.1016/j.neuron.2011.07.012
  - https://doi.org/10.1038/nrn2558
  - https://doi.org/10.1006/jmps.2001.1388
  - https://doi.org/10.1162/NECO_a_00212
  - https://doi.org/10.1016/j.cub.2015.02.036
---

# Timing and sequence learning (time cells, interval timing, chunking)

## Summary
The brain has no central clock, yet animals time intervals from milliseconds to
minutes and learn long sequences of actions. Time seems to be read from the **state
of populations** whose activity changes in a reproducible way after an event: cells
that fire one after another (time cells, striatal sequences) or decay at many speeds.
A behavioural law constrains every model: timing error grows in proportion to the
interval (**scalar timing**). For AI the contrast is sharp: a transformer is given
position from outside, while a recurrent network, like a brain, must carry time in
its own state.

## How it works

### Scalar timing (established behaviour)
When animals or people time an interval, the spread of their responses grows in
proportion to its length, so the coefficient of variation (SD / mean) stays roughly
constant: Weber's law applied to time. Gibbon (1977) made this the core of **scalar
expectancy theory**, in which a pacemaker emits pulses, an accumulator counts them,
and a stored count is compared with memory. The pacemaker-accumulator picture fits
the behaviour; whether the brain contains anything like a pacemaker is doubted, since
neural recordings point to population dynamics instead (Buhusi & Meck 2005).

### Where timing happens
- **Several systems, by timescale (supported).** Sub-second motor timing depends on the
  cerebellum; seconds-to-minutes interval timing on cortico-striatal circuits and
  dopamine (Buhusi & Meck 2005; Mauk & Buonomano 2004). The division is not clean.
- **Cerebellum (established).** Cerebellar damage impairs producing and judging short
  intervals (Ivry & Keele 1989; [[action-selection-and-motor-control]]). In eyeblink
  conditioning, Purkinje cells learn a pause timed to the interval between cue and
  air puff, and the timing survived when the cue was replaced by direct stimulation of
  the input fibres, pointing to a mechanism inside the Purkinje cell (Johansson et al.
  2014, **supported**).
- **Striatum (supported).** In rats timing a fixed interval, striatal neurons fired in
  a sequence that tiled the interval, and the sequence stretched or compressed when the
  interval changed (Mello, Soares & Paton 2015).
- **Frontal cortex (supported).** In monkeys producing intervals, medial frontal
  responses kept their shape but scaled in time with the interval; the speed of the
  population trajectory set the produced time (Wang et al. 2018).
- **Hippocampal time cells (established).** In rats waiting through a delay between two
  stimuli, CA1 neurons fired at successive moments of the delay, tiling it like place
  cells tile a track; when the delay changed, many re-timed (MacDonald et al. 2011).
  Earlier, Pastalkova et al. (2008) found CA1 cell sequences during wheel running in a
  memory delay, generated internally without changing sensory cues, that predicted the
  rat's next choice. Later time cells tend to have wider time fields (Eichenbaum 2014),
  the single-cell face of scalar timing (**supported**). Lateral entorhinal cortex
  carries a slowly changing signal from which time within and across trials can be
  decoded (Tsao et al. 2018).

### Models of neural time
| Model | Time is | Gives scalar timing? |
|---|---|---|
| Pacemaker-accumulator (Gibbon 1977) | A count of pulses | Only with added noise assumptions |
| Population clock / state-dependent network (Karmarkar & Buonomano 2007; Buonomano & Maass 2009) | The current state of a recurrent network, which evolves the same way after each cue | Not by default |
| Temporal context model (Howard & Kahana 2002) | A slowly drifting context vector bound to each item as it is encoded | Explains recency and contiguity in free recall |
| Scale-invariant Laplace model (Shankar & Howard 2012) | Leaky integrators with a spectrum of time constants, inverted into time cells | Yes, when time constants are spread geometrically |

These models are **hypotheses**; they are not exclusive, and each matches some data.
The population-clock idea links to [[population-dynamics-and-neural-manifolds]]: an
interval is a trajectory through state space, and its speed sets the timing (Wang et
al. 2018).

### Sequences and chunking
- **Chunking (established).** People recode long strings into fewer, larger units
  (Miller 1956); working memory holds a few chunks, not a few items
  ([[attention-and-working-memory]]).
- **Motor chunking in the basal ganglia (supported).** Graybiel (1998) proposed the
  basal ganglia package practised action sequences into chunks run as one unit. As mice
  learned a fast lever-press sequence, striatal and nigral neurons came to fire at the
  start or stop of the whole sequence (Jin & Costa 2010), a neural mark of a chunk
  boundary.
- **Theta sequences (established).** Within one theta cycle, hippocampal place cells
  fire in the order of places just behind, at and ahead of the animal (Foster & Wilson
  2007), a compressed sweep that follows from phase precession
  ([[brain-rhythms-and-oscillations]]). The compression brings the spikes of cells for
  neighbouring places close enough in time for STDP to link them (**hypothesis** for how
  sequences are learned). Replay in sleep reuses these sequences
  ([[sleep-and-memory-consolidation]]).

## Relevance to building brain-like AI
- **Positional encodings vs intrinsic time.** Self-attention is blind to order, so
  transformers add a positional encoding; the original one used sinusoids whose
  wavelengths form a geometric progression (Vaswani et al. 2017). That bank of
  geometric timescales resembles the spread of time constants in the Laplace model
  (an analogy, not evidence of shared mechanism). Recurrent and state-space networks
  instead carry time in their state, as brains seem to.
- **A cheap, scale-invariant clock**: leaky traces with geometrically spaced time
  constants, read out linearly, give elapsed time with error proportional to the
  interval (code below). It needs no training of the clock itself.
- **Hippocampal models and transformers.** Whittington, Warren & Behrens (2022) showed
  that a transformer with recurrently updated positional encodings is closely related to
  a hippocampal model and develops place- and grid-like units (**hypothesis** about the
  brain, a result about the model).
- **Chunking as abstraction**: learning to execute and plan over reusable sub-sequences
  (options, macro-actions) is the RL counterpart of basal-ganglia chunking.

## Code
A population clock: 60 units whose rates decay with time constants spread from 0.1 s
to 100 s. A maximum-likelihood readout of noisy rates recovers elapsed time without
bias, and its error grows in proportion to the interval, so the coefficient of
variation stays constant: scalar timing from geometric time constants alone.

```python
import numpy as np

rng = np.random.default_rng(0)
# 60 units, each a trace that decays from 1 after a cue, with log-spaced time constants
taus = np.logspace(-1, 2, 60)                  # 0.1 s to 100 s
sigma = 0.1                                    # same noise on every unit's rate

def clock(t):                                  # population state t seconds after the cue
    return np.exp(-np.asarray(t)[..., None] / taus)

grid = np.logspace(-2, 2, 4000)                # candidate elapsed times, 0.01 to 100 s
templates = clock(grid)

def read_time(states):                         # max-likelihood decoder for Gaussian noise
    dist = (templates ** 2).sum(axis=1) - 2 * states @ templates.T   # squared distance - const
    return grid[np.argmin(dist, axis=1)]

stats = {}
for t in [0.5, 1, 2, 4, 8]:
    est = read_time(clock(t) + sigma * rng.normal(size=(500, taus.size)))
    stats[t] = (est.mean(), est.std())
    print(f"t = {t:>3} s: decoded {est.mean():5.2f} +/- {est.std():.3f} s, CV {est.std() / est.mean():.3f}")

cvs = np.array([sd / m for m, sd in stats.values()])
assert all(abs(m - t) / t < 0.1 for t, (m, _) in stats.items())   # unbiased
assert stats[8][1] > 8 * stats[0.5][1]          # error grows with the interval...
assert cvs.max() / cvs.min() < 1.5              # ...in proportion to it (scalar timing)
```

Why it is scalar: at time `t` the units that still change fastest are those with `tau`
near `t`, and with time constants spread evenly on a log scale the same number of
units is in that range at every `t`, so precision scales with `1/t` (the argument of
Shankar & Howard 2012, valid only inside the range of time constants).

## Open questions
- Is there one timing mechanism used in different circuits, or different mechanisms
  per timescale and task?
- Do time cells measure time, or do they track whatever changes during a delay
  (distance, effort, internal state)?
- How are chunk boundaries chosen, and how does a learned chunk become a single unit
  that can be inserted in new sequences?
- How does the brain learn sequences far longer than one theta cycle compresses?

## Related
- [[brain-rhythms-and-oscillations]] - theta phase precession, the basis of theta sequences.
- [[memory-systems]] - the hippocampus binds items to time and context in episodes.
- [[action-selection-and-motor-control]] - basal ganglia and cerebellum, the circuits for chunking and short-interval timing.
- [[population-dynamics-and-neural-manifolds]] - intervals as trajectories whose speed sets the timing.
- [[spatial-navigation]] - place cells, the spatial counterpart of time cells.
- [[sleep-and-memory-consolidation]] - replay of learned sequences during sleep.
- [[attention-and-working-memory]] - the chunk limit of working memory.
- [[language-and-llms]] - transformers, where position is given rather than kept.

## References
- Gibbon (1977) "Scalar expectancy theory and Weber's law in animal timing", *Psychol Rev* 84:279. doi:10.1037/0033-295X.84.3.279
- Buhusi & Meck (2005) "What makes us tick? Functional and neural mechanisms of interval timing", *Nat Rev Neurosci* 6:755. doi:10.1038/nrn1764
- Mauk & Buonomano (2004) "The neural basis of temporal processing", *Annu Rev Neurosci* 27:307. doi:10.1146/annurev.neuro.27.070203.144247
- Ivry & Keele (1989) "Timing functions of the cerebellum", *J Cogn Neurosci* 1:136. doi:10.1162/jocn.1989.1.2.136
- Johansson et al. (2014) "Memory trace and timing mechanism localized to cerebellar Purkinje cells", *PNAS* 111:14930. doi:10.1073/pnas.1415371111
- Mello, Soares & Paton (2015) "A scalable population code for time in the striatum", *Curr Biol* 25:1113. doi:10.1016/j.cub.2015.02.036
- Wang, Narain, Hosseini & Jazayeri (2018) "Flexible timing by temporal scaling of cortical responses", *Nat Neurosci* 21:102. doi:10.1038/s41593-017-0028-6
- MacDonald, Lepage, Eden & Eichenbaum (2011) "Hippocampal 'time cells' bridge the gap in memory for discontiguous events", *Neuron* 71:737. doi:10.1016/j.neuron.2011.07.012
- Pastalkova et al. (2008) "Internally generated cell assembly sequences in the rat hippocampus", *Science* 321:1322. doi:10.1126/science.1159775
- Eichenbaum (2014) "Time cells in the hippocampus: a new dimension for mapping memories", *Nat Rev Neurosci* 15:732. doi:10.1038/nrn3827
- Tsao et al. (2018) "Integrating time from experience in the lateral entorhinal cortex", *Nature* 561:57. doi:10.1038/s41586-018-0459-6
- Karmarkar & Buonomano (2007) "Timing in the absence of clocks: encoding time in neural network states", *Neuron* 53:427. doi:10.1016/j.neuron.2007.01.006
- Buonomano & Maass (2009) "State-dependent computations: spatiotemporal processing in cortical networks", *Nat Rev Neurosci* 10:113. doi:10.1038/nrn2558
- Howard & Kahana (2002) "A distributed representation of temporal context", *J Math Psychol* 46:269. doi:10.1006/jmps.2001.1388
- Shankar & Howard (2012) "A scale-invariant internal representation of time", *Neural Comput* 24:134. doi:10.1162/NECO_a_00212
- Miller (1956) "The magical number seven, plus or minus two", *Psychol Rev* 63:81. doi:10.1037/h0043158
- Graybiel (1998) "The basal ganglia and chunking of action repertoires", *Neurobiol Learn Mem* 70:119. doi:10.1006/nlme.1998.3843
- Jin & Costa (2010) "Start/stop signals emerge in nigrostriatal circuits during sequence learning", *Nature* 466:457. doi:10.1038/nature09263
- Foster & Wilson (2007) "Hippocampal theta sequences", *Hippocampus* 17:1093. doi:10.1002/hipo.20345
- Vaswani et al. (2017) "Attention is all you need", *NeurIPS*. arXiv:1706.03762
- Whittington, Warren & Behrens (2022) "Relating transformers to models and neural representations of the hippocampal formation", *ICLR*. arXiv:2112.04035
