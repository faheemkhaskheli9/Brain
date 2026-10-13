# Connectomics and whole-brain emulation: can an exact human brain replica be built? (state as of October 2026)

Research date: 2026-10-12. Every number has an inline source. Dates in brackets are when the item was published or announced. Items marked "(not re-verified here)" were carried over from the owner's KB file `simulation/whole-brain-emulation-projects.md` and were not re-fetched in this pass.

## Largest completed connectomes and their sizes, and progress toward a whole mouse brain

### Takeaway
As of October 2026, complete synapse-level connectomes exist only for insects and smaller animals. The largest are the adult fly brain (FlyWire, ~139k neurons, 2024) and the whole male fly CNS (brain plus nerve cord, ~166.7k neurons, published in *Cell* in September 2026). Mammals have only ~1 mm³ volumes: MICrONS mouse cortex (~120k neurons, ~523M synapses, 2025) and H01 human cortex (2024). No whole mouse connectome exists. The most active project images 10-15 mm³ (2-3% of a mouse brain). Credible timelines for a whole mouse put it about 5 years out (optimistic, expansion microscopy) to 10-15 years out (EM, Wellcome).

### Cited Findings
**Completed connectomes**
- [1986] *C. elegans*: 302 neurons, ~7,000 synapses, traced by hand from EM (White et al. 1986). From the owner's KB, not re-verified here.
- [Oct 2025] About ten whole-nervous-system *C. elegans* datasets now exist from individual worms, and "40-50% of synaptic connections differ between identical worms" — [State of Brain Emulation 2025 site](https://brainemulation.mxschons.com/)
- [2024] FlyWire adult female fly brain: 139,255 neurons and 50M+ synapses (Dorkenwald et al., *Nature* 634:124). From the owner's KB, not re-verified here — [NIH summary](https://www.nih.gov/news-events/nih-research-matters/complete-wiring-map-adult-fruit-fly-brain)
- [Preprint Oct 2025; *Cell*, published online 3 Sep 2026] Male *Drosophila* CNS (central brain, optic lobes and ventral nerve cord): 166,700 neurons. Berg et al., "Sexual dimorphism in the complete Drosophila male central nervous system connectome", DOI 10.1016/j.cell.2026.08.015, led by Janelia — [Sci.News, 9 Sep 2026](https://www.sci.news/biology/complete-fruit-fly-connectome-15053.html); [UKRI](https://www.ukri.org/news/world-first-map-of-a-male-fly-brain-a-win-for-neuroscience/)
  - The paper found 262 sex-specific and 114 sexually dimorphic cell types, which make up 4.8% of the central brain. The preprint was DOI 10.1101/2025.10.09.680999, with a Janelia release dated 6 Oct 2025 — [Janelia](https://www.janelia.org/news/researchers-reveal-connectome-of-the-male-fruit-fly-central-nervous-system)
  - Fully proofread adult fly connectomes now exist for both "the male central nervous system and the female brain" — [SoBE 2025 site](https://brainemulation.mxschons.com/)
- [Apr 2025] MICrONS, 1 mm³ of mouse visual cortex: ~120,000 neurons and 523M automatically detected synapses. It is the "largest dense mouse reconstruction" — [SoBE 2025 site](https://brainemulation.mxschons.com/); [MICrONS Explorer](https://www.microns-explorer.org/cortical-mm3). The owner's KB also records ~200,000 total cells and ~75,000 neurons with activity recorded before imaging.
- [2024] H01, 1 mm³ of human temporal cortex: ~57,000 cells, ~150M synapses, 1.4 PB of images (Shapson-Coe et al., *Science* 384:eadk4858). From the owner's KB, not re-verified here — [doi](https://doi.org/10.1126/science.adk4858)

**Toward a whole mouse brain**
- [Sep 2023] NIH BRAIN CONNECTS: $150M for 11 projects. Its flagship is a $33M Harvard-led project, with Google, Allen, MIT, Cambridge, Princeton and JHU, to map 10-15 mm³ of mouse hippocampal formation (2-3% of the brain) over 5 years. It expects about 25 PB of data — [Google Research blog](https://research.google/blog/google-research-embarks-on-effort-to-map-a-mouse-brain/)
- [2025] A search summary says NIH funding-priority changes in early 2025 hit the flagship project, and that its technical work appears to continue without NIH support. This is secondary and unconfirmed; I did not find the primary source — [BRAIN Initiative CONNECTS page](https://braininitiative.nih.gov/taxonomy/term/235)
- [21 Jun 2023] The Wellcome "Scaling connectomics" report says a whole mouse connectome "should be a goal on a 10-15 year timeline". Manual proofreading could take "~100,000 person-years" with today's methods — [Wellcome](https://wellcome.org/insights/reports/scaling-connectomics)
- Wellcome's EM cost breakdown, as cited by E11 Bio:
  - Imaging: ~$300M over 5 years.
  - Registration and segmentation: ~$400M per year for 2 years.
  - Proofreading: ~$2B per year for 7-15 years, so $7-21B total and more than 95% of the cost.
  - Raw-data cloud storage: more than $1B.
  - Source: [E11 Bio roadmap, 3 Dec 2024](https://e11.bio/blog/roadmap)
- [Dec 2024] E11 Bio PRISM combines protein barcoding, expansion microscopy (integrated with LICONN) and self-proofreading AI segmentation. E11 claims:
  - "at least a 100-fold reduction" in whole-brain connectomics cost;
  - later mouse connectomes for "tens of millions of dollars", perhaps $10M;
  - a full optical mouse connectome "in just five years", so about 2029.
  - These are company targets, not results — [E11 Bio roadmap](https://e11.bio/blog/roadmap)
- [1 Oct 2025] E11 released a PRISM pilot in mouse hippocampus as a bioRxiv preprint (Park, Sheridan et al., with Boyden and Winnubst) and a public toolbox — [E11 PRISM blog](https://www.e11.bio/blog/prism); [Addgene collection](https://www.addgene.org/depositor-collections/e11-bio-prism-collection)
- [Jun 2025] LICONN (Tavakoli, Lyudchik, Januszewski, Danzl et al., *Nature* 642:398-410, ISTA + Google) is light-microscopy connectomics. Two hydrogels expand the tissue about 16-fold, giving effective resolution below 20 nm on standard microscopes, and synapse-level reconstructions also carry molecular labels — [IDEAS/RePEc record](https://ideas.repec.org/a/nat/nature/v642y2025i8067d10.1038_s41586-025-08985-1.html); [ISTA news](https://ista.ac.at/en/news/piecing-together-the-brain-puzzle/); [Google Research pub](https://research.google/pubs/light-microscopy-based-dense-connectomic-reconstruction-of-mammalian-brain-tissue/)
- [Oct 2025] Cost per reconstructed neuron has fallen from ~$16,500 for the original *C. elegans* connectome to ~$100 in recent larval-zebrafish projects. Proofreading is still the bottleneck for mammalian neurons — [SoBE 2025, arXiv 2510.15745v2](https://arxiv.org/pdf/2510.15745v2)
- Asimov Press gives secondhand Wellcome figures for ~70M mouse neurons: $200-300M for imaging, $7-21B for proofreading, and up to 17 years. Its own projection for expansion microscopy is about $100M over ~5 years — [Asimov Press](https://press.asimov.com/articles/brains)
- Multi-beam EM (61 or 91 beams in parallel) is one way to speed up imaging — [SoBE 2025](https://arxiv.org/pdf/2510.15745)
- [Dec 2025] A researcher quoted by MIT McGovern says a complete mouse connectome is achievable "within 10 to 15 years" — [MIT McGovern](https://mcgovern.mit.edu/2025/12/15/all-the-connections/)
- [Apr 2026] An RNA-barcode method charted thousands of mouse-brain connections, which "turns brain mapping into a sequencing task". This is projection-level, not dense synaptic — [ScienceDaily](https://www.sciencedaily.com/releases/2026/04/260407193848.htm)
- [Sep 2026] NSF gave the University of Vermont $19M over five years for a connectomics observatory — [Valley News](https://vnews.com/2026/09/25/vermont-brain-mapping-observatory/)

### Inferences
- Scale gap to human: the human brain is ~1.2 million mm³ (owner's KB). H01 covered 1 mm³ with 1.4 PB, so EM imaging of a human brain at the same rate would be on the order of 10^6 PB, about an exabyte, before segmentation. A secondary source puts EM scanning of a human brain at about $100B ([GreaterWrong](https://www.greaterwrong.com/posts/STbrbCypsobBwaghf/will-whole-brain-emulation-matter-for-the-ai-transition-2); secondary, treat as rough).
- The binding constraint is proofreading cost, not imaging. Self-proofreading barcoded expansion microscopy (PRISM, LICONN) is the main bet for bringing a mouse below $100M, but no mammalian whole-brain result exists yet.
- New since the KB: the male CNS connectome (2025 preprint, *Cell* Sep 2026); LICONN (*Nature* Jun 2025); E11 PRISM (Oct 2025); the SoBE 2025 report; and the ~$16,500 to ~$100 per-neuron cost trend. The KB's milestone table does not list the male CNS or MANC.

### Gaps
- I did not retrieve exact synapse counts for the 2026 male CNS paper (Sci.News says only "millions of connections"). I did not separately look up MANC (male nerve cord, 2023-2024) figures.
- I found no 2026 primary announcement of a mammalian volume larger than ~1 mm³ being finished. The status of the BRAIN CONNECTS hippocampus project in 2026 is unconfirmed.
- The Wellcome page did not show its dollar figures directly; they come via E11 and Asimov.

## Simulations built from connectomes: size, hardware, speed and behaviour

### Takeaway
Connectome-based simulation reproduces some behaviour in worms and flies. These models simplify heavily: point neurons, inferred weights, little or no neuromodulation. The large mammalian and human-scale simulations (Fugaku mouse cortex, China's Digital Twin Brain) are not built from synaptic connectomes. They use atlas statistics and MRI tractography, and they validate against coarse signals such as BOLD, not specific behaviour or memories. Nothing anywhere is an "exact replica".

### Cited Findings
**Fly**
- [Nature 634, 2024] Shiu et al. built a leaky integrate-and-fire (LIF) model of the entire adult fly brain from FlyWire connectivity plus predicted neurotransmitter identity. Activating sugar- or water-sensing neurons predicted which neurons drive feeding, and optogenetics in real flies confirmed the predictions — [Nature record](https://ideas.repec.org/a/nat/nature/v634y2024i8032d10.1038_s41586-024-07763-9.html); [bioRxiv preprint](https://www.biorxiv.org/content/10.1101/2023.05.02.539144.full.pdf)
  - Its simplifications, per SoBE 2025: zero basal firing, no gap junctions, and no neuromodulation beyond excitation/inhibition — [SoBE 2025](https://arxiv.org/pdf/2510.15745)
  - A public implementation (hosted by Eon Systems) describes ~138k neurons and "~5M synapses". The "5M" probably means connections between neuron pairs rather than individual synapses (FlyWire has 50M+ synapses), so treat it as a labelling inconsistency — [GitHub eonsystemspbc/fly-brain](https://github.com/eonsystemspbc/fly-brain)
  - I could not verify the widely repeated "~95% accuracy" figure in a primary source.
- [Early 2026] Eon Systems (a San Francisco public benefit corporation) showed the Shiu-based whole-brain emulation driving a NeuroMechFly v2 / MuJoCo body that walked, groomed and fed or drank in a sandbox. Eon calls it the first multi-behaviour embodied WBE. That claim is the company's own, and I found no peer-reviewed paper — [ForkLog](https://forklog.com/en/researchers-upload-simulated-fly-brain-into-a-matrix/amp); [ISPR, Apr 2026](https://ispr.info/2026/04/21/researchers-upload-model-of-flys-brain-to-matrix-let-it-control-virtual-body/); [Let's Data Science](https://letsdatascience.com/news/researchers-simulate-fruit-fly-brain-controlling-virtual-bod-55db9549)
  - Coverage is inconsistent: neuron counts are given as ~125k or 139,255, one outlet claims ~91% behavioural accuracy, and the claim that scrambled wiring drops accuracy to 1% appears in only one source — [Seedtable](https://seedtable.com/companies/eon-systems); [Yahoo Tech](https://tech.yahoo.com/science/articles/scientists-upload-complete-fruit-fly-183733167.html)
  - One critic reports Eon aims to emulate a mouse brain in about two years, and disputes its consciousness framing — [Feedbagel](https://feedbagel.com/post/analysis-eon-systems-claims-of-digital-fruit-fly-consciousness-and-brain-emulati)
- [arXiv Feb 2026, v2 Mar 2026] FlyGM (Jin, Zhu, Zhang, Sui) uses a network with exactly the adult fly connectome's structure as a whole-body locomotion controller. It beat rewired graphs, random graphs and MLPs on sample efficiency and performance. The connectome is used as an architecture prior, and the weights are trained, so this is not an emulation — [arXiv 2602.17997](https://arxiv.org/abs/2602.17997v1)
- [2025] The Janelia/DeepMind whole-body fly model uses an RL-trained controller, not the connectome — [Fanatical Futurist](https://www.fanaticalfuturist.com/2026/02/researchers-put-a-simulated-fly-brain-in-a-simulated-fly-body-in-the-matrix/). In a March 2026 MIT talk, Srini Turaga described plans for a full-animal fly simulation — [MIT BCS](https://bcs.mit.edu/events/special-seminar-srini-turaga-0)

**Worm**
- [*Nature Computational Science*, 16 Dec 2024] BAAIWorm (Lei Ma, Peking University/BAAI) is a closed-loop simulation of brain, body and environment: 302 multi-compartment, biophysically detailed neurons, 96 muscle cells and fluid forces in 3D. Inputs were ion channels, morphologies, electrophysiology and whole-brain calcium imaging — [PKU NBIC](https://nbic.pku.edu.cn/en/Achievements/d57de79476bf4b279d32e0c285da6405.htm); [hyper.ai](https://hyper.ai/en/stories/2f3136b4d2b779f41646870c64df8321)
  - The preprint version (MetaWorm) ran in real time at 30 fps — [bioRxiv](https://www.biorxiv.org/content/10.1101/2024.02.22.581686.full.pdf)
  - Single-neuron models were validated against patch-clamp recordings for only 5 representative neurons — [SoBE 2025](https://arxiv.org/pdf/2510.15745)
- [Oct 2025] *C. elegans* multi-scale closed-loop simulations "reproduce basic behaviors" (locomotion) — [SoBE 2025 site](https://brainemulation.mxschons.com/)

**Mouse**
- [SC25, Nov 2025] Allen Institute, University of Electro-Communications and RIKEN ran a whole mouse cortex on the Fugaku supercomputer: ~9 million multi-compartment biophysical neurons, 26 billion synapses, 86 regions. It was built from the Allen Cell Types Database and Connectivity Atlas with the Brain Modeling ToolKit and run with the Neulite simulator (doi 10.1145/3712285.3759819) — [UEC announcement](https://www.uec.ac.jp/eng/news/announcement/2025/20251118_7309.html); [Cosmic Log](https://cosmiclog.com/2025/11/17/scientists-simulate-the-brain-on-a-supercomputer/)
  - This is a statistical, atlas-based model, not a synaptic connectome. The summaries I found gave no speed relative to real time.

**Human scale**
- [arXiv 2022-2023; reported in *Nature Computational Science*, Dec 2024] Fudan's Digital Twin Brain (Jianfeng Feng): 86 billion spiking neurons and 47.8 trillion synapses on 14,012 GPUs across 3,503 nodes (126 PFLOPS theoretical, 224 TB of GPU memory) — [arXiv 2308.01241](https://arxiv.org/pdf/2308.01241); [arXiv 2211.15963](https://arxiv.org/pdf/2211.15963)
  - It ran 65x, 78.8x and 118.8x slower than real time at mean firing rates of ~7, 15 and 30 Hz.
  - Structure came from MRI, DTI and PET, and parameters were fitted by hierarchical mesoscopic data assimilation. Simulated resting-state BOLD correlated with real BOLD at >0.9, and it was also tested on a visual task.
  - Sources disagree on the venue: [Warwick WRAP](https://wrap.warwick.ac.uk/id/eprint/194522) says *Nature Computational Science*, while Chinese press says *National Science Review*.

**EBRAINS virtual brain twins**
- [Ongoing; preliminary insights Dec 2025] The EPINOV trial tests personalised Virtual Epileptic Patient models (The Virtual Brain) for locating the epileptogenic zone before surgery. Surgery fails in ~40-50% of drug-resistant cases. No efficacy results were published in what I found — [EBRAINS](https://ebrains.eu/news-and-events/2025/epinov-clinical-trial-virtual-brain-technology-to-support-surgery-in-drug); [Summit 2025](https://summit2025.ebrains.eu/news/epinov-clinical-trial-virtual-brain-technology-to-support-surgery-in-drug-resistant-epilepsy)
  - A secondary source gives 356 enrolled patients, unverified — [Cortex Signals](https://cortexsignals.beehiiv.com/p/the-brain-s-infrastructure-era)
  - A separate open dataset of 30 virtual epilepsy patients was published in *PLOS Comp Biol* — [EBRAINS](https://ebrains.eu/news-and-events/2025/thirty-new-personalised-virtual-brain-twins-offer-ground-truth-for-epilepsy)
  - These are region-level (neural-mass) models, not neuron-level.

### Inferences
- Two separate axes get confused in coverage:
  1. Connectome-exact but simplified models (fly LIF, BAAIWorm).
  2. Huge but non-connectome models (Fugaku cortex, DTB).
  None is both connectome-exact and biophysically complete at mammalian scale. DTB has neuron counts at human scale, but its wiring is statistical and it runs ~65-120x slower than real time.
- New since the KB: Eon's embodied fly (2026), FlyGM (2026), BAAIWorm (Dec 2024), Fugaku mouse cortex (Nov 2025), DTB, and EPINOV. The KB's simulation table lists none of them.

### Gaps
- Real-time factors for the Shiu model, the Eon embodiment and the Fugaku run were not found in a primary source.
- No primary Eon paper was found, so its quantitative behavioural-match claims are unverified.

## Why structure alone is not enough; has the 1986 C. elegans connectome yielded a working emulation?

### Takeaway
No. Forty years after the 1986 worm wiring diagram, there is still no emulation that reproduces the worm's full behavioural repertoire from its connectome. The best models (BAAIWorm, 2024) reproduce basic locomotion using many non-connectome measurements. A wiring diagram leaves out the signs and weights of synapses, gap junctions, neuromodulators, intrinsic cell dynamics, plasticity and the brain's current state. Worms also differ from one another a lot, so "the" connectome is not a complete specification.

### Cited Findings
- 40-50% of synaptic connections differ between genetically identical worms — [SoBE 2025 site](https://brainemulation.mxschons.com/)
- The Shiu fly model left out gap junctions, basal activity and neuromodulation beyond excitation/inhibition — [SoBE 2025](https://arxiv.org/pdf/2510.15745)
- No organism has whole-brain recording (≥95% of neurons) at single-neuron resolution. Larval zebrafish reaches ~80% coverage and *C. elegans* ~50%. Calcium imaging samples at 1-30 Hz, and recordings last minutes to hours — [SoBE 2025 site](https://brainemulation.mxschons.com/). Without this data, a model's parameters cannot be checked or fitted.
- BAAIWorm needed ion-channel, morphology, electrophysiology and calcium-imaging data on top of the connectome, and validated only 5 neurons by patch clamp — [PKU NBIC](https://nbic.pku.edu.cn/en/Achievements/d57de79476bf4b279d32e0c285da6405.htm); [SoBE 2025](https://arxiv.org/pdf/2510.15745)
- LICONN is motivated by the fact that EM alone does not capture molecular identity. It "directly incorporates molecular information" into the reconstruction — [ISTA](https://ista.ac.at/en/news/piecing-together-the-brain-puzzle/)
- The owner's KB already lists the missing layers: weights and signs, neuromodulators and gap junctions, learning rules, body and environment, and the momentary potentiation state (`simulation/whole-brain-emulation-projects.md`). The findings above agree with it.

### Inferences
- An "exact replica" of a specific person needs that person's own state: synaptic strengths, receptor and molecular composition, and possibly glia. Current preservation and imaging pipelines are destructive and capture only anatomy. Even complete molecular-annotated imaging (PRISM, LICONN) would not record dynamic variables such as ongoing activity and neuromodulator levels. This is reasoning from the cited gaps, not a sourced claim.
- The worm case is strong evidence that connectome plus simple neurons is not sufficient. The fly results show it is enough to predict some specific circuits.

### Gaps
- I did not find a 2025-2026 quantitative assessment of how much glia or neuromodulator data would be needed for emulation. The SoBE report likely covers this in its computational section (PDF p.68), but the PDF was too large to fetch.

## Expert roadmaps, cost and timeline estimates

### Takeaway
The 2008 Sandberg & Bostrom roadmap put human WBE compute at 10^18 to 10^25 FLOPS for its most plausible detail levels, with a full range of 10^15 to 10^30 or more. The 2025 State of Brain Emulation report (Zanichelli, Schons, Freeman, Shiu, Arkhipov) is the current reference. It finds:
- a full mouse connectome is a decade or more away;
- small organisms (<1M neurons) could be emulated within the decade for low hundreds of millions of dollars;
- the bottleneck has shifted toward recording data and computation.

No credible source gives a date for an exact human replica. Mouse estimates run from about 2029 (E11's optimistic optical target) to the late 2030s (Wellcome's 10-15 years from 2023, plus proofreading).

### Cited Findings
- [2008] Sandberg & Bostrom, FHI Technical Report 2008-3 — [PDF](https://www.futureofhumanityinstitute.org/s/2008-3.pdf)
  - The roadmap's compute range for a human brain is 10^15-10^30 FLOPS — [SoBE 2025](https://arxiv.org/pdf/2510.15745)
  - The workshop's three most plausible levels, each in FLOPS — [AI Impacts](https://aiimpacts.org/brain-performance-in-flops/):

    | Detail level | FLOPS |
    |---|---|
    | Spiking network | 10^18 |
    | Electrophysiology | 10^22 |
    | Metabolome | 10^25 |

- [Oct-Nov 2025] The State of Brain Emulation Report 2025 (arXiv 2510.15745, v3 5 Nov 2025): 175 pages and 45+ expert contributors, organised around neural dynamics, connectomics and computational modelling — [arXiv](https://arxiv.org/abs/2510.15745v3); [summary](https://theconsciousness.ai/posts/state-of-brain-emulation-report-2025-zanichelli/)
  - Mouse has ~500x the neurons of a fly, and human ~1 million times — [SoBE site](https://brainemulation.mxschons.com/)
  - Small organisms (<1M neurons) could plausibly be emulated "within the decade, at a cost in the low $100Ms" — [SoBE site](https://brainemulation.mxschons.com/)
  - "Less than 500 people globally" work on brain emulation, and global basic neuroscience funding is about $0.5B a year — [SoBE site](https://brainemulation.mxschons.com/)
  - A full mouse connectome is a decade or more away. This is a secondary summary — [Envisioning](https://www.envisioning.com/vocab/whole-brain-emulation)
  - The report has a budget "Guesstimator" tool — [SoBE site](https://brainemulation.mxschons.com/)
- Foresight hosted a "State of Brain Emulation in 2025" session at Vision Weekend 2025 — [Foresight](https://foresight.org/?p=3843). Carboncopies runs a journal club that discussed the Shiu model — [Carboncopies](https://carboncopies.org/Events/JournalClubs/MemoryDecoding/2024-12-29/)
- [2023] Wellcome estimated 10-15 years for a mouse, ~100,000 person-years of proofreading, and $7-21B of proofreading cost — [Wellcome](https://wellcome.org/insights/reports/scaling-connectomics); [E11](https://e11.bio/blog/roadmap)
- [2024] E11 Bio targets a mouse connectome in about 5 years at roughly 100x lower cost. This is a company target — [E11](https://e11.bio/blog/roadmap)
- [2026] Eon Systems' reported goal of a mouse emulation within about two years comes from a critical secondary source and is a company aspiration — [Feedbagel](https://feedbagel.com/post/analysis-eon-systems-claims-of-digital-fruit-fly-consciousness-and-brain-emulati)

### Inferences
- **Established (Oct 2026):** a whole adult fly CNS is mapped, and fly and worm emulations reproduce a few behaviours. Mammals are at 1 mm³. Human-scale spiking simulation exists only with statistical wiring, about 100x slower than real time.
- **Plausible but speculative:** a mouse connectome in the 2030s if expansion-microscopy and AI proofreading cost curves hold, and a mouse emulation sometime after that, once recording and parameter inference catch up.
- **Human exact replica:** not feasible today. No published roadmap I found gives a credible date. Several obstacles stack up: an exabyte-scale imaging job, proofreading that now scales at ~$100 or more per neuron (86B neurons implies ~$10^12-10^13 at current zebrafish-level costs; my arithmetic, not a source), molecular and dynamic state that current methods cannot capture, and no method to validate an emulation against a person.

### Gaps
- The full SoBE 2025 PDF (>10 MB) could not be fetched, so its exact mouse and human cost and timeline tables, compute projections and expert-survey numbers are missing. Read PDF p.58 (connectomics) and p.68 (modelling), or the data repository at brainemulation.mxschons.com.
- I did not verify the Sandberg & Bostrom table against the original PDF; the figures come from SoBE 2025 and AI Impacts.
