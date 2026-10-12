# Paper notes: E. Innate priors and development

Structured notes on the sources cited by hypotheses H081-H092, generated 2026-10-12. Seven were read from local PDFs, five from web full text (arXiv PDFs, a wexler.free.fr PDF, PMC), seven from the abstracts in sources.json, and two (Hensch 2005, Hasson 2020) had no abstract and no reachable full text, so those notes say almost nothing by design.

## Zador 2019: A critique of pure learning and what artificial neural networks can learn from animal brains
- **Cited for:** H081 (the genome stores compact wiring and learning rules, and that bottleneck forces generalisation)
- **Link:** https://doi.org/10.1038/s41467-019-11786-6 · **Basis:** full text
- **Question:** Why do young animals function well with so little training data, and what should ANNs take from that?
- **Method / model:** A perspective, no experiments. It argues that much behaviour is innate, encoded as wiring rules in the genome. The "genomic bottleneck" is the compression of wiring into the genome. Evolution is an outer loop and lifetime learning an inner loop.
- **Experiments:** None. It gives back-of-envelope numbers: the human genome has about 3x10^9 nucleotides (at most about 1 GB). Specifying about 10^14 connections at about 37 bits each needs about 3.7x10^15 bits, so the genome is "at least six orders of magnitude too small". C. elegans has 302 neurons and about 7,000 synapses.
- **Key results:**
  - Examples of innate behaviour: deer-mouse burrowing, looming responses, place-cell scaffolds, face salience.
  - The limited genome "may act as a regularizer or an information bottleneck, shifting the balance from variance to bias".
  - Implications: optimise wiring topology and architecture, and generalise transfer learning.
- **Limitations / caveats:** Conceptual only. The regularisation claim is hedged ("may act as") and untested.
- **Bearing on H081:** partly supports. The compression argument and the capacity numbers are in the paper, but "that bottleneck itself forces generalisation" is stated there as a hypothesis, not a result. The row's phrasing is firmer than the source.
- **Reproduce in this repo:** Train a small net, then compress its weights into a low-parameter rule (for example a shared-kernel or low-rank generator) and compare few-shot transfer to a new task against the uncompressed copy.

## Katz & Shatz 1996: Synaptic activity and the construction of cortical circuits
- **Cited for:** H082 (spontaneous activity such as retinal waves pre-trains sensory maps before birth)
- **Link:** https://doi.org/10.1126/science.274.5290.1133 · **Basis:** abstract only
- **Question:** How does neural activity, spontaneous and sensory-driven, build visual circuits?
- **Method / model:** A review. Spontaneous activity sculpts circuits on the basis of the brain's "best guess" at the initial wiring. With sensory maturation, experience-dependent activity takes over.
- **Experiments:** None of its own. The abstract gives no data.
- **Key results:** The sequential combination of spontaneous and experience-dependent activity lets circuits mature and keep adapting.
- **Limitations / caveats:** I read only the abstract. It does not mention retinal waves by name, and "pre-trains" and "speeds later learning" are the row's analogy.
- **Bearing on H082:** partly supports. The abstract backs activity-dependent pre-sculpting before sensory experience. It does not test any speed-up of later learning.
- **Reproduce in this repo:** Pre-train a small map-forming net on synthetic travelling waves, then train on natural-like patches and compare steps to a fixed loss against no pre-training.

## Newport 1990: Maturational constraints on language learning
- **Cited for:** H083 (starting with limited capacity helps learning, "less is more")
- **Link:** https://doi.org/10.1207/s15516709cog1401_2 · **Basis:** abstract only
- **Question:** Why does language acquisition succeed only with early exposure?
- **Method / model:** A review of first- and second-language acquisition studies. It weighs two hypotheses: maturational decay of language-specific constraints, or decline because nonlinguistic cognitive abilities expand.
- **Experiments:** None of its own. It reviews studies where asymptotic performance falls with age of first exposure, roughly linearly through childhood and flattening in adulthood.
- **Key results:** Late exposure gives lower asymptotic performance, so learning constraints must exist early and weaken with maturation. The second hypothesis (expanding cognitive abilities) is discussed in more detail.
- **Limitations / caveats:** Abstract only. It does not use the phrase "less is more" in the text I read.
- **Bearing on H083:** partly supports. It supplies the developmental evidence and the second hypothesis, which is the "limited resources help" idea. It has no model and tests nothing computational.
- **Reproduce in this repo:** See the Elman 1993 note below. One growing-capacity versus full-capacity comparison covers both citations.

