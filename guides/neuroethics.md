---
title: Neuroethics
category: guides
tags: [neuroethics, moral-status, whole-brain-emulation, organoids, neural-data, neurorights, bci, privacy, dual-use, ai-welfare]
use_cases:
  - is it ethical to simulate a brain, and could a simulation suffer
  - what rules govern brain organoid research
  - who owns neural data from a headset or brain-computer interface
  - what are neurorights and which laws protect brain data
  - what ethical risks come with building brain-like AI
status: draft
last_verified: 2026-10-12
sources:
  - https://doi.org/10.1038/551159a
  - https://doi.org/10.1080/0952813X.2014.895113
  - https://doi.org/10.17226/26078
  - https://www.isscr.org/guidelines
  - https://www.unesco.org/en/ethics-neurotech
---

# Neuroethics

## Summary
Building brain-like systems raises questions that the rest of this KB does not
answer: whether a detailed simulation or a lab-grown piece of brain could have
experiences that matter, who may read and keep data recorded from a person's
brain, and how brain-inspired methods could be misused. Few of these questions
have settled answers, but several now have **rules**: organoid research
guidelines, neural-data privacy laws in Chile and several US states, and a
UNESCO recommendation (2025). This file separates what those rules say (fact)
from the moral arguments behind them (positions, not facts).

## How it works

### Could a simulation matter morally? (open question)
- No test can currently tell whether a system is conscious
  ([[theories-of-consciousness]]). A whole-brain emulation that copied a human
  brain's function would, on functionalist views, have the same experiences as
  the original; on other views (e.g. integrated information theory, which ties
  consciousness to the physical causal structure) it might have none. Which is
  right is **unknown**.
- **Precautionary positions.** Sandberg (2014) proposed treating an emulation as
  if it had the moral status of the system it copies, and treating animal-model
  emulations with the care owed to the animal. Metzinger (2021) argued for a
  moratorium on research that risks creating artificial suffering. Butlin et al.
  (2023) derived "indicator properties" of consciousness from the leading
  theories and found no current AI system has most of them, while finding no
  obvious technical barrier to building one that does. Long, Sebo et al. (2024)
  argued that AI developers should start assessing AI welfare now. These are
  arguments, not findings.
- **What this KB's projects imply.** The simulations here (spiking networks,
  Brain World) are tiny and far from any theory's threshold. The question
  becomes practical only for large, detailed emulations
  ([[whole-brain-emulation-projects]]).

### Brain organoids (rules exist; status open)
- **What they are.** Cerebral organoids are 3D tissues grown from human stem
  cells that form brain-like layers (Lancaster et al. 2013). Some show
  coordinated electrical activity with oscillations (Trujillo et al. 2019).
  Cultured neurons on electrodes have been trained to play a simple game,
  *Pong*, in a closed loop (Kagan et al. 2022); whether this counts as learning
  or "sentience" in any morally relevant sense is disputed.
- **Rules.** The ISSCR Guidelines for Stem Cell Research (2021) allow organoid
  research under ordinary oversight but put transplanting human cells into the
  brains of non-human primates, and similar chimera work, under specialised
  review. A US National Academies report (2021) concluded that current organoids
  are far too simple to be conscious and that new oversight is not yet needed,
  while recommending the question be revisited as they grow more complex.
- **Consent.** Donors of the cells usually consent to research in general, not
  to the growth of brain tissue specifically; Farahany et al. (2018) called for
  consent and oversight frameworks to anticipate this.

### Neural data, privacy and consent (laws exist)
- **Why it is different.** Neural data can reveal information a person has not
  chosen to express. Decoders already reconstruct the gist of heard or imagined
  stories from fMRI (Tang et al. 2023). In that study decoding needed many hours
  of cooperative training data from each person, and a person could defeat it by
  thinking of something else: today's decoders do not read minds without
  consent. That limit is technical, not legal ([[brain-computer-interfaces]]).
- **Neurorights proposals.** Yuste et al. (2017) proposed four priorities:
  privacy and consent, agency and identity, augmentation, and bias. Ienca &
  Andorno (2017) proposed new rights including *mental privacy*, *mental
  integrity* and *cognitive liberty*.
- **Laws and instruments (established, with dates):**
  - **Chile, 2021.** Law 21.383 amended Article 19 of the Constitution to
    protect "brain activity" and the information derived from it. In August
    2023 Chile's Supreme Court ordered the headset maker Emotiv to delete a
    user's neural data that it had kept for research without specific consent.
  - **Colorado, 2024.** HB 24-1058 added biological data, including neural
    data, to the "sensitive data" of the Colorado Privacy Act, the first US
    state law to name neural data.
  - **California, 2024.** SB 1223 added neural data to the sensitive personal
    information covered by the California Consumer Privacy Act.
  - **Montana, 2025.** Neural data was added to the state's genetic information
    privacy law.
  - **OECD, 2019.** The Recommendation on Responsible Innovation in
    Neurotechnology, the first intergovernmental standard in the field.
  - **UNESCO, November 2025.** Member states adopted the Recommendation on the
    Ethics of Neurotechnology at the 43rd General Conference; it is guidance,
    not a binding treaty.
