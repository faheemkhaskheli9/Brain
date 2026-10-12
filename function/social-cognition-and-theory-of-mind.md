---
title: Social cognition and theory of mind
category: function
tags: [theory-of-mind, false-belief, tpj, mpfc, mentalizing, mirror-neurons, imitation, social-learning, pedagogy, inverse-planning, inverse-rl, llm-tom]
use_cases:
  - what is theory of mind and where is it in the brain
  - when do children pass false-belief tasks
  - what do mirror neurons actually explain
  - how do people and animals learn by watching others
  - infer an agent's goal from its behaviour (inverse planning)
  - do large language models have theory of mind
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1016/0010-0277(83)90004-5
  - https://doi.org/10.1016/S1053-8119(03)00230-1
  - https://doi.org/10.1162/jocn.2009.21189
  - https://doi.org/10.1016/j.cognition.2009.07.005
  - https://doi.org/10.1038/s41562-024-01882-z
---

# Social cognition and theory of mind

## Summary
**Theory of mind** (ToM) is attributing beliefs, desires and intentions to others and
using them to predict what they will do. It is tested with **false-belief tasks**,
which children start to pass in the preschool years, and it recruits a consistent
network centred on the **temporo-parietal junction (TPJ)** and **medial prefrontal
cortex (mPFC)**. Mirror neurons are real but what they explain is contested. For AI
the useful idea is that understanding another agent can be cast as **inverting a
model of rational planning**, the same maths as inverse reinforcement learning.

## How it works

### Theory of mind and false belief (established)
- The term comes from Premack & Woodruff (1978), who asked it of chimpanzees.
- **False-belief task** (Wimmer & Perner 1983): Maxi puts chocolate in one cupboard
  and leaves; his mother moves it. Where will Maxi look? Answering "the old place"
  requires representing a belief that differs from reality. The Sally-Anne version
  (Baron-Cohen, Leslie & Frith 1985) found most autistic children in their sample
  failed while children with Down syndrome of lower mental age passed.
- **Development.** A meta-analysis of false-belief studies (Wellman, Cross & Watson
  2001) found that results cluster systematically by age across countries and task
  variants, with most children passing explicit tasks from about age 4: a genuine
  conceptual change, not a task artefact.
- **Earlier, implicit ToM (supported, debated).** Onishi & Baillargeon (2005) reported
  that 15-month-olds look longer when an actor searches where her false belief
  should *not* send her. Replication attempts of related looking-time and
  anticipatory-looking measures have been mixed (Kulke et al. 2018), so whether
  infants represent beliefs or track simpler cues is open.

### The mentalizing network (established)
- Thinking about other people's thoughts reliably activates the **TPJ** (especially
  right), **mPFC**, precuneus and temporal poles (Frith & Frith 2006).
- The right TPJ responds selectively to stories about beliefs compared with stories
  about physical facts or false photographs (Saxe & Kanwisher 2003).
- **Causal evidence:** disrupting right TPJ with TMS made people weigh an agent's
  intentions less and outcomes more in moral judgments, especially for attempted
  harms (Young et al. 2010).

### Mirror neurons (findings established, strong claims contested)
- **Finding:** neurons in macaque ventral premotor area F5 fire both when the monkey
  grasps an object and when it watches someone else grasp it (di Pellegrino et al.
  1992; Gallese et al. 1996). Single-neuron recordings in epilepsy patients found
  cells with mirror properties in supplementary motor area and medial temporal lobe
  (Mukamel et al. 2010).
- **Strong claim (contested):** mirror neurons are the basis of action understanding,
  imitation and, by extension, empathy and language (Rizzolatti & Craighero 2004),
  and their dysfunction causes autism ("broken mirror").
- **Critique:** people can understand actions they cannot perform, and damage to
  motor areas does not reliably abolish action understanding (Hickok 2009). Heyes
  (2010) argues mirror properties are **learned** by associating seeing and doing,
  so they may be a product of social experience rather than its cause.

### Social learning (established, with debated parts)
- **Observational learning:** children who watched an adult hit a Bobo doll copied
  the aggression without being rewarded for it (Bandura, Ross & Ross 1961).
- **Neonatal imitation (contested):** Meltzoff & Moore (1977) reported newborns copy
  facial gestures; a large longitudinal study found no evidence for it (Oostenbroek
  et al. 2016).
- **Over-imitation:** with a transparent puzzle box, chimpanzees skipped actions that
  were visibly useless, while children copied them (Horner & Whiten 2005). Humans
  copy the *method*, not just the goal, which favours faithful cultural transmission.
- **Natural pedagogy (hypothesis, influential):** ostensive cues such as eye contact
  and infant-directed speech tell an infant "this is being taught to you", so it
  learns generalisable knowledge from a single demonstration (Csibra & Gergely 2009).