## Elman 1993: Learning and development in neural networks: the importance of starting small
- **Cited for:** H083 (growing capacity beats full capacity)
- **Link:** https://doi.org/10.1016/0010-0277(93)90058-4 · **Basis:** full text (web)
- **Question:** Can a network learn complex grammar if it starts fully formed, or only if it matures?
- **Method / model:** A simple recurrent network is trained to predict the next word in sentences with relative clauses, number agreement and verb-argument structure. Two schemes: incremental input (simple sentences first) and incremental memory (the recurrent feedback is cut every 3-4 words in phase 1, then the window grows to 4-5, 5-6, 6-7 words, then full).
- **Experiments:** Five phases of 10,000 sentences. Input mix: 100% simple, then 75/25, 50/50, 25/75, 0/100 simple/complex, five epochs each. The memory-limited run needed 12 epochs in its first phase. Baseline: the network trained on the full corpus from the start.
- **Key results:**
  - The full-corpus network failed to master the task and stayed in a local error minimum.
  - Incremental input succeeded, with a final error of 0.177.
  - The memory-limited network also succeeded, without staging the data.
  - Analysis: limited memory restricts early learning to simple sentences, which sets up the structure needed later.
- **Limitations / caveats:** One toy grammar, one architecture, a handful of runs. Later replication attempts by others (for example Rohde & Plaut 1999) reported different outcomes. I did not check that here.
- **Bearing on H083:** supports it in this toy setting, and it is the direct source of "starting small". The row's wording matches the abstract.
- **Reproduce in this repo:** Train a small numpy RNN on a toy nested-agreement grammar with a recurrent window schedule (3, 4, 5, 6, 8 steps) versus the full window from step 0. Compare final next-token error over several seeds.

## Spelke & Kinzler 2007: Core knowledge
- **Cited for:** H084 (infants start with core knowledge systems that learning builds on)
- **Link:** https://doi.org/10.1111/j.1467-7687.2007.00569.x · **Basis:** abstract only
- **Question:** What are the innate foundations of human cognition?
- **Method / model:** A review of research on infants, non-human primates, children and adults in diverse cultures.
- **Experiments:** None of its own.
- **Key results:** Four core systems, for representing objects, actions, number and space, and perhaps a fifth for social partners. They have deep roots in phylogeny and ontogeny and shape adult cognition.
- **Limitations / caveats:** The abstract names "actions" where the row says "agents" and lists "geometry" separately. I did not read the body to see how it divides space and geometry.
- **Bearing on H084:** supports the claim. The row's wording of the systems differs slightly from the abstract.
- **Reproduce in this repo:** Give a Brain World agent an object-permanence or agent-detection prior (for example an occlusion-tracking module) and count samples to reach a fixed return against an agent without it.

## Hensch 2005: Critical period plasticity in local cortical circuits
- **Cited for:** H085 (critical periods are a learning-rate schedule: high plasticity early, locked down later)
- **Link:** https://doi.org/10.1038/nrn1787 · **Basis:** abstract only (sources.json holds no abstract, so this is from title and metadata)
- **Question:** What circuit mechanisms open and close critical periods?
- **Method / model:** A review. I could not read it or its abstract.
- **Experiments:** n/a
- **Key results:** None that I verified.
- **Limitations / caveats:** The "learning-rate schedule" framing is the repo's analogy. I cannot say how the review phrases it.
- **Bearing on H085:** does not test it, and I cannot verify support. The review is about critical-period plasticity in cortex, which is the right topic.
- **Reproduce in this repo:** Train a local-rule net with a decaying versus constant learning rate on task A, then a distribution shift. Measure forgetting of A and speed on B.

