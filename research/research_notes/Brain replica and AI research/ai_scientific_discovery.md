# AI-driven scientific discovery and AI "scientist" systems (state as of October 2026)

Scope note: research done 2026-10-12 with about 20 search and fetch calls. Items marked **[company claim]** come from the developer. Items marked **[independent]** come from third parties or peer review. Items marked **[background, not re-fetched]** are well-known facts whose URL was not opened in this session; check them before quoting. Where only a secondary summary was found, it says so.

## 1. Main systems and their verified results

### Takeaway
By 2026 the best-documented results are narrow but real. These include AlphaEvolve's 48-multiplication 4x4 complex matrix algorithm, IMO 2025 gold-level proofs, the Virtual Lab nanobodies with wet-lab binding data, and Co-Scientist and Robin drug-repurposing hits tested in cell or lab assays (Nature, 2026). Each result needed heavy human framing, selection and experimental validation. Fully autonomous "AI scientist" papers (Sakana, Agents4Science) reach at best workshop quality.

### Cited Findings

**Sakana AI Scientist v1 (Aug 2024) and v2 (Apr 2025)**
- [company claim] AI Scientist-v2 uses agentic tree search. Sakana worked with the organizers of the ICLR 2025 "I Can't Believe It's Not Better" workshop. Three fully AI-generated papers were submitted for blind review, and one scored an average of 6.33, above the average acceptance threshold. — [arXiv 2504.08066](https://arxiv.org/pdf/2504.08066)
- [company claim] Sakana itself said none of the three would meet its internal bar for the main ICLR conference track. The accepted paper was withdrawn after review under a pre-agreed protocol. — [The Decoder](https://the-decoder.com/ai-generated-paper-passes-peer-review-before-planned-withdrawal/); [arXiv 2504.08066](https://arxiv.org/pdf/2504.08066)
- A 2026 search result says a Nature study found Sakana's automated reviewer produced scores similar to those of human reviewers. I did not open the Nature paper. — summarized in search results; see [aihola](https://aihola.com/article/ai-scientist-nature-publication) (secondary)

**Google AI co-scientist / "Co-Scientist" (Google DeepMind / Google Research)**
- [peer reviewed, 2026] Gottweis et al., "Accelerating scientific discovery with Co-Scientist", *Nature* 2026, DOI 10.1038/s41586-026-10644-y. It is a multi-agent system with a supervisor, reflection agents and Elo-ranked hypothesis "tournaments". — [Nature](https://www.nature.com/articles/s41586-026-10644-y); [Phys.org / The Conversation, K. Verspoor, 24 May 2026](https://phys.org/news/2026-05-ai-scientists-reveal-fundamental-limits.html)
- For acute myeloid leukemia it selected 30 drug candidates. Oncologists refined the list and 5 were tested in the lab. 3 showed some positive results and 1 looked particularly promising. — [Phys.org](https://phys.org/news/2026-05-ai-scientists-reveal-fundamental-limits.html)
- On 15 expert-curated biomedical goals, blinded independent experts rated its hypotheses higher on novelty and impact. — [Nature](https://www.nature.com/articles/s41586-026-10644-y) (via search summary)
- [background, not re-fetched] The original Feb 2025 preprint (arXiv 2502.18864) reported that Co-Scientist independently proposed the mechanism by which cf-PICIs spread across bacterial species using phage tails. The Penadés lab at Imperial had found this experimentally but had not yet published it. — [arXiv 2502.18864](https://arxiv.org/abs/2502.18864)

**FutureHouse Robin (2025) and Edison Scientific Kosmos (Nov 2025)**
- [peer reviewed, 2026] Ghareeb et al., "A multi-agent system for automating scientific discovery", *Nature* 2026, DOI 10.1038/s41586-026-10652-y. For dry age-related macular degeneration, Robin proposed 30 repurposing candidates. The top 5 were tested and 2 were identified as promising. — [Phys.org](https://phys.org/news/2026-05-ai-scientists-reveal-fundamental-limits.html)
- [company claim] Kosmos technical report (arXiv 2511.02824, Nov 2025): independent scientists checked 102 statements from Kosmos reports. Overall accuracy was about 79%: 85.5% for data-analysis statements, 82.1% for literature statements and only 57.9% for interpretation statements. 3 of the 7 reported "discoveries" reproduced findings human scientists had already made, some of them unpublished. — [arXiv 2511.02824](https://arxiv.org/pdf/2511.02824); [Edison announcement](https://edisonscientific.com/news/announcing-kosmos)

**Stanford / CZ Biohub Virtual Lab (Nature, 2025)**
- [peer reviewed] Swanson, Wu, Bulaong, Pak and Zou, "The Virtual Lab of AI agents designs new SARS-CoV-2 nanobodies", *Nature* (Oct 2025 issue), DOI 10.1038/s41586-025-09442-9 (preprint Nov 2024). An LLM "PI" agent leads specialist agents, with a human giving feedback. The agents built an ESM + AlphaFold-Multimer + Rosetta pipeline that produced 92 nanobodies. Wet-lab tests found two with improved binding to the JN.1 and KP.3 variants that kept binding to the ancestral spike. — [Nature Index page](https://www.nature.com/nature-index/article/10.1038/s41586-025-09442-9)

**Biomni (Stanford)**
- General-purpose biomedical agent, preprint May 2025. — [bioRxiv 2025.05.30.656746](https://www.biorxiv.org/content/10.1101/2025.05.30.656746.full.pdf)
- A secondary source reports later publication in *Science* (DOI 10.1126/science.adz4351). Not verified. — [36Kr](https://eu.36kr.com/en/p/3889073788926470)
- [company claim, Anthropic, Jan 2026] Biomni is Claude-powered. Reported results: a GWAS that took about 20 minutes instead of months; a cloning protocol that matched a postdoc with more than 5 years' experience in a blind evaluation; analysis of 450+ wearable files in 35 minutes against an estimated 3 weeks; and new transcription factors linked to embryonic development, found in more than 336k cells. — [Anthropic, "How scientists are using Claude to accelerate research and discovery", 15 Jan 2026](https://www.anthropic.com/news/accelerating-scientific-research)

**DeepMind AlphaEvolve (May 2025) and AlphaFold**
- AlphaEvolve is a Gemini-powered evolutionary coding agent. It found a 4x4 complex-valued matrix multiplication using 48 scalar multiplications, beating Strassen's 49 (1969) for that setting. The result applies only to complex or real fields as a tensor decomposition, not to every 4x4 case. Humans built rational-coefficient variants within months. — [arXiv 2604.11504 (Lectures on AI for Mathematics)](https://arxiv.org/pdf/2604.11504); [Julia discourse thread](https://discourse.julialang.org/t/new-4x4-algorithm-found/129012); [tianpan.co (secondary)](https://tianpan.co/blog/2026-02-08-alphaevolve-evolutionary-coding-agent-algorithm-discovery)
- [background, not re-fetched] Hassabis and Jumper shared the 2024 Nobel Prize in Chemistry for AlphaFold protein-structure prediction. This is the clearest case of an AI system with a field-changing, independently validated scientific impact. — [nobelprize.org press release](https://www.nobelprize.org/prizes/chemistry/2024/press-release/)

**OpenAI science results**
- [company claim + collaborators] "Early science acceleration experiments with GPT-5", arXiv 2511.16072, 20 Nov 2025. Co-authors include Bubeck, Gowers, Sellke and Weil, with Vanderbilt, Berkeley, Columbia, Oxford, Cambridge, LLNL and Jackson Lab. Case studies cover math, physics, biology, CS, astronomy and materials. Claims include literature synthesis, computation and "novel proofs of unsolved propositions". The paper also documents limitations. — [OpenAI](https://openai.com/index/accelerating-science-gpt-5/); [arXiv 2511.16072](https://arxiv.org/pdf/2511.16072)
- Erdős problems episode (Oct 2025): see section 3.

**IMO 2025 (July 2025)**
- Google DeepMind's advanced Gemini Deep Think and an OpenAI experimental model each scored 35/42, the gold threshold. Both solved problems 1–5 and failed problem 6. Both worked in natural language within 4.5 hours. Gemini was graded through the official IMO process. OpenAI did not officially enter, and its answers were graded by former IMO medalists or judges. — [Simon Willison, 21 Jul 2025](https://simonwillison.net/2025/Jul/21/gemini-imo/); [Maginative](https://www.maginative.com/article/gemini-with-deep-think-achieves-gold-at-international-math-olympiad/); [NYU Shanghai RITS](https://rits.shanghai.nyu.edu/ai/ai-wins-gold-at-2025-international-mathematical-olympiad/)

**Agents4Science 2025 (22 Oct 2025, Stanford, virtual)**
- This was the first conference with AI agents as required first authors and as reviewers. It received 315 submissions; 62 were desk-rejected and 253 reviewed by 3 LLM reviewers each. The top 79 went to human experts, and 48 papers were accepted. An LLM-based fabricated-citation checker was used. — [Organizers' paper, arXiv 2511.15534](https://arxiv.org/pdf/2511.15534); [Science News](https://www.sciencenews.org/article/science-conference-test-ai-agents)
- Coverage framed the outcome as showing fundamental weaknesses: losing focus and citing inaccurate sources. — [SCMP](https://www.scmp.com/news/china/science/article/3331218/why-ai-scientists-fail-impress-human-experts-one-kind-online-conference)

**Periodic Labs and Lila Sciences (autonomous-lab startups)**
- Periodic Labs raised a seed round of more than $300M led by a16z (Sept 2025) and is building a robot-run lab in Menlo Park. Reported talks at about $7.5B in May 2026 (single secondary source). — [etcentric](https://www.etcentric.org/tag/dst); [CB Insights compare](https://www.cbinsights.com/compare/lila-sciences-vs-periodic-labs)
- Lila Sciences (Flagship) launched with a $200M seed and a $235M Series A. A $115M extension including Nvidia in Oct 2025 took its valuation above $1.3B. Its stated goal is "scientific superintelligence" with automated labs. — [Reuters via TradingView](https://de.tradingview.com/news/reuters.com%2C2025%3Anewsml_L6N3VV09K%3A0-ai-lab-lila-sciences-tops-1-3-billion-valuation-with-new-nvidia-backing); [BiopharmaTrend](https://www.biopharmatrend.com/news/lila-sciences-raises-235m-to-build-autonomous-ai-labs-joins-unicorn-ranks-1376/)
- I found no peer-reviewed discovery from either company.

**Other 2026 items**
- A closed-loop system generated and tested hypotheses in yeast with minimal human intervention (*J. R. Soc. Interface*, 2026). Humans kept priorities, interpretation and ethics oversight. — [Phys.org, Sept 2026](https://phys.org/news/2026-09-ai-scientist-autonomously-generates-validates.html) (search snippet only)
- UBC's "new AI scientist conducts its own research" (Mar 2026). — [UBC Science](https://science.ubc.ca/news/2026-03/new-ai-scientist-conducts-its-own-research) (not opened)

### Inferences
- The pattern across validated wins: AI narrows the search space (candidates, hypotheses, algorithms), and humans plus wet labs or formal checkers confirm the result. Verifiable domains (math with checkers, protein binding assays) give the most trustworthy results.
- Repurposing hits at "some positive results in cell lines" are early preclinical signals, not discoveries in the clinical sense.

### Gaps
- I did not open the Nature 2026 Sakana paper, the Sept 2026 *J. R. Soc. Interface* paper or the UBC system.
- I did not confirm whether Biomni's *Science* DOI is real.
- I found no 2026 IMO / AI results.

## 2. Anthropic and Claude for science

### Takeaway
Anthropic's science offering is infrastructure plus case studies: an AI for Science credits program (May 2025), Claude for Life Sciences connectors (Oct 2025), and a Jan 2026 post on three labs. The documented results are speed-ups and candidate generation, with no independently validated discovery attributed to Claude alone.

### Cited Findings
- AI for Science program (May 2025): free API credits for high-impact research, focused on biology and life sciences. — [Anthropic](https://anthropic.com/news/ai-for-science-program)
- Claude for Life Sciences (Oct 2025): connectors to Benchling, PubMed, BioRender, 10x Genomics and others, for literature review, hypothesis generation, analysis and regulatory drafting. Novo Nordisk reported that clinical documentation went from more than 10 weeks to 10 minutes (internal metric, company-reported). — [Anthropic](https://www.anthropic.com/news/claude-for-life-sciences); [Maginative](https://www.maginative.com/article/anthropic-launches-claude-for-life-sciences-with-benchling-pubmed-integration/)
- Jan 2026 case studies [company claim]:
  - Biomni (see section 1).
  - Cheeseman Lab (Whitehead/MIT) built MozzareLLM, which interprets gene clusters from CRISPR knockout imaging screens. It flagged an RNA-modification pathway that other models dismissed as noise.
  - Lundberg Lab (Stanford) uses Claude to pick candidate genes for focused primary-cilia screens. A whole-genome screen is planned as ground truth, and the post's 150/200 vs 80/200 comparison is hypothetical.
  — [Anthropic, 15 Jan 2026](https://www.anthropic.com/news/accelerating-scientific-research)
- One secondary source describes a "Claude Science" beta workspace (30 June 2026) with named early users: Manifold Bio, the Allen Institute and UCSF Brain Tumor Center. Single source, not verified. — [letsdatascience](https://letsdatascience.com/news/anthropic-launches-claude-science-and-drug-program-9ddae733)
- Independent adoption estimate: about 2.1% of scientists with ORCID-linked GitHub profiles used Claude Code as of 15 Feb 2026 (n = 331 users, directional only). — [Republic of Science](https://republicofscience.substack.com/p/how-do-scientists-use-claude-code)

### Inferences
- For this Brain repo, the honest framing is: "Claude is used as a research workflow tool (analysis, literature, candidate selection); validated discoveries still come from human-run experiments."

### Gaps
- I could not confirm the "Claude Science" product from Anthropic's own pages.
- I found no peer-reviewed paper whose central finding is credited to Claude.

## 3. Failures, critiques and overclaims

### Takeaway
Independent checks repeatedly found that autonomous AI scientists fail many experiments, misjudge novelty and hallucinate citations. Headline "discoveries" have been overclaimed: the Erdős episode and the A-Lab novelty correction. Peer review at top ML venues is now letting through fabricated references and AI-written reviews.

### Cited Findings
- **Beel, Kan and Baumgart, "Evaluating Sakana's AI Scientist: Bold Claims, Mixed Results, and a Promising Future?"** arXiv 2502.14297 (v1 20 Feb 2025, v3 15 Oct 2025; SIGIR Forum 2025). This is an independent evaluation. A secondary summary gives these figures: 42% of experiments failed from coding errors, code changed by only about 8% across iterations, the literature review mislabelled established ideas as novel, and a paper cost $6–15 with about 3.5 hours of human involvement. The figures were not checked against the PDF. — [arXiv](https://arxiv.org/abs/2502.14297); [learn.traeai summary](https://learn.traeai.com/t/ai-engineering/phases/15-autonomous-systems/05-ai-scientist-v2)
- External evaluations of Sakana's workshop-accepted paper reported hallucinations, faked results and overstated novelty (secondary). — [aihola](https://aihola.com/article/ai-scientist-nature-publication)
- **Erdős problems (Oct 2025).** Bubeck, Weil and Sellke posted that GPT-5 had "solved" about 10 open Erdős problems. Thomas Bloom of erdosproblems.com said "open" only meant he knew of no solution; GPT-5 had found existing literature. Hassabis called it "embarrassing" and the post was deleted. Sources disagree on whose post was deleted. Commentators, including Terence Tao, noted that literature search is the real value. — [TechCrunch, 19 Oct 2025](https://techcrunch.com/2025/10/19/openais-embarrassing-math/); [The Decoder](https://the-decoder.com/leading-openai-researcher-announced-a-gpt-5-math-breakthrough-that-never-happened/); [Gigazine](https://gigazine.net/gsc_news/en/20251020-openai-researcher-announced-gpt-5-math-breakthrough)
- **A-Lab (Szymanski et al., Nature 2023).** The paper claimed autonomous synthesis of 41 new materials. Critics, including Palgrave and Schoop, disputed the novelty and phase identification [background, not re-fetched]. A secondary tracker says Nature issued an author correction in Jan 2026 that revised the "target novelty" framing and the synthesis accounting, with no retraction. — [kingy.ai tracker (secondary)](https://kingy.ai/mathematics-science-breakthrough-tracker/records/science-correction-2026-a-lab-autonomous-materials/)
- **Hallucinated citations.**
  - NeurIPS 2025: 100 fabricated citations across 53 accepted papers (about 1%), despite 3–5 reviewers per paper. NeurIPS put the system-wide rate at 1.1% and said a bad reference does not necessarily invalidate a paper. — [arXiv 2602.05930](https://arxiv.org/html/2602.05930v1); [Fortune, 21 Jan 2026](https://www.fortune.com/2026/01/21/neurips-ai-conferences-research-papers-hallucinations)
  - ICLR 2026: GPTZero sampled 300 submissions and found more than 50 with serious problems, including fake references, some scored up to 8.0. One analysis claimed 21% of ICLR 2026 reviews were fully AI-generated. GPTZero is a detection vendor, so treat these as estimates. — [Fortune](https://www.fortune.com/2026/01/21/neurips-ai-conferences-research-papers-hallucinations); [hyper.ai](https://hyper.ai/en/stories/f0d643d86b3fb7f93ccd59c5a247ea15)
- **Structural limits (2026 preprints).**
  - "Correct Answer, Wrong Mechanism": AI scientists defend general claims that their own data contradict. — [arXiv 2606.23175](https://arxiv.org/pdf/2606.23175)
  - A benchmarking study of autonomous research systems using multi-model review warns that the field is proliferating faster than evaluation. — [arXiv 2607.28631](https://arxiv.org/pdf/2607.28631)
- **Co-Scientist and Robin critique (independent commentary).**
  - Neither system validates hypotheses physically itself, and both depend heavily on humans for framing and prioritizing.
  - Co-Scientist was not benchmarked against specialized computational drug-repurposing methods.
  - Robin's analysis agent was weak on statistics and bioinformatics.
  — [Verspoor, Phys.org / The Conversation, May 2026](https://phys.org/news/2026-05-ai-scientists-reveal-fundamental-limits.html)
- **Kosmos.** Interpretive statements were only 57.9% accurate, by the company's own evaluation. — [arXiv 2511.02824](https://arxiv.org/pdf/2511.02824)
- **arXiv flood response (31 Oct 2025).** arXiv CS now hosts review, survey and position papers only if they have already been vetted by a journal or conference, citing a flood of LLM-generated content. A Jan 2026 analysis estimates the policy could cut the Computers & Society category by up to 50%, and argues the policy misses most flagged (non-review) papers. — [Decrypt](https://decrypt.co/347196/arxiv-blocks-ai-generated-survey-papers-flood-trashy-submissions); [arXiv 2601.17036](https://arxiv.org/html/2601.17036)

### Inferences
- The most frequent failure is the same throughout: weak novelty and literature judgment. This covers the Sakana novelty mislabels, Erdős "solutions" that were already published, A-Lab "new" materials and fabricated citations. Any AI-generated hypothesis in this repo should get an explicit prior-art check.
- Interpretation is the weakest step, as the Kosmos 57.9% figure and the "wrong mechanism" preprint both show. AI-produced analyses are more trustworthy than AI-produced explanations.

### Gaps
- I did not fetch the Beel PDF, so the 42% and 8% figures rest on secondary summaries.
- I did not locate the primary Palgrave/Schoop critique (PRX Energy, 2024) or Nature's 2026 correction notice.
- I found no systematic reproducibility study of the agent-generated results.

## 4. Neuroscience in particular

### Takeaway
The main neuroscience-specific evidence is BrainBench: LLMs beat neuroscientists at predicting which version of an abstract's result is real. This measures pattern-matching of the literature, not discovery. AI-agent use on open brain datasets is mostly tool-level (Biomni-type analysis). The one brain-related item found is unverified.

### Cited Findings
- Luo et al., "Large language models surpass human experts in predicting neuroscience results", *Nature Human Behaviour* 9(2), Feb 2025 (online Nov 2024). BrainBench pairs real abstracts with versions whose results were altered. LLMs averaged about 81% accuracy against 63% for 171 neuroscience experts (about 10 years' experience on average). BrainGPT, an LLM tuned on the neuroscience literature, reached about 86%. LLM confidence tracked correctness, as it does for experts. — [Univ. Bristol record](https://research-information.bris.ac.uk/en/publications/large-language-models-surpass-human-experts-in-predicting-neurosc/); [News-Medical](https://www.news-medical.net/news/20241127/AI-models-beat-human-experts-in-forecasting-neuroscience-study-results.aspx); [Neuroscience News](https://neurosciencenews.com/ai-llms-neuroscience-data-28154/)
- The Claude for Life Sciences / "Claude Science" materials name a UCSF Brain Tumor Center researcher and an Allen Institute researcher as early users. No results are given, and this is a single secondary source. — [letsdatascience](https://letsdatascience.com/news/anthropic-launches-claude-science-and-drug-program-9ddae733)

### Inferences
- BrainBench shows that LLMs encode the field's statistical regularities, which is useful for prioritizing experiments. The same property means they favour results that fit existing literature, which may disadvantage truly surprising findings. This is a hypothesis, not tested in the sources found.

### Gaps
- I found no source documenting an AI agent autonomously generating and validating a novel neuroscience finding, for example from the Allen Brain Observatory, MICrONS, DANDI or the FlyWire connectome. Searches were not exhaustive.

## 5. Journal and preprint-server policies on AI authorship and use

### Takeaway
Since 2023 the policy is stable: AI cannot be an author, and its use must be disclosed. In 2025, arXiv CS added gatekeeping for review and position papers in response to the LLM flood.

### Cited Findings
- Nature (Jan 2023 editorial, still in force in 2026): no LLM can be credited as an author, because authorship carries accountability. LLM use must be documented in the methods or acknowledgments. — [Nature editorial "Tools such as ChatGPT threaten transparent science" (PDF mirror)](https://med.mahidol.ac.th/ceb/sites/default/files/public/pdf/journal_club/2023/Tools%20such%20as%20ChatGPT%20threaten%20transparent%20science%20here%20are%20our%20ground%20rules%20for%20their%20use.pdf); [Manusights 2026 summary](https://manusights.com/blog/nature-biotechnology-ai-policy)
- arXiv CS (31 Oct 2025): review, survey and position papers require prior peer-review vetting. — [Decrypt](https://decrypt.co/347196/arxiv-blocks-ai-generated-survey-papers-flood-trashy-submissions)
- Agents4Science 2025 was the deliberate exception, requiring AI as first author, which shows the mainstream venues do not allow it. — [arXiv 2511.15534](https://arxiv.org/pdf/2511.15534)
- A bibliometric survey of publisher AI policies shows the majority bar AI authorship and require disclosure. — [arXiv 2307.11918](https://arxiv.org/pdf/2307.11918)

### Inferences
- For any write-up from this repo: list AI tools in the methods or acknowledgments, never as authors, and verify every citation by hand.

### Gaps
- I did not retrieve the *Science* (AAAS) policy or the bioRxiv/medRxiv AI policy pages in this session. [Background, not re-fetched: *Science* journals bar AI authors and AI-generated images without editor permission, and require disclosure. bioRxiv requires disclosure and holds human authors responsible.] Verify at science.org/content/page/science-journals-editorial-policies and biorxiv.org/about/FAQ before quoting.