### Action understanding as inverse planning (supported)
Baker, Saxe & Tenenbaum (2009) model an observer who assumes the other agent plans
approximately rationally towards a goal, then inverts that model with Bayes' rule:
`P(goal | actions) ∝ P(goal) · Π P(action | state, goal)`. In maze experiments this
predicted human goal judgments quantitatively. It is the cognitive-science twin of
**inverse reinforcement learning** (Ng & Russell 2000).

## Relevance to building brain-like AI
- **Learning from demonstrations:** behavioural cloning copies actions; inverse RL
  infers the goal and generalises to new situations. Over-imitation suggests humans
  do some of both, copying methods when causal structure is opaque.
- **Modelling other agents:** an agent that keeps a model of others' goals and
  beliefs can predict them in multi-agent settings. Machine Theory of Mind
  (Rabinowitz et al. 2018) meta-learns such a model, and passes a false-belief test
  in a gridworld.
- **LLM ToM benchmarks (debated):** Kosinski (2024) reported that ChatGPT-4 (June
  2023) solved 75% of a battery of false-belief tasks, on par with 6-year-olds.
  Ullman (2023) showed small changes that keep the logic of the task intact flip
  such successes into failures. Strachan et al. (2024) compared GPT and LLaMA2 with
  1,907 humans: GPT-4 was at or above human level on false belief, indirect
  requests and misdirection, but poor on faux pas, which follow-up tests traced to
  over-cautious answering. Whether passing text tests means ToM, or that the tests
  can be solved without it, is **open**.
- **Teaching signals:** natural pedagogy is a reminder that a teacher who marks
  which example matters gives far more information than a random sample, which is
  the idea behind curricula and RLHF-style feedback.

## Code
Bayesian inverse planning on a 9x9 grid: the agent walks (noisily rationally) to one of
three goals; the observer, seeing only the moves, infers which.

```python
import numpy as np

rng = np.random.default_rng(0)

N = 9
goals = np.array([[0, 8], [8, 8], [8, 0]])
moves = np.array([[0, 1], [0, -1], [1, 0], [-1, 0]])
beta = 2.0                                   # rationality: higher = more reliably efficient

def action_probs(pos, goal):
    """Boltzmann-rational policy: P(a) ∝ exp(-beta * steps left after taking a)."""
    nxt = np.clip(pos + moves, 0, N - 1)
    cost = np.abs(nxt - goal).sum(axis=1)
    p = np.exp(-beta * (cost - cost.min()))
    return p / p.sum()

def walk(goal):
    pos, path = np.array([0, 0]), []
    while (pos != goal).any():
        a = rng.choice(4, p=action_probs(pos, goal))
        path.append((pos.copy(), a))
        pos = np.clip(pos + moves[a], 0, N - 1)
    return path

def posterior_trace(path):
    """Bayes: P(goal | moves so far) ∝ P(goal) * prod_t P(a_t | s_t, goal)."""
    log_post = np.log(np.ones(len(goals)) / len(goals))
    trace = [np.exp(log_post)]
    for pos, a in path:
        log_post += np.log([action_probs(pos, g)[a] for g in goals])
        p = np.exp(log_post - log_post.max())
        trace.append(p / p.sum())
    return trace

correct, early, late = 0, [], []
for _ in range(150):
    g = rng.integers(len(goals))
    trace = posterior_trace(walk(goals[g]))
    correct += trace[-1].argmax() == g
    early.append(trace[2][g])                 # after 2 moves
    late.append(trace[len(trace) // 2][g])     # halfway along the path

print(f"goal inferred correctly at the end: {correct / 150:.2f}")
print(f"mean belief in the true goal: start 0.33, after 2 moves {np.mean(early):.2f}, "
      f"halfway {np.mean(late):.2f}")
assert correct / 150 > 0.95
assert 1 / 3 < np.mean(early) < np.mean(late)
```

Belief in the true goal rises from the uniform prior as moves accumulate. Moves that
fit two goals equally (heading diagonally towards the far corner) leave it ambiguous,
as human observers also find (Baker et al. 2009). Extending the hidden state from
goals to beliefs about where things are gives a toy false-belief observer.

## Open questions
- Whether infants have implicit belief representations, or explicit ToM at age 4 is
  the first real one.
- Whether ToM is a dedicated system (TPJ as a "belief region") or general reasoning
  applied to agents.
- What mirror neurons contribute beyond motor preparation, and whether they are
  innate or learned.
- What LLM success on ToM benchmarks measures, and how to build tests that cannot be
  passed by surface statistics.

## Related
- [[language-and-llms]] - aphasic patients keep theory-of-mind abilities; LLM-brain comparisons.
- [[emotion-amygdala-and-interoception]] - emotion and empathy, the affective side of reading others.
- [[brain-development-and-critical-periods]] - the developmental timetable false-belief passing fits into.
- [[action-selection-and-motor-control]] - the motor system mirror neurons sit in.
- [[learning-and-plasticity]] - reward learning that inverse RL turns around.
- [[innate-priors-and-infant-learning]] - what infants bring to social learning.
- [[prefrontal-cortex-and-abstraction]] - mPFC and abstract representations of others.
- [[decision-making]] - the rational-planning model the observer inverts.