## Vogelsang et al. 2018: Potential downside of high initial visual acuity
- **Cited for:** H086 (blurry early vision forces learning of large-scale configural features)
- **Link:** https://doi.org/10.1073/pnas.1800901115 · **Basis:** abstract only
- **Question:** Do face-processing deficits after late cataract treatment come from a critical period, or from abnormally high initial acuity?
- **Method / model:** Train a convolutional network with high-resolution images, blurred images, and staged combinations. Examine receptive fields and performance.
- **Experiments:** CNN training only, as far as the abstract says. Architecture and dataset details are not in the abstract.
- **Key results:** Starting with blurred images produced receptive fields that integrate over larger image areas, with better performance and better generalisation across resolutions.
- **Limitations / caveats:** Abstract only. I do not know its sizes, baselines or statistics.
- **Bearing on H086:** supports it. The abstract's "better generalisation across resolutions" is close to the row's "robustness".
- **Reproduce in this repo:** Train a small conv or linear model on a blur-then-sharp schedule versus sharp only, and test on blurred, sharp and mid-resolution inputs.

## Ulyanov et al. 2018: Deep image prior
- **Cited for:** H087 (architecture alone carries strong priors, before any learning)
- **Link:** https://openaccess.thecvf.com/content_cvpr_2018/html/Ulyanov_Deep_Image_Prior_CVPR_2018_paper.html · **Basis:** full text
- **Question:** How much of a conv generator's success comes from its structure rather than from learning on datasets?
- **Method / model:** Fit a randomly initialised hourglass ConvNet (about 2 million parameters) to one degraded image by minimising ||f_theta(z) - x0||^2, with z a fixed noise tensor of 32 maps. Early stopping makes the network's structure act as the regulariser.
- **Experiments:** Denoising (9-image standard set, sigma = 25), 4x super-resolution (Set5, Set14), inpainting (text removal, 50% pixel dropout, large holes), AlexNet inversion and flash/no-flash. Baselines: CBM3D, non-local means, bicubic, SRResNet, convolutional sparse coding.
- **Key results:**
  - Denoising PSNR 29.22 after 1800 steps, 30.43 with averaging and 31.00 over two runs, versus CBM3D 31.42 and non-local means 30.26.
  - Super-resolution PSNR 29.90 (Set5) and 27.00 (Set14), versus bicubic 28.43 and 26.05 and SRResNet 32.10 and 28.53.
  - Fitting natural images is fast while noise is "rejected" (Fig. 2). Deeper nets helped and skip connections hurt inpainting.
- **Limitations / caveats:** Slow (minutes of GPU per image), hyperparameter-sensitive, no semantic inpainting. The prior comes from convolutional structure and the optimisation path, not from any connectome.
- **Bearing on H087:** supports. The authors' own claim is that structure alone gives a strong image prior. It does not test a "connectome-like" net.
- **Reproduce in this repo:** Fit an untrained structured net (local weight-shared kernels) and a dense random net to a noisy 1-D or 2-D signal with early stopping and compare denoising error.

## Gaier & Ha 2019: Weight agnostic neural networks
- **Cited for:** H087 (architecture alone carries priors)
- **Link:** https://arxiv.org/abs/1906.04358 · **Basis:** full text
- **Question:** How far can a topology go without any weight training?
- **Method / model:** A NEAT-style search over topologies. Every connection shares one weight, drawn from U(-2, 2) per rollout. Networks are ranked by mean performance over weights and by complexity.
- **Experiments:** CartPoleSwingUp, BipedalWalker, CarRacing (via a pre-trained VAE) and a downsampled 16x16 MNIST. Baselines are fixed-topology nets under random, shared random, tuned shared and tuned weights.
- **Key results:**
  - Shared-random-weight reward: SwingUp 515 +/- 58 (fixed topology 7 +/- 2), Biped 51 +/- 108 (fixed -107 +/- 12), CarRacing 375 +/- 177 (fixed -85 +/- 27). Tuned shared weight: 723, 261, 608.
  - Fully tuned weights: 932, 332 and 893, near the fixed-topology 918, 347 and 906.
  - MNIST: random weight 82.0 +/- 18.7%, weight ensemble 91.6%, tuned weight 91.9%, trained weights 94.2%.
