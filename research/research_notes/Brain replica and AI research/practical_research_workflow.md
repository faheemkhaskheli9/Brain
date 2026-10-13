# Practical workflow: solo, lab-less neuroscience and brain-inspired AI research with Claude (as of October 2026)

Research note, 2026-10-12. Search route: Firecrawl was out of credits (HTTP 402), so these notes come from WebSearch and WebFetch. Several findings rest on search-result summaries rather than full page reads. They are marked "(snippet)" and should be opened before anyone quotes them.

## Tooling: Claude Code features, literature MCP servers, Anthropic guidance, examples

### Takeaway
Claude can now reach PubMed directly (official connector, Oct 2025), and a bioRxiv/medRxiv connector is listed. Claude Code adds subagents, skills and code execution for the analysis side. Anthropic also funds researchers with credits. I found no first-party Anthropic guide written for solo neuroscience researchers.

### Cited Findings
- Anthropic launched "Claude for Life Sciences" on 20 Oct 2025. New connectors: Benchling, BioRender, PubMed, Scholar Gateway (Wiley), Synapse.org and 10x Genomics. Anthropic says PubMed "provides access to millions of biomedical research articles and clinical studies". The launch page does not mention bioRxiv. — [Anthropic](https://www.anthropic.com/news/claude-for-life-sciences)
- The same launch introduced Agent Skills ("folders of instructions, scripts, and resources"). The first scientific skill was `single-cell-rna-qc`, and users can write their own. The page also suggests using Claude Code to "process and analyze genomic data". — [Anthropic](https://www.anthropic.com/news/claude-for-life-sciences)
- The connector directory lists a bioRxiv connector ("Access bioRxiv and medRxiv preprint data") next to PubMed. (snippet) — [claude.com connectors (Benchling page, related connectors)](https://claude.com/marketplace/connectors/benchling)
- Anthropic's AI for Science program started in May 2025. It gives free API credits to high-impact projects, mainly in biology and life sciences, and does not give access to non-public models. — [Claude Help Center](https://support.claude.com/en/articles/11199177-anthropics-ai-for-science-program); [TechCrunch](https://techcrunch.com/2025/05/05/anthropic-launches-a-program-to-support-scientific-research/)
- Reported expansion in Aug 2026: 10,000 free or discounted Claude Team seats for scientists, plus up to $50,000 in credits per project. This comes from secondary coverage and is unverified. — [Natural 20 newsletter](https://natural20.beehiiv.com/p/anthropic-supercharges-claude-for-scientific-discovery)
- Reported Oct 2026: Anthropic committed $150M over three years to put Claude and Claude Code into federal "Genesis Mission" science projects (secondary). — [Runtime Wire](https://runtimewire.com/article/anthropic-150-million-genesis-mission-federal-science)
- Claude Code subagents run in their own context window with their own system prompt, tools and permissions. Built-in types include Explore and Plan, and custom agents are Markdown files in `.claude/agents/`. Anthropic's advice is to use subagents to check details early in a task so the main context stays free. These are secondary descriptions; check them against code.claude.com/docs. — [Inventive HQ](https://inventivehq.com/blog/claude-code-mcp-subagents-skills-hooks); [dev.to](https://dev.to/oikon/enhancing-claude-code-with-mcp-servers-and-subagents-29dd)
- Community literature MCP servers:
  - `openags/paper-search-mcp` searches and downloads from arXiv, PubMed, bioRxiv, medRxiv, Google Scholar, Semantic Scholar and IACR — [mcpservers.org](https://mcpservers.org/en/servers/openags/paper-search-mcp)
  - "Article MCP" covers Europe PMC, arXiv and PubMed — [glama.ai](https://glama.ai/mcp/servers/@gqy20/article-mcp/blob/54a2e89b26091542f1c7c33ca3edc24f4a7cb4ef/CLAUDE.md)
  - These are third-party and unaudited.

### Inferences
- A minimal research stack: the PubMed connector (and bioRxiv if enabled) for literature, a paper-search MCP for arXiv, and Claude Code with a custom read-only "citation-verifier" subagent and a "methods-reviewer" subagent. The repo-specific steps (open-questions register, preregistration in an issue, permutation test) then live in a project skill, so every session follows the same protocol.
- The AI for Science credits favour biology and life-sciences projects. A neuro-data analysis project is a plausible fit and costs nothing to apply for.

### Gaps
- I did not find an official Anthropic guide to using Claude Code for scientific research, or a first-hand blog post by a neuroscientist describing a Claude Code workflow. The search returned only secondary coverage.
- I did not confirm Anthropic's current "Research" (deep research) feature limits or citation behaviour for October 2026.

## Open data a solo researcher can analyse

### Takeaway
Everything listed is free to download except restricted human data. Practical sizes run from about 150 GB (Allen Neuropixels spike files) to petabytes (MICrONS EM, which is meant to be queried in the cloud, not downloaded). Use the official SDKs and query only what you need.

### Cited Findings
- **DANDI**: a public archive of neurophysiology data in NWB format, mirrored on AWS Open Data. Large imaging data is stored as Zarr, and blobs are content-hashed. — [AWS Registry](https://registry.opendata.aws/dandiarchive/)
- **Allen Brain Observatory, Visual Coding Neuropixels**:
  - Session NWB files (spikes, behaviour, stimuli) total 146.5 GB, at 1.7–3.3 GB each. LFP NWB files total 707 GB. These figures come from AllenSDK docs v1.5–v2.2.
  - The recommended access route is `EcephysProjectCache`. The data also sits in the public S3 bucket `allen-brain-observatory` (us-west-2).
  - — [AllenSDK docs](https://allensdk.readthedocs.io/en/stable/_static/examples/nb/ecephys_data_access.html)
- The Allen Observatory NWB files are mirrored on AWS Open Data, DANDI and the Allen data warehouse. — [eLife, de Vries et al. 2023](https://elifesciences.org/articles/85550/figures)
- **MICrONS**:
  - Covers about 1 mm³ of mouse visual cortex, petabytes in total.
  - Reported counts differ: about 82k neurons and 500M synapses in one source, about 200k cells in another.
  - EM and segmentation are read through cloud APIs (CAVE and Python tools), not bulk-downloaded. Functional data is available as NWB on DANDI or through DataJoint.
  - — [MICrONS tutorial, Python tools](https://tutorial.microns-explorer.org/python-tools.html); [Zenodo](https://zenodo.org/records/7741313) (snippet)
- **FlyWire**: the whole adult *Drosophila* brain, 139,255 proofread neurons (Dorkenwald et al., Nature, Oct 2024). Derived tables were distributed through FlyWire Codex, and some older versions can no longer be downloaded from Codex. — [AAU](https://www.aau.edu/newsroom/mapping-entire-fly-brain-step-toward-understanding); [Zenodo/Princeton note](https://zenodo.org/records/14720379) (snippet)
- **IBL Brain-Wide Map**:
  - Neuropixels recordings across the mouse brain. Two sources give different counts: 547 recordings, 32,784 neurons and 194 regions in one, versus 699 insertions and 281 regions in the other. The numbers probably reflect different releases.
  - Access is through the ONE API. Raw ephys is included, and an S3 bucket `ibl-brain-wide-map-public` (us-east-1) can be listed without an AWS account.
  - — [IBL data page](https://www.internationalbrainlab.com/data); [AWS Registry](https://registry.opendata.aws/ibl-autism) (snippet)
- **Human Connectome Project**:
  - Open Access data comes through ConnectomeDB after you register and accept the data use terms (no re-identification, no contact with participants). The HCP notes an IRB may be required.
  - Restricted data needs a separate application. HCP-Lifespan/Development data goes through the NIMH Data Archive, which requires institutional sponsorship. A lone independent researcher realistically gets Open Access tier only.
  - — [HCP Data Use Terms](https://humanconnectome.org/study/hcp-young-adult/data-use-terms); [HCP LS 2.0 access PDF](https://www.humanconnectome.org/storage/app/media/documentation/data_release/LS_Release_2.0_Access_Instructions.pdf)
- Neuromatch Academy keeps a curated guide to beginner-friendly neuron datasets (Steinmetz, Stringer, Allen and others), a good on-ramp. — [Neuromatch](https://instructor.compneuro.neuromatch.io/projects/neurons/README.html)

### Inferences
- For a laptop: Allen Neuropixels spike files (download a few sessions, about 2–3 GB each), DANDI dandisets streamed with remfile/fsspec, FlyWire connectivity tables (MB to GB scale), and MICrONS synapse tables through CAVE queries.
- The "unknown wiring" question in this repo matches FlyWire plus MICrONS functional and structural co-registration directly.
- HCP restricted, NDA and UK Biobank data are effectively closed to someone without an institution.

### Gaps
- No total DANDI size, and no OpenNeuro dataset count for 2026; the searches returned neither.
- I could not confirm whether MICrONS or FlyWire releases newer than 2024–2025 have changed access paths.

## Simulators and tools

### Takeaway
I gathered no new 2025–2026 version or status information on simulators; searches went to the higher-priority questions. Treat the list below as pointers to official docs, not verified current state.

### Cited Findings
- NeuroBench (Yik et al., Nature Communications 16:1545, Feb 2025, doi 10.1038/s41467-025-56739-4):
  - Has an algorithm track with four benchmarks (few-shot continual learning, computer vision, motor cortical decoding, chaotic forecasting) and a system track.
  - Plans a central leaderboard at neurobench.ai.
  - — [DOAJ record](https://doaj.org/article/c4d9e92cc504488f84821bfaf348306a); [Prophesee summary](https://www.prophesee.ai/2025/09/11/the-neurobench-framework-for-benchmarking-neuromorphic-computing-algorithms-and-systems/)

### Inferences
- From prior knowledge, not re-verified here:
  - Brian2 (brian2.readthedocs.io): easiest equation-level spiking models.
  - NEST: large point-neuron networks.
  - NEURON: morphologically detailed cells.
  - GeNN: GPU code generation.
  - snnTorch and Norse: PyTorch surrogate-gradient SNNs, the fastest route to NeuroBench algorithm-track entries.
  - Lava: Intel's neuromorphic framework; actual Loihi hardware needs membership in the Intel Neuromorphic Research Community.
- For a solo researcher, snnTorch or Norse on the NeuroBench harness gives a result that can be measured against a public leaderboard.

### Gaps
- Current versions, Lava/Loihi 3 access terms for independents, and the state of the NeuroBench leaderboard in October 2026 are all unverified.

## Community challenges an outsider can enter

### Takeaway
The best active venues for an outsider with measurable results:
- **BabyLM 2026**: open to anyone; EMNLP 2026 workshop with archival papers; 15 Jul 2026 deadline has passed, so watch for the 2027 call.
- **Algonauts**: 2025 edition closed; papers and code public.
- **Brain-Score**: continuous submissions; last confirmed competition was 2024.
- **NeuroBench**: leaderboard.
- **Carboncopies Brain Emulation Challenge**: synthetic ground-truth benchmark, still forming.
- **Sensorium**: datasets and benchmark remain usable; no 2025 edition found.

### Cited Findings
- **Algonauts 2025**:
  - Task: predict fMRI responses to multimodal movies, with about 65 h of movie-watching per subject for 4 subjects. The final ranking used held-out out-of-distribution films.
  - Sources disagree on how many films were held out (5 or 6).
  - Meta FAIR's TRIBE (video, audio and transcript fused) won among 260+ teams. VIBE came second. MedARC, a volunteer research collective, came fourth: evidence that non-traditional groups can place high.
  - — [Challenge paper arXiv 2501.00504](https://arxiv.org/pdf/2501.00504); [Insights from the winners, arXiv 2508.10784](https://arxiv.org/html/2508.10784); [Scotti substack](https://paulscotti.substack.com/p/insights-from-the-algonauts-2025); [Stacked regression report](https://arxiv.org/pdf/2510.06235)
- **BabyLM 2026**:
  - The 4th competition has a strict track (under 100M words), a strict-small track (under 10M) and a new Multilingual track (English, Dutch, Chinese). Non-competition papers on cognitively plausible training and evaluation are welcome.
  - Submission is through OpenReview, up to 8 pages, double-blind, archival or non-archival.
  - Deadline 15 Jul 2026; workshop at EMNLP 2026 in Budapest.
  - — [arXiv 2602.20092](https://arxiv.org/abs/2602.20092); [ACL portal](https://www.aclweb.org/portal/content/2nd-babylm-workshop)
- **Brain-Score**:
  - The 2024 edition was a *benchmarking* competition: find benchmarks where top models fail. It had a $10k prize pool and a deadline of 30 Jun 2024.
  - The 2022 edition scored models on 30+ neural and behavioural benchmarks.
  - I found no 2026 competition. The platform itself accepts model and benchmark plugin submissions continuously through GitHub.
  - — [CNS list 2024](https://lists.cnsorg.org/hyperkitty/list/comp-neuro@lists.cnsorg.org/thread/4EWUVTDPFVLIN4ZVO2YOTOWXJ3FLT7K6/); [Purdue 2022](https://engineering.purdue.edu/C-BRIC/News/2022-brainscore-competition); [brain-score GitHub](https://www.github.com/brain-score); [docs](https://brain-scoreweb.readthedocs.io/en/latest/)
- **Sensorium**:
  - The 2023 edition (NeurIPS) used 78,853 mouse V1 neurons, each recorded for about 2 h of video, with in-domain and out-of-distribution tracks. It drew 160+ submissions from 22 teams; winners beat the prior state of the art by 50%. A retrospective appeared at NeurIPS 2024.
  - No 2025 edition found.
  - — [arXiv 2407.09100](https://arxiv.org/abs/2407.09100v1); [mlanthology](https://mlanthology.org/neurips/2024/turishcheva2024neurips-retrospective)
- **Brain Emulation Challenge (Carboncopies)**:
  - Synthetic "virtual brains" with known ground truth, used to test system-identification and connectome-to-function methods. Metrics cover structure, behaviour and dynamics.
  - Shown at SfN 2025. Workshop held 21 Feb 2025.
  - Timelines and prizes not found.
  - — [Challenge overview](https://carboncopies.org/Research/BrainGenix/Challenge/Overview/); [Dec 2025 newsletter](https://carboncopies.org/Newsletter/December2025/); [World Wide Neuro](https://world-wide.org/seminar/brain-emulation-challenge-workshop-mv5z71e9a429)
- **NeuroBench**: open benchmark harness and planned leaderboard (see above). — [DOAJ](https://doaj.org/article/c4d9e92cc504488f84821bfaf348306a)

### Inferences
- The Brain Emulation Challenge fits this repo's "unknown wiring" research problem most closely: inferring structure from activity on ground-truth synthetic brains. It is worth contacting Carboncopies directly.
- Brain-Score's *benchmark* submissions (finding where models fail) are a cheap, publishable contribution for an outsider who has data-analysis skill but little compute.

### Gaps
- Algonauts 2026 status, any Brain-Score 2025/2026 competition, Kaggle neuro competitions in 2025–2026, and any Sensorium successor were not found or not searched (out of tool budget).

## Best practices and published guidelines for AI-assisted research

### Takeaway
Funders and publishers agree on four rules: AI cannot be an author, use must be disclosed in the Methods, humans stay accountable, and AI-produced text and citations must be verified. Fabricated citations are a measured and growing problem in 2025–2026, so verifying every reference is mandatory.

### Cited Findings
- **COPE position** (13 Feb 2023): AI tools cannot be authors because they cannot take responsibility. Their use must be disclosed in the Methods or a similar section, and authors stay fully liable. — [COPE](https://publicationethics.org/guidance/cope-position/authorship-and-ai-tools)
- **Nature / Springer Nature**: no LLM authorship, and use is documented in Methods or Acknowledgements (secondary sources only). — [Good Men Project repost](https://goodmenproject.com/?p=883689)
- **EU "Living guidelines on the responsible use of generative AI in research"**:
  - 2nd version, April 2025, an ERA Forum document for researchers, organisations and funders.
  - Rests on the European Code of Conduct for Research Integrity. Flags plagiarism, sensitive-data leakage and bias.
  - — [European Commission](https://research-and-innovation.ec.europa.eu/document/2b6cf7e5-36ac-41cb-aab5-0d32050143dc_en)
- **NIH NOT-OD-25-132** (17 Jul 2025):
  - Applications "substantially developed by AI" are not considered original. There is a cap of 6 applications per PI per calendar year from 25 Sep 2025, introduced after AI-assisted PIs submitted 40+ applications in one round.
  - — [Federal Register 2025-14744](https://www.govinfo.gov/content/pkg/FR-2025-08-05/html/2025-14744.htm); [UIC summary](https://grad.uic.edu/news-stories/nih-limits-ai-use-caps-grant-apps/)
- **Fabricated citations, measured**:
  - An audit of 111M references in 2.5M papers (arXiv, bioRxiv, SSRN, PMC) estimates at least 146,932 hallucinated citations in 2025 alone, rising after mid-2024 alongside AI search and agentic research tools. — [arXiv 2605.07723](https://arxiv.org/pdf/2605.07723)
  - GhostCite: 13 LLMs fabricated 14.2–94.9% of the citations they were asked to generate. 1.07% of AI/ML and security papers contained invalid citations, up 80.9% in 2025. — [arXiv 2602.06718](https://arxiv.org/abs/2602.06718)
  - A reported Lancet study found biomedical papers with fabricated citations rose from 1 in 2,828 (2023) to 1 in 277 (early 2026). This is secondary and the Lancet paper was not opened. — [arXiv 2607.22693](https://arxiv.org/pdf/2607.22693)
- **Agents4Science 2025** (first conference with AI as first authors and reviewers):
  - 315 submissions, 48 accepted. A reference-verification step was needed.
  - Coverage says AI agents struggled to stay focused and to cite accurately.
  - — [Organisers, arXiv 2511.15534](https://arxiv.org/pdf/2511.15534); [Science News](https://www.sciencenews.org/article/science-conference-test-ai-agents)

### Inferences
- Additions to the repo's 7-step protocol:
  1. Resolve every reference through a DOI, PMID or arXiv ID API call before it enters a topic file. Never accept a bare title from a model.
  2. Write an "AI use" Methods paragraph for any preprint: tools, versions, and what the human verified.
  3. Put the preregistration on OSF (timestamped and public), not only in a GitHub issue, when the result will be submitted anywhere.
  4. Pin model versions and seeds, and keep notebooks or scripts that regenerate every number.
- Never upload restricted human data (HCP restricted, NDA) to a cloud LLM. The EU guidelines flag sensitive-data exposure, and HCP terms forbid re-identification attempts.

### Gaps
- I did not fetch OSF preregistration templates or the FORCE11/NeurIPS reproducibility checklists, and found no 2025–2026 empirical study on the quality of AI-written analysis code in neuroscience specifically.

## Publishing as an independent, and citizen science

### Takeaway
arXiv became much harder for independents in January 2026: an institutional email no longer endorses you automatically, so you need a personal endorser or a prior accepted paper. bioRxiv, workshops (BabyLM through OpenReview), Zenodo-archived repos and citizen-science projects (FlyWire, Eyewire II) remain open routes.

### Cited Findings
- **arXiv endorsement**:
  - Mathematics dropped institutional-email auto-endorsement on 10 Dec 2025. All categories followed on 21 Jan 2026.
  - New submitters now need institutional email *plus* prior authorship of an accepted paper in that domain, or a personal endorsement from an established author.
  - CS surveys and position papers need documented prior peer review.
  - Every submission needs a full English version from 1 Feb 2026; machine translation is allowed.
  - — [arXiv blog, Dec 2025](https://blog.arxiv.org/arxiv/2025/12/10/updated-endorsement-policy-for-arxiv-mathematics); [arXiv blog 2026](https://blog.arxiv.org/2026); [CASRAI summary](https://casrai.org/news/arxiv-2026-endorsement-english-ai-policy-changes)
- arXiv is also rate-limiting authors after a flood of AI-generated "slop" submissions. — [Socket](https://socket.dev/blog/arxiv-rate-limiting-slop)
- **BabyLM workshop**: archival 8-page papers through OpenReview, double-blind (no affiliation advantage). — [arXiv 2602.20092](https://arxiv.org/abs/2602.20092)
- **FlyWire**: browser-based collaborative proofreading open to anyone; volunteers proofread and labelled cell types. About 20% of FlyWire community annotations came from the Eyewire community. — [FlyWire join](https://join.flywire.ai); [AAU](https://www.aau.edu/newsroom/mapping-entire-fly-brain-step-toward-understanding); [Nature Methods 2021](https://link.springer.com/article/10.1038/s41592-021-01330-0)
- **Eyewire II** (announced 31 Mar 2025): trace 100,000+ mouse retina neurons. A June 2026 preprint reportedly counts 25k proofread cells (Wikipedia only, unverified). — [Wikipedia](https://en.wikipedia.org/wiki/Eyewire)

### Inferences
- Realistic routes for this repo's owner:
  1. A bioRxiv preprint for neuroscience findings. bioRxiv screens content but does not need an endorser; this comes from prior knowledge and was not re-verified this session.
  2. A workshop paper (BabyLM, NeurIPS/ICLR workshops) to earn the "accepted paper" that later unlocks arXiv.
  3. Brain-Score benchmark or model plugin PRs, which are citable public contributions.
  4. FlyWire or Eyewire proofreading to build standing in the connectomics community, and a possible endorser or collaborator.
  5. Ask an Algonauts or BabyLM author for arXiv endorsement after sharing a working result.

### Gaps
- bioRxiv's 2026 policy on AI-generated or independent-author submissions was not checked.
- I found no first-hand accounts of independent researchers collaborating with labs.

## What the existing guide (guides/research-with-ai.md) lacks

### Takeaway
The guide's 7-step protocol is sound, but it has no concrete tools, data access paths, venues or policy references.

### Cited Findings
- Compared with the cached summary of the guide, it lacks:
  - The PubMed/bioRxiv connectors and literature MCP servers ([Anthropic](https://www.anthropic.com/news/claude-for-life-sciences); [paper-search-mcp](https://mcpservers.org/en/servers/openags/paper-search-mcp)).
  - Dataset access commands and sizes ([AllenSDK](https://allensdk.readthedocs.io/en/stable/_static/examples/nb/ecephys_data_access.html)).
  - Community benchmarks as the "test could have failed" mechanism (Algonauts, Brain-Score, BabyLM, NeuroBench, Brain Emulation Challenge).
  - The January 2026 arXiv endorsement change ([arXiv blog](https://blog.arxiv.org/2026)).
  - COPE/EU disclosure rules ([COPE](https://publicationethics.org/guidance/cope-position/authorship-and-ai-tools); [EU](https://research-and-innovation.ec.europa.eu/document/2b6cf7e5-36ac-41cb-aab5-0d32050143dc_en)).
  - Current citation-fabrication evidence: it cites Walters & Wilder 2023, and newer numbers exist ([GhostCite](https://arxiv.org/abs/2602.06718); [arXiv 2605.07723](https://arxiv.org/pdf/2605.07723)).
  - OSF preregistration: the guide preregisters in GitHub issues only.
  - Citizen science as an on-ramp.

### Inferences
- The highest-value edit is a "Tools and venues" section mapping each step to a tool:
  - step 2 → PubMed connector, plus DOI/PMID resolution
  - step 3 → OSF
  - step 4 → a dataset SDK, plus a benchmark
  - step 7 → bioRxiv, or a workshop, given arXiv endorsement

### Gaps
- I compared against the cached summary, not the full text of the guide.