## References
- Premack & Woodruff (1978) "Does the chimpanzee have a theory of mind?", *Behav Brain Sci* 1:515. doi:10.1017/S0140525X00076512
- Wimmer & Perner (1983) "Beliefs about beliefs: representation and constraining function of wrong beliefs in young children's understanding of deception", *Cognition* 13:103. doi:10.1016/0010-0277(83)90004-5
- Baron-Cohen, Leslie & Frith (1985) "Does the autistic child have a 'theory of mind'?", *Cognition* 21:37. doi:10.1016/0010-0277(85)90022-8
- Wellman, Cross & Watson (2001) "Meta-analysis of theory-of-mind development: the truth about false belief", *Child Dev* 72:655. doi:10.1111/1467-8624.00304
- Onishi & Baillargeon (2005) "Do 15-month-old infants understand false beliefs?", *Science* 308:255. doi:10.1126/science.1107621
- Kulke, Reiß, Krist & Rakoczy (2018) "How robust are anticipatory looking measures of Theory of Mind? Replication attempts across the life span", *Cogn Dev* 46:97. doi:10.1016/j.cogdev.2017.09.001
- Frith & Frith (2006) "The neural basis of mentalizing", *Neuron* 50:531. doi:10.1016/j.neuron.2006.05.001
- Saxe & Kanwisher (2003) "People thinking about thinking people: the role of the temporo-parietal junction in 'theory of mind'", *NeuroImage* 19:1835. doi:10.1016/S1053-8119(03)00230-1
- Young, Camprodon, Hauser, Pascual-Leone & Saxe (2010) "Disruption of the right temporoparietal junction with transcranial magnetic stimulation reduces the role of beliefs in moral judgments", *PNAS* 107:6753. doi:10.1073/pnas.0914826107
- di Pellegrino, Fadiga, Fogassi, Gallese & Rizzolatti (1992) "Understanding motor events: a neurophysiological study", *Exp Brain Res* 91:176. doi:10.1007/BF00230027
- Gallese, Fadiga, Fogassi & Rizzolatti (1996) "Action recognition in the premotor cortex", *Brain* 119:593. doi:10.1093/brain/119.2.593
- Rizzolatti & Craighero (2004) "The mirror-neuron system", *Annu Rev Neurosci* 27:169. doi:10.1146/annurev.neuro.27.070203.144230
- Mukamel, Ekstrom, Kaplan, Iacoboni & Fried (2010) "Single-neuron responses in humans during execution and observation of actions", *Curr Biol* 20:750. doi:10.1016/j.cub.2010.02.045
- Hickok (2009) "Eight problems for the mirror neuron theory of action understanding in monkeys and humans", *J Cogn Neurosci* 21:1229. doi:10.1162/jocn.2009.21189
- Heyes (2010) "Where do mirror neurons come from?", *Neurosci Biobehav Rev* 34:575. doi:10.1016/j.neubiorev.2009.11.007
- Bandura, Ross & Ross (1961) "Transmission of aggression through imitation of aggressive models", *J Abnorm Soc Psychol* 63:575. doi:10.1037/h0045925
- Meltzoff & Moore (1977) "Imitation of facial and manual gestures by human neonates", *Science* 198:75. doi:10.1126/science.198.4312.75
- Oostenbroek et al. (2016) "Comprehensive longitudinal study challenges the existence of neonatal imitation in humans", *Curr Biol* 26:1334. doi:10.1016/j.cub.2016.03.047
- Horner & Whiten (2005) "Causal knowledge and imitation/emulation switching in chimpanzees (*Pan troglodytes*) and children (*Homo sapiens*)", *Anim Cogn* 8:164. doi:10.1007/s10071-004-0239-6
- Csibra & Gergely (2009) "Natural pedagogy", *Trends Cogn Sci* 13:148. doi:10.1016/j.tics.2009.01.005
- Baker, Saxe & Tenenbaum (2009) "Action understanding as inverse planning", *Cognition* 113:329. doi:10.1016/j.cognition.2009.07.005
- Ng & Russell (2000) "Algorithms for inverse reinforcement learning", *Proc. ICML 2000*, 663-670.
- Rabinowitz et al. (2018) "Machine theory of mind", *Proc. ICML 2018*. arXiv:1802.07740
- Kosinski (2024) "Evaluating large language models in theory of mind tasks", *PNAS* 121:e2405460121. doi:10.1073/pnas.2405460121
- Ullman (2023) "Large language models fail on trivial alterations to theory-of-mind tasks", arXiv:2302.08399
- Strachan et al. (2024) "Testing theory of mind in large language models and humans", *Nat Hum Behav* 8:1285. doi:10.1038/s41562-024-01882-z