- **Limitations / caveats:** Individually random weights fail. Success needs a single shared weight and an evolved topology. The structure is searched, not given.
- **Bearing on H087:** supports. Searched architectures work with untrained weights. It says nothing about brain-derived wiring.
- **Reproduce in this repo:** Compare a readout trained on a fixed random recurrent or structured net against a dense random net on one task (same readout, same size).

## Navlakha, Barth & Bar-Joseph 2015: Decreasing-rate pruning optimizes the construction of efficient and robust distributed networks
- **Cited for:** H088 (prune many synapses early at a falling rate for efficient, robust networks)
- **Link:** https://doi.org/10.1371/journal.pcbi.1004347 · **Basis:** full text
- **Question:** What is the rate of synapse pruning in the developing cortex, and does that rate help network construction?
- **Method / model:** Electron microscopy counts in mouse barrel cortex (layer 4, D1 barrel), then simulations of distributed routing networks. The pruning algorithm starts dense, tracks local edge use along source-target paths, and drops low-use edges at a chosen global rate. Compared with growing from a spanning tree and with a fixed no-learning network.
- **Experiments:** 41 animals, 16 time points (P14-P40), 21,355 synapses in 9,754 images. Simulations on node/edge-budget routing problems plus an airline-network application.
- **Key results:**
  - Pruning was fast then slow. The P19-P29 interval pruned 39.99% of synapses versus 10.87% in P29-P39 (P < 0.01).
  - Pruned networks beat growing and no-learning networks on efficiency (shortest-path distance) and robustness (alternative paths).
  - Decreasing rates beat increasing or constant rates (text states about 30% more efficient than increasing rates).
- **Limitations / caveats:** The authors state they do not model neural information processing. Efficiency and robustness are graph-routing measures with a fixed edge budget, not learning performance.
- **Bearing on H088:** partly supports. The falling rate is measured in cortex, and the routing benefit is shown in a graph model. "Efficient and robust networks" in the row means routing networks here. Transfer to a local-rule learning net is untested.
- **Reproduce in this repo:** Train a Hebbian net from a dense start and prune at a constant, rising or falling rate to the same sparsity. Compare accuracy after random unit or synapse damage.

## Smith & Gasser 2005: The development of embodied cognition: six lessons from babies
- **Cited for:** H089 (infants build their own curriculum from what they see and handle)
- **Link:** https://doi.org/10.1162/1064546053278973 · **Basis:** abstract only
- **Question:** What do developmental findings imply for building embodied intelligent agents?
- **Method / model:** A position paper. It offers six lessons, resting on the embodiment hypothesis that intelligence arises from sensorimotor interaction with an environment.
- **Experiments:** None in the abstract.
- **Key results:** Argues that starting as a baby grounded in a physical, social and linguistic world is crucial for flexible intelligence.
- **Limitations / caveats:** I did not read the six lessons, so I cannot confirm they include self-generated curricula.
- **Bearing on H089:** partly supports (embodiment as a developmental driver). I could not verify the "self-made curriculum" wording.
- **Reproduce in this repo:** n/a (T2).

## Orhan, Gupta & Lake 2020: Self-supervised learning through the eyes of a child
- **Cited for:** H089 (egocentric child data supports useful category learning)
- **Link:** https://doi.org/10.48550/arxiv.2007.16189 · **Basis:** full text (web)
- **Question:** How much early visual knowledge can generic self-supervised learning extract from a child's headcam video?
- **Method / model:** Train MobileNetV2 with temporal classification (frames in a time segment share a class, after temporal invariance, Foldiak 1991 and Wiskott & Sejnowski), and image-based and temporal MoCo-v2. Evaluate frozen features with linear readouts.
- **Experiments:** SAYCam headcam video of three children: 150-200 hours per child, sampled from 6 to 32 months. Evaluation on a curated labelled subset of child S and on Toybox. Baselines: an ImageNet-trained net, a random untrained net, HOG.
- **Key results:**
  - Temporal-classification models gave high linear accuracy on labelled S and Toybox, and sometimes beat the ImageNet-trained baseline.
  - Models trained on children A and Y generalised to child S's labelled data.
  - ImageNet linear top-1: 20.9% (TC-S), 18.1% (TC-A), 17.6% (TC-Y), 16.4% (MoCo-V2-S), close to 25% for all three children, versus 1.2% for a random net.
