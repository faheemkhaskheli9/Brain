---
title: Measuring the brain - methods and open datasets
category: simulation
tags: [methods, eeg, meg, fmri, neuropixels, calcium-imaging, optogenetics, open-data, allen-brain-observatory, openneuro, dandi, nwb, bids, ibl, microns]
use_cases:
  - how does neuroscience record brain activity and what can each method see
  - EEG vs fMRI vs Neuropixels - which resolution do I get
  - where can I download real brain recordings to test a model
  - how do I load Allen, DANDI, IBL, OpenNeuro or MICrONS data in Python
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1038/nn.3839
  - https://doi.org/10.1038/nature24636
  - https://doi.org/10.1038/nature06976
  - https://doi.org/10.1038/s41593-019-0550-9
  - https://doi.org/10.7554/eLife.71774
  - https://doi.org/10.7554/eLife.78362
---

# Measuring the brain - methods and open datasets

## Summary
Every claim in this knowledge base rests on some way of measuring the brain, and
every method trades **where** (spatial resolution), **when** (temporal
resolution), **how much** (coverage) and **how invasive**. No method sees
millions of single neurons at millisecond precision across a whole human brain.
Large open archives now let anyone test a model against real recordings: the
Allen Brain Observatory, OpenNeuro, DANDI, the International Brain Laboratory
and MICrONS. This file is the bridge from reading the KB to building with it.

## How it works

### Methods and their resolution (established)
Ranges are order-of-magnitude, as in the classic spatial-temporal map of methods
(Sejnowski, Churchland & Movshon 2014).

| Method | Measures | Spatial | Temporal | Coverage | Invasive? |
|---|---|---|---|---|---|
| **EEG** | Summed electric fields of synchronised cortical neurons, at the scalp | centimetres | milliseconds | whole head, poor for deep structures | no |
| **MEG** | Magnetic fields from the same currents | millimetres to centimetres | milliseconds | whole head | no |
| **fMRI** (BOLD) | Blood oxygenation, an indirect, slow proxy of local activity | ~1-3 mm voxels | seconds; response peaks ~5 s after activity | whole brain | no |
| **Single units / tetrodes** | Spikes of individual neurons from an electrode tip | one neuron | sub-millisecond | a few to tens of neurons | yes |
| **Neuropixels** | Spikes from a 10 mm silicon shank with 960 sites, 384 recorded at once | one neuron | sub-millisecond | hundreds of neurons across several brain regions per probe | yes |
| **Calcium imaging** (two-photon) | Fluorescence of a calcium indicator such as GCaMP, which rises when a neuron spikes | one neuron (micrometres) | tens to hundreds of ms (indicator kinetics) | hundreds to thousands of neurons near the surface | yes, genetically modified animals |
| **Optogenetics** | Not a recording: light-gated ion channels switch genetically chosen cells on or off | cell type | milliseconds | one region per light source | yes, genetically modified animals |

Notes:
- **fMRI is slow because blood is slow.** The BOLD signal is neural activity
  smeared by a haemodynamic response lasting tens of seconds (Glover 1999). It
  reflects synaptic input and local processing more than spiking output, and a
  voxel averages hundreds of thousands of neurons (Logothetis 2008). The code
  below shows the consequence.
- **EEG and MEG are fast but blurred.** Reconstructing where a signal came from
  (source localisation) has no unique solution without extra assumptions.
- **Neuropixels** (Jun et al. 2017; Steinmetz et al. 2021 for the 2.0 version)
  made recording from many regions at once routine in rodents; it is the
  workhorse of the IBL brain-wide map and the Allen visual coding survey.
- **Calcium imaging** sees every labelled cell in a field of view and can follow
  the same neurons for weeks, but the indicator is slower than a spike, so exact
  spike times have to be inferred (Chen et al. 2013 for GCaMP6).
- **Optogenetics** (Boyden et al. 2005) is what turns correlation into causation:
  silence a cell type and see what breaks.
- Most human data are non-invasive (EEG, MEG, fMRI). Most single-neuron data are
  from mice and monkeys. Human single-neuron data come from patients with
  electrodes implanted for clinical reasons.