- **Open issue.** Most laws protect raw neural data; whether they cover
  *inferences* drawn from it (mood, attention, intent) is unclear.

### Dual use of brain-inspired AI (argument)
The same methods can serve harmful ends. Neural decoders built for patients who
cannot speak could, if they became less dependent on cooperation, be used for
surveillance or interrogation. Models that predict which stimuli most drive a
brain region can also be used to design maximally engaging or manipulative
content. Urbina et al. (2022) showed in drug discovery how simply flipping a
model's objective turns a beneficial tool into a harmful one; the same logic
applies here. These are **risks to weigh**, not observed harms.

## Relevance to building brain-like AI
| Question | Practical step for a project like this KB's |
|---|---|
| Could the model suffer? | Not for small rate or spiking models; note it as a design review question before scaling an emulation |
| Using open brain recordings | Follow each dataset's licence and consent terms ([[measuring-the-brain-and-open-datasets]]); never try to re-identify participants |
| Collecting neural data (EEG headset, BCI) | Get explicit, specific consent; store and delete per the laws above where they apply |
| Publishing a decoder | State what it needs from the subject (training hours, cooperation) and its failure modes |

## Open questions
- What evidence, if any, could show that a simulation or organoid has
  experiences.
- Whether neurorights need new law or are covered by existing privacy and
  human-rights law (a live dispute among legal scholars).
- How to treat inferences drawn from neural data, not just the raw signal.
- At what level of detail or scale an emulation should come under ethical review.

## Related
- [[theories-of-consciousness]] - the theories that disagree about whether a simulation would feel anything.
- [[whole-brain-emulation-projects]] - the emulations whose moral status is in question.
- [[brain-computer-interfaces]] - where neural data and consent questions arise in practice.
- [[measuring-the-brain-and-open-datasets]] - consent and licence terms of open recordings.

## References
- Sandberg (2014) "Ethics of brain emulations", *J Exp Theor Artif Intell* 26:439. doi:10.1080/0952813X.2014.895113
- Metzinger (2021) "Artificial suffering: an argument for a global moratorium on synthetic phenomenology", *J Artif Intell Conscious* 8:43. doi:10.1142/S270507852150003X
- Butlin et al. (2023) "Consciousness in artificial intelligence: insights from the science of consciousness", arXiv. doi:10.48550/arXiv.2308.08708
- Long, Sebo et al. (2024) "Taking AI welfare seriously", arXiv. doi:10.48550/arXiv.2411.00986
- Lancaster et al. (2013) "Cerebral organoids model human brain development and microcephaly", *Nature* 501:373. doi:10.1038/nature12517
- Trujillo et al. (2019) "Complex oscillatory waves emerging from cortical organoids model early human brain network development", *Cell Stem Cell* 25:558. doi:10.1016/j.stem.2019.08.002
- Kagan et al. (2022) "In vitro neurons learn and exhibit sentience when embodied in a simulated game-world", *Neuron* 110:3952. doi:10.1016/j.neuron.2022.09.001
- ISSCR (2021) Guidelines for Stem Cell Research and Clinical Translation. https://www.isscr.org/guidelines
- National Academies (2021) *The Emerging Field of Human Neural Organoids, Transplants, and Chimeras*. doi:10.17226/26078
- Farahany et al. (2018) "The ethics of experimenting with human brain tissue", *Nature* 556:429. doi:10.1038/d41586-018-04813-x
- Tang, LeBel, Jain & Huth (2023) "Semantic reconstruction of continuous language from non-invasive brain recordings", *Nat Neurosci* 26:858. doi:10.1038/s41593-023-01304-9
- Yuste et al. (2017) "Four ethical priorities for neurotechnologies and AI", *Nature* 551:159. doi:10.1038/551159a
- Ienca & Andorno (2017) "Towards new human rights in the age of neuroscience and neurotechnology", *Life Sci Soc Policy* 13:5. doi:10.1186/s40504-017-0050-1
- Chile, Ley 21.383 (2021), constitutional amendment on neurorights. https://www.bcn.cl/leychile/navegar?idNorma=1166983
- Chile Supreme Court, Girardi v. Emotiv (9 August 2023); summary: https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2024.1330439
- Colorado HB 24-1058 (2024), protection of privacy of biological data. https://leg.colorado.gov/bills/hb24-1058
- California SB 1223 (2024, signed 28 September 2024), consumer privacy: sensitive personal information: neural data. https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202320240SB1223
- KFF Health News (2025) "States pass privacy laws to protect brain data collected by devices" (Colorado, California, Montana). https://kffhealthnews.org/news/article/colorado-california-montana-states-neural-data-privacy-laws-neurorights/
- OECD (2019) Recommendation of the Council on Responsible Innovation in Neurotechnology, OECD/LEGAL/0457. https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0457
- UNESCO (2025) Recommendation on the Ethics of Neurotechnology. https://www.unesco.org/en/ethics-neurotech
- Urbina, Lentzos, Invernizzi & Ekins (2022) "Dual use of artificial-intelligence-powered drug discovery", *Nat Mach Intell* 4:189. doi:10.1038/s42256-022-00465-9