- **Limitations / caveats:** The authors list: the videos are about one week of visual experience; video only, so the embodied and haptic aspects are ignored; no language; the best models need unrealistic colour-distortion augmentations.
- **Bearing on H089:** partly supports (useful categories emerge from headcam data), but it does not test self-made curricula. It has no comparison with non-egocentric data and it explicitly leaves out the embodied part.
- **Reproduce in this repo:** n/a (T2).

## Hasson, Nastase & Goldstein 2020: Direct fit to nature
- **Cited for:** H090 (no special algorithm: the brain "direct-fits" a huge over-parameterised model to dense embodied data)
- **Link:** https://doi.org/10.1016/j.neuron.2019.12.002 · **Basis:** abstract only (sources.json holds no abstract, so this is from title and metadata)
- **Question:** I could not read the paper. The title ("Direct fit to nature: an evolutionary perspective on biological and artificial neural networks") names the thesis.
- **Method / model:** A perspective paper. Nothing further verified.
- **Experiments:** n/a
- **Key results:** None verified.
- **Limitations / caveats:** I made no claim about its argument beyond the title.
- **Bearing on H090:** cannot verify. The row's wording follows the title, but the matched-data BabyLM test is the repo's, not the paper's.
- **Reproduce in this repo:** n/a (T2).

## Confavreux et al. 2020: A meta-learning approach to (re)discover plasticity rules that carve a desired function into a neural network
- **Cited for:** H091 (evolution as the outer loop meta-learned plasticity rules)
- **Link:** https://doi.org/10.1101/2020.10.24.353409 · **Basis:** abstract only
- **Question:** Can plasticity rules be found by their function instead of by fitting data?
- **Method / model:** Parameterise rules by a Volterra expansion. Use gradient descent or evolutionary strategies to minimise a loss on how well a rule turns a random network into one with the target function.
- **Experiments:** Rediscover Oja's rule at the single-neuron level. A two-layer firing-rate network must recover several principal components (Oja plus anti-Hebbian). Integrate-and-fire networks with plastic inhibitory afferents hit a target rate.
- **Key results:** It rediscovers Oja and finds a subset of rules that solve the inhibitory task.
- **Limitations / caveats:** A proof of principle. Abstract only, so no numbers read.
- **Bearing on H091:** partly supports as an engineering analogy (meta-learned rules). It meta-learns with gradients or ES, so it does not show that evolution did this.
- **Reproduce in this repo:** Evolve the coefficients of a parametrised rule in Brain World, and compare against fixed Hebb and Oja rules.

## Najarro & Risi 2020: Meta-learning through Hebbian plasticity in random networks
- **Cited for:** H091 (evolved plasticity rules)
- **Link:** https://doi.org/10.48550/arxiv.2007.02686 · **Basis:** full text (web)
- **Question:** Can an agent with random weights and evolved Hebbian rules learn its policy during its lifetime?
- **Method / model:** Per-synapse ABCD rule: dw_ij = eta_ij (A_ij o_i o_j + B_ij o_i + C_ij o_j + D_ij). Weights start random (U[-0.1, 0.1]). Evolution strategies search the rule coefficients.
- **Experiments:** CarRacing-v0 (92,690 weights, 456,640 Hebbian coefficients) and a PyBullet Ant quadruped (12,288 synapses, 61,440 coefficients), including damaged legs. Static-weight baselines trained with the same ES.
- **Key results:**
  - CarRacing reward 872 +/- 11 for Hebbian versus 711 +/- 16 for static weights.
  - Quadruped, unseen left-leg damage: Hebbian 452 +/- 95 (solved) versus static 68 +/- 56 (failed). On seen morphologies static weights travelled farther (for example 1604 versus 1051).
  - The weights converge within about 30 to 80 Hebbian updates.
- **Limitations / caveats:** The Hebbian solutions generalise to the unseen damage with high variance. The appendix ablates restricted ABCD forms, but there is no baseline against a fixed Hebb or Oja rule.
- **Bearing on H091:** partly supports. It is a working evolved-rule outer loop, but its baselines are static weights. It does not test the falsifier (evolved rules versus plain Hebb or Oja).
- **Reproduce in this repo:** A small ES over ABCD coefficients versus fixed Hebb and Oja on a toy adaptive-control task with a sudden change.