### Open datasets (established, last checked 2026-10-11)

| Dataset | What it holds | Format | Python access |
|---|---|---|---|
| **Allen Brain Observatory** | Standardised two-photon calcium imaging of mouse visual cortex during visual stimuli (de Vries et al. 2020), plus a Neuropixels survey of the mouse visual system (Siegle et al. 2021) | NWB | `allensdk` |
| **OpenNeuro** | Hundreds of public human MRI, EEG, MEG and iEEG datasets (Markiewicz et al. 2021) | BIDS | `openneuro-py`, then `nibabel` / `mne-bids` |
| **DANDI** | Archive for cellular neurophysiology: electrophysiology, calcium imaging and behaviour, BRAIN Initiative funded | NWB (Rübel et al. 2022) | `dandi`, `pynwb` |
| **International Brain Laboratory (IBL)** | Mice doing one standardised decision task across many labs (IBL 2021), with Neuropixels recordings across the brain | ALF files via ONE | `ONE-api` |
| **MICrONS** | A cubic millimetre of mouse visual cortex: activity of tens of thousands of neurons, then the electron-microscopy connectome of the same tissue | CAVE tables, meshes | `caveclient` |

MICrONS size figures are in [[whole-brain-emulation-projects]]. The Allen Cell
Types Database (single-neuron recordings, used by `game/eval.py`) is covered in
[[evaluating-brain-models]].

### Loading the data
These snippets need the named packages and a network connection; check each
project's docs for current versions.

```python
# not run here: needs allensdk, pynwb, dandi, ONE-api, openneuro-py and network access
from allensdk.core.brain_observatory_cache import BrainObservatoryCache
boc = BrainObservatoryCache(manifest_file="allen/manifest.json")
exps = boc.get_ophys_experiments(targeted_structures=["VISp"])
data = boc.get_ophys_experiment_data(exps[0]["id"])
t, dff = data.get_dff_traces()             # time, (cells x time) dF/F traces

# DANDI: download a dandiset with the CLI (`dandi download DANDI:<id>`), then:
from pynwb import NWBHDF5IO
with NWBHDF5IO("path/to/file.nwb", "r") as io:
    nwb = io.read()
    units = nwb.units.to_dataframe()       # one row per sorted neuron, spike_times column

# IBL: public data through ONE
from one.api import ONE
one = ONE(base_url="https://openalyx.internationalbrainlab.org",
          password="international", silent=True)
eid = one.search()[0]                      # one experimental session
trials = one.load_object(eid, "trials")    # choices, stimulus contrast, feedback, ...

# OpenNeuro: a BIDS dataset, e.g. ds000117 (faces, MEG+EEG+fMRI)
import openneuro
openneuro.download(dataset="ds000117", target_dir="ds000117", include=["sub-01"])
```

## Relevance to building brain-like AI
- **Pick the data that matches the model's level.** A spiking model is tested
  against single units (DANDI, IBL, Allen Neuropixels); a vision network against
  population responses in visual cortex (Allen, Brain-Score); a whole-brain or
  cognitive model against fMRI or EEG (OpenNeuro). See [[levels-of-brain-modeling]].
- **Model the measurement, not just the brain.** To compare a model to fMRI,
  pass its activity through a haemodynamic response first; to compare to calcium
  imaging, through the indicator's kinetics. Skipping this step compares two
  different things.
- **Standard formats save weeks.** NWB and BIDS mean one loader works across
  hundreds of datasets.
- How to turn a recording into a score: [[evaluating-brain-models]].

## Code
Why fMRI cannot separate fast events. Brief neural events are convolved with
the canonical double-gamma haemodynamic response (as in SPM; Glover 1999).

