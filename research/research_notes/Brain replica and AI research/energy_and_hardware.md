# Matching the brain's power, speed and efficiency in hardware (state as of October 2026)

Scope note: notes compiled 2026-10-12. Items are dated. Items marked "[not re-opened this session]" are well-known papers whose URL/DOI is given from prior knowledge but whose page was not fetched in this research pass; the report writer should treat their exact figures as needing a check. Vendor claims are labelled VENDOR; independent or peer-reviewed measurements are labelled INDEPENDENT/PAPER.

## 1. The brain's energy budget: power, energy per event, sparsity, operations per second

### Takeaway
The brain runs on roughly 20 W, most of it spent on communication (spikes, synaptic transmission, white-matter signalling) rather than "computation"; activity is very sparse (well under ~1% of cortical neurons strongly active at once by Lennie's estimate), and its "operations per second" figure is uncertain by about four orders of magnitude.

### Cited Findings
- Levy & Calvert 2021 (PNAS 118(18): e2008173118, "Communication consumes 35 times more energy than computation in the human cortex, but both costs are needed to predict synapse number"): of 4.94 ATP-watts per cortex, gray-matter communication plus total white-matter costs are 71% (3.52 W); computation is about 2%. — [PMC8106317](https://pmc.ncbi.nlm.nih.gov/articles/PMC8106317)
- The 35:1 communication-to-computation ratio holds only under the assumption that all white-matter costs (including oligodendrocyte/myelination) count as communication. — [PMC8106317](https://pmc.ncbi.nlm.nih.gov/articles/PMC8106317); bioRxiv version: [biorxiv 2021.02.15.431272](https://www.biorxiv.org/content/10.1101/2021.02.15.431272.full.pdf)
- The 2020 preprint of the same work put cortical computation at about 0.17 W of ATP and communication at 4.6 W ("Computation in the human cerebral cortex uses less than 0.2 watts..."). — [bioRxiv 2020.04.23.057927](https://www.biorxiv.org/content/10.1101/2020.04.23.057927.full.pdf)
- Levy & Calvert also argue a neuron's computation costs about 10^8 times more than the thermodynamic best-possible bits per joule. — [PMC8106317](https://pmc.ncbi.nlm.nih.gov/articles/PMC8106317)
- Lennie 2003 ("The Cost of Cortical Computation", Current Biology 13:493-497): the high cost of a single spike "severely limits, possibly to fewer than 1%, the number of neurons that can be substantially active concurrently"; he scales Attwell & Laughlin's budget to human-sized neurons. — [Lennie 2003 PDF](https://www2.bcs.rochester.edu/sites/plennie/pdfs/Lennie03a.pdf)
- Lennie's often-quoted average cortical firing rate of ~0.16 Hz appears in secondary sources only in this search; not confirmed from the primary text here. — [Lennie 2003 PDF](https://www2.bcs.rochester.edu/sites/plennie/pdfs/Lennie03a.pdf) (unverified figure)
- Attwell & Laughlin 2001 (J Cereb Blood Flow Metab 21:1133) built the bottom-up "energy budget for signalling in the grey matter" (rodent): action potentials and postsynaptic (synaptic) currents dominate signalling cost, which is what makes sparse coding pay. [not re-opened this session] — [doi:10.1097/00004647-200110000-00001](https://doi.org/10.1097/00004647-200110000-00001)
- Operations-per-second estimates for the brain span roughly 10^13 to 10^17 FLOP/s with a central estimate near 10^15 (Carlsmith 2020, Open Philanthropy), which shows the uncertainty is about four orders of magnitude. [not re-opened this session] — [Open Philanthropy, Carlsmith 2020](https://www.openphilanthropy.org/research/how-much-computational-power-does-it-take-to-match-the-human-brain/)

### Inferences
- The brain's efficiency is mainly a communication-and-sparsity story, not a "cheap arithmetic" story. This matches the hardware bottleneck in silicon (data movement, Section 6): both systems pay most for moving information, and the brain cuts that bill by sending few spikes over short, local wires.
- Comparing "brain ops/s per watt" with chip TOPS/W is unreliable because the brain number is uncertain by ~10^4 and a synaptic event is not equivalent to a MAC.
- Consistent with the owner's KB (`learning/efficient-brain-like-learning.md` cites ~1% activity from Lennie 2003; `glia-and-energy-budget`): nothing found contradicts it. New detail worth adding: the Levy & Calvert split (computation ~0.1-0.2 W of a ~5 W cortex ATP budget) and the caveat that the 35:1 rests on a white-matter assumption.

### Gaps
- Exact per-spike ATP and per-synaptic-event energy figures (e.g. Attwell & Laughlin's ~10^9 ATP per action potential, later revised down by Alle et al. 2009 and Harris et al. 2012) were not verified in this pass.
- No fresh 2025-2026 review of whole-brain energy budget found in the searches.

## 2. AI energy for comparison: training and inference of frontier models

### Takeaway
A typical text query to a frontier chatbot is now estimated at about 0.2-0.3 Wh (Epoch AI estimate; Google measured median), but long-context and reasoning queries can cost 10-100x more; training energy for frontier models is poorly disclosed and secondary estimates for GPT-4 span 1.75-50 GWh-scale disagreements. Data centres overall used ~415 TWh in 2024.

### Cited Findings
- Epoch AI (7 Feb 2025, ESTIMATE not measurement): ~0.3 Wh per typical GPT-4o text query. Assumptions: ~100B active parameters (MoE, ~200B total), 500 output tokens, ~1e14 FLOP per query, H100 at ~1,500 W including server/datacentre overhead, 10% utilization, average draw 70% of peak. Reasonable alternatives give ~0.1 to 1-4 Wh. — [Epoch AI](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use)
- Same Epoch estimate: 10k input tokens + 500 output ≈ 2.5 Wh; 100k input tokens + 500 output ≈ 40 Wh. Reasoning models likely use more. — [Epoch AI](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use)
- Google (Aug 2025, VENDOR MEASUREMENT of its own fleet): median Gemini Apps text prompt ≈ 0.24 Wh; a narrower accelerator-only figure is ~0.10 Wh. — [Hannah Ritchie, Aug 2025 summary](https://www.sustainabilitybynumbers.com/p/ai-footprint-august-2025); Google's paper: [arXiv 2508.15734](https://arxiv.org/abs/2508.15734) [not re-opened this session]
- Sam Altman (2025) stated an average 0.34 Wh per ChatGPT query, with no published methodology. — [Hannah Ritchie, Aug 2025](https://hannahritchie.substack.com/p/ai-footprint-august-2025)
- A secondary blog estimate puts GPT-5 at ~18 Wh per medium response, up to ~40 Wh with extended reasoning (third-party estimate, low confidence). — [brainpool.ai](https://brainpool.ai/blog/the-energy-and-greenhouse-gas-footprint-of-llm-inference-data-centers-frontier-models-scaling-and-the-road-to-2030)
- GPT-4 training energy: secondary estimates disagree widely, ~1,750 MWh ([patentpc](https://patentpc.com/blog/ai-energy-consumption-how-much-power-ai-models-like-gpt-4-are-using-new-stats)) vs ~50 GWh from ~25,000 A100s for 90-100 days ([RISE blog](https://www.ri.se/en/news/blog/generative-ai-does-not-run-on-thin-air)). No primary disclosure exists.
- 2025 arXiv paper argues the environmental impacts of LM training keep rising and uses Epoch AI's model database as input. — [arXiv 2510.09022](https://arxiv.org/pdf/2510.09022)
- IEA "Energy and AI" (April 2025): data centres used ~415 TWh in 2024 (~1.5% of world electricity), growing ~12%/yr since 2017; projected ~945 TWh by 2030 and ~1,200 TWh by 2035 (Base Case). — [IEA executive summary](https://www.iea.org/reports/energy-and-ai/executive-summary)

### Inferences
- Rough scale comparison: the brain uses 20 W x 3600 s = 72 kJ = 20 Wh per hour. One typical chatbot query (~0.3 Wh) is about 1 minute of whole-brain energy; a 100k-token long-context query (~40 Wh, Epoch) is about 2 hours of brain energy. This compares a whole thinking human against one answer, so it is illustrative only.
- If GPT-4 training was ~50 GWh, that equals ~285,000 years of a 20 W brain (50e9 Wh / 175,200 Wh per year). At ~1.75 GWh it is ~10,000 years. Either way, training a frontier model costs orders of magnitude more energy than a human lifetime of brain energy (~70 years ≈ 12 MWh) — the uncertainty is in the size of the gap, not its existence.
- Per-query inference efficiency improved quickly 2023-2025 (estimates fell from ~3 Wh to ~0.3 Wh, largely from better hardware, MoE and better assumptions), so the gap at inference is narrowing faster than at training.

### Gaps
- No primary training-energy disclosure for any 2025-2026 frontier model was found; Epoch AI's per-model training-power figures were not retrieved.
- No independent measurement of reasoning-model per-query energy found; the 18-40 Wh GPT-5 figure is a third-party estimate.

## 3. Neuromorphic hardware 2024-2026: neurons, synapses, power, benchmarks

### Takeaway
The largest neuromorphic systems now hold 1-2 billion neurons (Hala Point 2024; Darwin Monkey 2025) at kilowatt-scale peak power, i.e. about 1-2% of human neuron count at ~100x the brain's power and with far fewer, simpler synapses. Commercial products in 2024-2026 are sub-milliwatt edge chips (Akida Pico, Innatera Pulsar). Almost all efficiency multipliers (18x, 72.7x, 500x, 15 TOPS/W) are vendor claims; NeuroBench (Nature Communications, Feb 2025) is the main attempt at standard independent comparison.

### Cited Findings
- **Intel Hala Point (announced April 2024)**: 1,152 Loihi 2 chips, 140,544 neuromorphic cores, up to 1.15 billion neurons, 128 billion synapses, MAXIMUM 2,600 W, 20 petaops, up to 15 TOPS/W at INT8 (VENDOR claim); deployed at Sandia; 10x neuron capacity and 12x performance of Pohoiki Springs. — [Intel newsroom](https://newsroom.intel.com/artificial-intelligence/intel-builds-worlds-largest-neuromorphic-system); [AnandTech](https://www.anandtech.com/show/21355/intel-and-sandia-national-laboratories-roll-out-hala-point-neuromorphic-research-system)
- **Loihi 3**: no primary Intel announcement found. A third-party piece syndicated on a Wedbush investor page claims an early-2026 Loihi 3 (8M neurons, 64B synapses per chip, 4 nm) and carries a no-accuracy disclaimer; a Russian-language 2026 piece calls it a rumour; an investor-forum post disputes it. Treat as UNCONFIRMED. — [Wedbush-hosted article](https://investor.wedbush.com/wedbush/article/tokenring-2026-1-19-the-brain-like-revolution-intels-loihi-3-and-the-dawn-of-real-time-neuromorphic-edge-ai); [serverflow.ru](https://serverflow.ru/blog/stati/chto-takoe-intel-loihi-razbiraem-semeystvo-neyromorfnykh-protsessorov-ot-intel); [boersennews forum](https://www.boersennews.de/community/diskussion/brainchip-klassengruppe/75441/down/105104023/)
- **Darwin Monkey / "Wukong" (Zhejiang University, August 2025)**: 960 Darwin 3 chips in 15 blade servers; >2 billion spiking neurons and >100 billion synapses (macaque-scale neuron count); ~2,000 W "under typical operating conditions" per Science and Technology Daily (VENDOR/state media, no independent measurement). — [eWeek](https://www.eweek.com/news/china-darwin-monkey-ai-supercomputer/); [Zhejiang University](https://www.zju.edu.cn/english/2025/0910/c19573a3079424/page.htm); [Gigazine](https://gigazine.net/gsc_news/en/20250829-chinas-darwin-monkey-brain-inspired-supercomputer)
- **SpiNNaker2 / SpiNNcloud**: Sandia system delivered June 2025, ~150-180 million neurons (24 boards x 48 chips, toroidal interconnect); Leipzig University system announced July 2025 with 656,640 cores (~4,320 chips, 152 Arm cores each) simulating at least 650 million neurons. SpiNNcloud claims 18x GPU energy efficiency, and 78x for successor SpiNNext (VENDOR). — [The Next Platform](https://www.nextplatform.com/2025/06/16/sandia-deploys-spinnaker2-neuromorphic-system/); [DCD](https://www.datacenterdynamics.com/en/news/spinncloud-to-deploy-worlds-largest-neuromorphic-supercomputer-at-leipzig-university/)
- **IBM NorthPole (LLM results Sept 2024, IEEE HPEC)**: 16-card 2U research appliance ran a 3B-parameter Granite LLM at 28,356 tokens/s drawing 672 W; IBM reports 72.7x better energy efficiency (tokens/s/W) than a 4 nm GPU in the low-latency regime and 46.9x lower latency than a 5 nm GPU (VENDOR paper; NorthPole is 12 nm; not spiking, it is near-memory digital inference). — [IBM Research blog](https://research.ibm.com/blog/northpole-llm-inference-results); [HPEC 2024 paper PDF](https://modha.org/wp-content/uploads/2024/09/NorthPole_HPEC_LLM_2024.pdf)
- **BrainChip Akida Pico (1 Oct 2024)**: event-based NPU core under 1 mW, intended to wake a host MCU; BrainChip gave no performance benchmarks (VENDOR). — [BrainChip](https://brainchip.com/brainchip-unveils-ai-npu-that-consumes-less-than-a-milliwatt/); [TechSpot](https://www.techspot.com/community/topics/brainchip-unveils-microscopic-npu-that-consumes-less-than-1-milliwatt-of-power.288519/)
- **Innatera Pulsar (21 May 2025)**: "first mass-market neuromorphic microcontroller"; 600 µW for radar presence detection, 400 µW for audio scene classification; claims up to 100x lower latency and 500x lower energy than conventional AI processors (VENDOR). — [insideHPC](https://insidehpc.com/2025/05/innatera-introduces-neuromorphic-microcontroller/); [EE Journal](https://www.eejournal.com/industry_news/innatera-unveils-pulsar-the-worlds-first-mass-market-neuromorphic-microcontroller-for-the-sensor-edge/)
- **NeuroBench (Nature Communications 16:1545, Feb 2025)**: community benchmark framework for neuromorphic algorithms and systems, with hardware-independent and hardware-dependent tracks; argues the field lacked standard benchmarks. Updates at neurobench.ai. — [DOAJ record](https://doaj.org/article/c4d9e92cc504488f84821bfaf348306a); [TU Delft record](https://research.tudelft.nl/en/publications/the-neurobench-framework-for-benchmarking-neuromorphic-computing-/)
- **TrueNorth (2014, older)**: 1M neurons, 256M synapses, ~70 mW per chip. — already in owner KB, citing [Merolla et al. 2014](https://doi.org/10.1126/science.1254642)

### Inferences
- Brain-scale arithmetic: human brain ≈ 86 billion neurons ([organoid review noting the 86B figure](https://arxiv.org/pdf/2604.27933)). Hala Point (1.15B neurons, ≤2.6 kW peak) would need ~75 systems ≈ 195 kW peak to match neuron count, and still has ~1,000x fewer synapses than the brain's commonly quoted ~10^14 (synapse count not verified this pass). Darwin Monkey (2B, ~2 kW typical) would need ~43 systems ≈ 86 kW. Both ~4,000-10,000x the brain's 20 W, before counting synapse deficit and simpler neuron models.
- Darwin Monkey's "typical" 2 kW and Hala Point's "maximum" 2.6 kW are not like-for-like (typical vs peak) and neither is independently measured, so "Darwin Monkey is more efficient" cannot be concluded.
- Where neuromorphic clearly wins now: always-on sensor-edge tasks at hundreds of µW (Pulsar, Akida Pico) and sparse/event workloads. For dense LLM-style inference, the strongest results come from non-spiking near-memory designs (NorthPole), not spiking chips.
- FLAG for owner KB (`simulation/neuromorphic-hardware.md`): newer than the KB's table and not recorded there — Darwin Monkey (2B neurons, Aug 2025), SpiNNaker2 Sandia (June 2025) and Leipzig (650M neurons, July 2025), NorthPole's 2024 LLM result (72.7x, vendor), Innatera Pulsar (May 2025), Akida Pico (Oct 2024), and NeuroBench (Feb 2025). Loihi 3 should NOT be added; no primary source. Nothing found contradicts the KB's Hala Point row (it correctly labels 2,600 W as max and as Intel's figure).

### Gaps
- No independent (non-vendor) power measurement found for Hala Point, Darwin Monkey or SpiNNaker2 systems; no typical-power figure for Hala Point.
- NeuroBench leaderboard numbers (per-task energy, accuracy) were not retrieved in this pass.
- Analog/memristive in-memory computing (e.g. IBM's analog AI chips, 2023-2025 Nature/Nature Electronics papers) was not searched within the tool budget; the KB's "device variability is the hard problem" statement remains the summary.
- SynSense Speck/Xylo 2025-2026 specs not retrieved.

## 4. Biological computing: Cortical Labs CL1, FinalSpark, DishBrain, organoid intelligence

### Takeaway
Biocomputing is commercially available as a research tool (CL1 at $35k or cloud rental; FinalSpark remote organoid platform), but systems hold ~10^4-10^6 neurons, live up to ~6 months, and have demonstrated only simple closed-loop tasks such as Pong; claimed energy advantages ("a million times less") are unmeasured company claims.

### Cited Findings
- **Cortical Labs CL1 (launched March 2025)**: $35,000 per unit, $20,000 each in a 30-unit rack, cloud rental from ~$300/week; first 115 units to ship summer 2025. — [TechRadar](https://www.techradar.com/pro/a-breakthrough-in-computing-cortical-labs-cl1-is-the-first-living-biocomputer-and-costs-almost-the-same-as-apples-best-failure); [TechRadar on rental](https://www.techradar.com/pro/what-a-deal-you-can-now-rent-human-brain-cells-on-a-silicon-chip-for-7-days-for-less-than-a-nintendo-switch-2)
- CL1 official page: neurons kept alive up to 6 months by built-in life support; bi-directional stimulation/read interface; access via "Cortical Cloud"; claims "a fraction of energy other technologies use" but gives NO neuron count and NO power figure. — [corticallabs.com/cl1](https://corticallabs.com/cl1)
- CL1 neuron count is inconsistent across secondary sources: ~800,000 per unit ([liveinthefuture](https://liveinthefuture.org/stories/biocomputing-neurons-for-sale)), ~200,000 in a 2026 review (per search summary), and ~8 x 10^6 in another comparison table ([longtermwiki](https://www.longtermwiki.com/knowledge-base/intelligence-paradigms/biological-organoid)). Unresolved.
- **FinalSpark Neuroplatform (launched May 2024)**: remote-access platform using human brain organoids, up to 4 organoids per MEA, up to 16 organoids on the platform; each organoid ~10,000 neurons, ~0.5 mm thick. Company claims bioprocessors use "a million times less power" than digital processors (VENDOR claim, no measured benchmark). — [ANSA/Business Wire 2024](https://www.ansa.it/sito/notizie/economia/business_wire/2024/05/15/finalspark-launches-the-first-remote-research-platform-using-human-neurons_5fcb882a-72de-4bcb-993d-493194fc30dc.html); [BioAlps](https://bioalps.org/finalsparks-neuroplatform-the-era-of-organic-computing-has-begun/)
- **DishBrain (Kagan et al., Neuron, Oct 2022)**: cultured neurons on an MEA learned to play simplified Pong, improving within ~5 minutes of gameplay. — [arXiv 2604.27933 review](https://arxiv.org/pdf/2604.27933); original paper [doi:10.1016/j.neuron.2022.09.001](https://doi.org/10.1016/j.neuron.2022.09.001) [not re-opened this session]
- A 2026 review notes current organoids contain fewer than 5 million neurons vs ~86 billion in the human brain. — [arXiv 2604.27933](https://arxiv.org/pdf/2604.27933)

### Inferences
- Neuron-level energy is genuinely brain-like (it is biology), but whole-system energy includes incubation, perfusion, temperature control and the electrode/recording electronics, none of which vendors have published; so no system-level efficiency comparison with silicon is possible today.
- Realistic use now: drug screening, disease modelling and basic research on learning in vitro, not general computing. Limits: small scale, finite lifespan (weeks to ~6 months), variability between cultures, low I/O bandwidth through MEAs, and immature training methods. Ethics (organoid intelligence) is an open issue.

### Gaps
- No primary source for CL1 neuron count or electrode count; DishBrain neuron count (~800k often quoted) not verified.
- No measured wall-plug power for a CL1 unit or rack.
- No peer-reviewed demonstration found of organoid/culture systems doing tasks beyond simple closed-loop games or reservoir-style classification.

## 5. Speed: large spiking simulations vs biological real time

### Takeaway
Real-time simulation is solved for ~10^5-neuron point-neuron models on a single GPU and for large point-neuron models on neuromorphic hardware, but detailed biophysical models at mouse-cortex scale (Fugaku, Nov 2025) run far slower than real time; no system yet runs a human-scale detailed model.

### Cited Findings
- Potjans-Diesmann cortical microcircuit (~77,000 neurons, ~3 x 10^8 synapses): NEST on an Intel i9-9900K needed ~62.7 s wall time per biological second; GeNN on a V100 ~2.16 s; NeuronGPU ~1.64 s (2020). — [arXiv 2007.14236](https://arxiv.org/pdf/2007.14236)
- Same microcircuit runs close to real time on a single RTX 2080 Ti (2021). — [Frontiers Comput Neurosci 2021](https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2021.627620/pdf)
- An earlier SpiNNaker (v1) port of the microcircuit ran ~20x slower than real time; later work reached real time on SpiNNaker. — [arXiv 1909.08665 "Real-Time Cortical Simulation on Neuromorphic Hardware"](https://arxiv.org/pdf/1909.08665)
- GeNN vs NEST (Schmitt et al. 2023): simulation time scales linearly with model time and roughly linearly with the number of synapses; real-time factor = T_wall / T_model. — [PMC9950635](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9950635/); [Frontiers Neuroinform 2023](https://www.frontiersin.org/articles/10.3389/fninf.2023.941696/pdf)
- NEST Conference June 2025 abstract: microcircuit on Graphcore IPUs aiming for faster than real time (abstract, no result). — [hifis.net contribution PDF](https://events.hifis.net/event/2047/contributions/16717/contribution.pdf)
- Allen Institute + University of Electro-Communications on Fugaku (SC'25, Nov 2025): whole mouse cortex, ~9-10 million biophysically detailed neurons, 26 billion synapses, 86 regions, using Brain Modeling ToolKit and Neulite. No measured real-time factor was reported in the coverage found. — [UEC release](https://www.uec.ac.jp/eng/news/announcement/2025/20251118_7309.html); [Neuroscience News](https://neurosciencenews.com/supercomputer-cortex-mapping-29938/)
- BrainScaleS (analog) runs neuron dynamics much faster than biological real time (accelerated physics). — owner KB `simulation/neuromorphic-hardware.md` (no new number retrieved this pass)

### Inferences
- Speed depends mainly on synapse count and neuron-model detail: point-neuron models of ~10^5 neurons are a solved real-time problem on one GPU; detailed multi-compartment models at 10^7 neurons need an exascale-class machine (Fugaku, ~400+ PFLOPS peak) and still are not reported as real time.
- Neuromorphic systems (Hala Point, SpiNNaker2, Darwin Monkey) are designed to run at or faster than real time for point-neuron models, but their published capacity figures are neuron counts, not demonstrated brain-like models at that scale.

### Gaps
- Fugaku mouse-cortex real-time factor and power draw were not found (would need the SC'25 paper itself).
- No published real-time factor found for a billion-neuron model on Hala Point or Darwin Monkey.

## 6. Why efficiency is hard on today's hardware, and what event-driven/sparse software recovers

### Takeaway
GPUs spend most energy moving data (weights and activations between memory and compute) on dense, clocked work, whereas the brain stores weights at the synapse and only spends energy when a spike arrives; event-driven and sparse methods recover part of this, but on GPUs the gains are capped because the hardware rewards dense batched work.

### Cited Findings
- Epoch's own per-query estimate assumes only ~10% GPU compute utilization during inference — most of the provisioned hardware is idle, waiting mainly on memory bandwidth, which is the von Neumann cost in practice. — [Epoch AI](https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use)
- IBM attributes NorthPole's 72.7x token/J advantage to intertwining memory and compute on-chip (no off-chip weight traffic); this is a vendor result but shows the size of the memory-movement penalty. — [IBM Research blog](https://research.ibm.com/blog/northpole-llm-inference-results)
- Innatera explains Pulsar's sub-mW budget by computing only when input changes (event-driven). — [insideHPC](https://insidehpc.com/2025/05/innatera-introduces-neuromorphic-microcontroller/)
- In the brain, communication dominates the energy budget (~71% vs ~2% computation per Levy & Calvert), i.e. the brain faces the same "moving information costs most" problem and solves it with sparse spikes and local storage. — [PMC8106317](https://pmc.ncbi.nlm.nih.gov/articles/PMC8106317)
- Owner's KB already measured an event-driven trace update giving ~3.6x fewer operations at 7% activity with weights within 0.015% of the dense result, and notes the saving vanishes if the active set changes every step. — `e:\Projects\Brain\learning\efficient-brain-like-learning.md` (owner's own measurement)

### Inferences
- Software can recover the sparsity win (skip zero activations, event-driven updates, MoE routing, quantization) on any hardware, but the memory-movement win needs hardware with weights stored next to compute (near/in-memory, neuromorphic, analog). Hence the KB's "you need sparse algorithms AND this kind of hardware" is still the right summary.
- What is realistically achievable now (Oct 2026): (a) sub-milliwatt always-on sensing on neuromorphic MCUs; (b) ~10-70x energy gains on specific inference workloads from near-memory chips (vendor figures); (c) 1-2B-neuron point-neuron systems at ~2 kW. What remains open: brain-scale synapse counts (~10^14) at tens of watts, on-chip learning that matches backprop-trained accuracy, standard independent benchmarks (NeuroBench is the start), and a real-time detailed model of even a mouse cortex.

### Gaps
- No independent GPU-vs-neuromorphic head-to-head on an identical task with wall-plug energy found in this pass (NeuroBench results would be the place to look).
- Memory-movement energy figures (pJ per DRAM access vs per MAC, e.g. Horowitz ISSCC 2014) were not re-verified here.