## Miconi, Stanley & Clune 2018: Differentiable plasticity
- **Cited for:** H092 (each synapse has a learnable plasticity coefficient)
- **Link:** https://proceedings.mlr.press/v80/miconi18a.html · **Basis:** full text
- **Question:** Can plasticity be optimised by gradient descent in large recurrent networks?
- **Method / model:** x_j(t) = tanh(sum_i [w_ij + alpha_ij Hebb_ij(t)] x_i(t-1)), with Hebb_ij(t+1) = eta x_i(t-1) x_j(t) + (1-eta) Hebb_ij(t). The w and alpha are trained between lifetimes by backprop. Hebbian traces exist only within a lifetime.
- **Experiments:** Memorising and completing sets of novel binary or natural images, with 2,004,002 trainable parameters for 1,000-pixel patterns and 2,101,250 for CIFAR images. Omniglot 5-way 1-shot, where plasticity adds 320 parameters over 111,426. A maze task trained with A2C, 15 runs per condition.
- **Key results:**
  - Plastic networks (51 neurons) solved the pattern task where non-plastic RNNs and LSTMs with 2,050 neurons failed or solved it imperfectly.
  - Omniglot: competitive with published meta-learners.
  - Per-connection alpha beat a shared alpha, and shared alpha plateaued low in the maze.
- **Limitations / caveats:** alpha is fixed within a lifetime and changes only across lifetimes, so the plasticity is tuned, not plastic during life.
- **Bearing on H092:** supports the per-synapse coefficient part and the "plastic versus fixed" comparison. "Plasticity itself is plastic" slightly overstates it.
- **Reproduce in this repo:** A small recurrent net with w + alpha*Hebb, with learned alpha versus a shared alpha versus fixed Hebb, on a memorise-new-patterns task.

## Miconi et al. 2019: Backpropamine
- **Cited for:** H092 (plasticity under learned control)
- **Link:** https://arxiv.org/abs/2002.10585 · **Basis:** full text
- **Question:** Can neuromodulated plasticity, where the network controls its own learning rate, be trained by gradient descent?
- **Method / model:** The intra-lifetime rate eta is replaced by a network-computed neuromodulatory signal M(t) (simple), or by a retroactive version using eligibility traces.
- **Experiments:** Cue-reward and maze tasks, plus Penn Treebank language modelling with LSTMs at fixed parameter count (about 4.8 million parameters, and a 24.2 million-parameter model).
- **Key results:**
  - PTB test perplexity: baseline LSTM 104.26 +/- 0.22, with differentiable plasticity 103.80 +/- 0.25, simple neuromodulation 102.48 +/- 0.28, and about 1.7 better than baseline for retroactive.
  - The larger model used per-neuron rather than per-connection plasticity coefficients.
- **Limitations / caveats:** Small gains on language modelling.
- **Bearing on H092:** supports, and it is closer to "plasticity that is itself dynamic" than the 2018 paper. The row cites it for the same idea as 2018, but it adds neuromodulation.
- **Reproduce in this repo:** See the 2018 entry, with an added learned M(t) gate.

## Corrections to the hypotheses file
- H081: soften "That bottleneck itself forces generalisation" to "may act as a regulariser" (Zador's wording).
- H083: Newport 1990's abstract gives the maturational and cognitive-expansion hypotheses, not a model. Elman 1993 is the main source of "starting small".
- H084: the abstract of Spelke & Kinzler lists objects, actions, number and space, with social partners as a possible fifth. Check "agents" and "geometry" against the full text.
- H085, H090: sources.json has no abstract for Hensch 2005 or Hasson 2020, so neither could be checked here.
- H088: Navlakha et al. test pruning rates in routing networks, so say "routing-network efficiency and robustness".
- H089: Orhan et al. do not test self-selected curricula, and SAYCam is video only. Smith & Gasser is a position paper.
- H091: Confavreux and Najarro are meta-learning methods, not evidence about evolution. Najarro compares with static weights, not Hebb or Oja.
- H092: in Miconi 2018 alpha is fixed within a lifetime. "Plasticity itself is plastic" fits Backpropamine's M(t) better.