```python
import numpy as np
from math import gamma

# Why fMRI cannot resolve fast events: neural activity is seen through a slow
# haemodynamic response (canonical double-gamma HRF, peak ~5 s, undershoot ~15 s).
dt = 0.1
t = np.arange(0, 30, dt)

def hrf(t, a1=6, a2=16, ratio=1 / 6):
    g = lambda a: t ** (a - 1) * np.exp(-t) / gamma(a)
    h = g(a1) - ratio * g(a2)
    return h / h.max()

def bold(event_times, T=60):
    neural = np.zeros(int(T / dt))
    neural[(np.array(event_times) / dt).astype(int)] = 1.0   # brief neural events
    return np.convolve(neural, hrf(t))[: len(neural)]

def n_peaks(sig):
    return int(np.sum((sig[1:-1] > sig[:-2]) & (sig[1:-1] > sig[2:]) & (sig[1:-1] > 0.3 * sig.max())))

print("HRF peaks at", round(t[np.argmax(hrf(t))], 1), "s")
for gap in (1, 4, 12):
    print(f"two events {gap:>2} s apart -> BOLD peaks seen: {n_peaks(bold([10, 10 + gap]))}")
assert n_peaks(bold([10, 11])) == 1    # 1 s apart: merged into one bump
assert n_peaks(bold([10, 22])) == 2    # 12 s apart: resolved
```

Output: events 1 s and 4 s apart produce one BOLD bump; 12 s apart, two. A
single spike lasts about a millisecond.

## Open questions
- How exactly does the BOLD signal relate to spiking, synaptic input and
  inhibition in each brain region? (Logothetis 2008.)
- Can non-invasive methods ever reach cellular resolution in humans?
- How well do mouse findings, where the best data are, transfer to primates and
  humans?

## Related
- [[evaluating-brain-models]] - scoring a model against these recordings.
- [[whole-brain-emulation-projects]] - MICrONS and other connectome datasets.
- [[levels-of-brain-modeling]] - which data fits which level of model.
- [[sensory-systems-and-vision]] - the visual cortex most of these datasets record.

## References
- Sejnowski, Churchland & Movshon (2014) "Putting big data to good use in neuroscience", *Nat Neurosci* 17:1440. doi:10.1038/nn.3839
- Logothetis (2008) "What we can do and what we cannot do with fMRI", *Nature* 453:869. doi:10.1038/nature06976
- Glover (1999) "Deconvolution of impulse response in event-related BOLD fMRI", *NeuroImage* 9:416. doi:10.1006/nimg.1998.0419
- Jun et al. (2017) "Fully integrated silicon probes for high-density recording of neural activity", *Nature* 551:232. doi:10.1038/nature24636
- Steinmetz et al. (2021) "Neuropixels 2.0: A miniaturized high-density probe for stable, long-term brain recordings", *Science* 372:eabf4588. doi:10.1126/science.abf4588
- Chen et al. (2013) "Ultrasensitive fluorescent proteins for imaging neuronal activity", *Nature* 499:295. doi:10.1038/nature12354
- Boyden et al. (2005) "Millisecond-timescale, genetically targeted optical control of neural activity", *Nat Neurosci* 8:1263. doi:10.1038/nn1525
- de Vries et al. (2020) "A large-scale standardized physiological survey reveals functional organization of the mouse visual cortex", *Nat Neurosci* 23:138. doi:10.1038/s41593-019-0550-9
- Siegle et al. (2021) "Survey of spiking in the mouse visual system reveals functional hierarchy", *Nature* 592:86. doi:10.1038/s41586-020-03171-x
- Markiewicz et al. (2021) "The OpenNeuro resource for sharing of neuroscience data", *eLife* 10:e71774. doi:10.7554/eLife.71774
- Rübel et al. (2022) "The Neurodata Without Borders ecosystem for neurophysiological data science", *eLife* 11:e78362. doi:10.7554/eLife.78362
- International Brain Laboratory et al. (2021) "Standardized and reproducible measurement of decision-making in mice", *eLife* 10:e63711. doi:10.7554/eLife.63711
- MICrONS Consortium (2025) "Functional connectomics spanning multiple areas of mouse visual cortex", *Nature* 640:435. doi:10.1038/s41586-025-08790-w
- Portals: https://observatory.brain-map.org, https://openneuro.org, https://dandiarchive.org, https://www.internationalbrainlab.com, https://www.microns-explorer.org
