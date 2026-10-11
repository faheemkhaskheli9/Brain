---
title: Emotion, the amygdala and interoception
category: function
tags: [emotion, amygdala, fear-conditioning, extinction, insula, interoception, value, homeostasis]
use_cases:
  - how does the brain learn to fear something
  - what does the amygdala do besides fear
  - what is interoception and what does the insula do
  - could emotions be predictions of body state
  - give an AI agent drives or emotions grounded in homeostasis
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1146/annurev.neuro.23.1.155
  - https://doi.org/10.1038/nature04490
  - https://doi.org/10.1038/nrn2555
  - https://doi.org/10.1038/nrn3950
  - https://doi.org/10.7554/eLife.04811
---

# Emotion, the amygdala and interoception

## Summary
Fear conditioning in the amygdala is one of the best-mapped learning circuits in
the brain: a tone paired with a shock comes to trigger freezing and a racing heart
through a short chain of nuclei. The amygdala also tags stimuli with positive
value, so it is a value system beside dopamine, not only a fear centre. The insula
maps the state of the body (interoception). A leading **hypothesis** treats
emotions as the brain's predictions of that body state, which ties emotion to
[[predictive-processing]] and gives AI a concrete recipe: reward grounded in
keeping internal variables in range.

## How it works

### Fear conditioning (established)
- **Circuit.** The conditioned stimulus (a tone) reaches the lateral amygdala from
  the auditory thalamus and cortex; the unconditioned stimulus (a shock) converges
  there too. Pairing them potentiates the CS synapses. The central nucleus is the
  output: to the hypothalamus for heart rate and stress hormones, and to the
  periaqueductal grey for freezing (LeDoux 2000).
- **Humans.** Patients with amygdala damage fail to acquire a conditioned skin
  conductance response although they can report the pairing (Bechara et al. 1995,
  see [[brain-structure-overview]]). Patient S.M., with bilateral amygdala
  damage, shows little fear in real threat situations (Feinstein et al. 2011).
- **Extinction is new learning, not forgetting.** Presenting the tone without
  the shock reduces fear, but the original memory survives: fear returns in a new
  context (renewal) or after time (spontaneous recovery) (Bouton 2004). The
  ventromedial prefrontal cortex carries the extinction memory and inhibits the
  amygdala (Milad & Quirk 2002). This is the basis of exposure therapy.
- **The "low road".** A fast subcortical thalamus → amygdala route exists in
  rodents. Whether it lets humans react to threats they never consciously see is
  debated; Pessoa & Adolphs (2010) argue for "many roads" through cortex instead.

### Value beyond dopamine (established)
Amygdala neurons in monkeys encode both positive and negative value of a cue and
flip within trials when the cue's meaning is reversed (Paton et al. 2006). Dopamine
signals the error in predicted reward ([[learning-and-plasticity]]); the amygdala
holds learned value attached to specific stimuli, appetitive as well as aversive,
and passes it to the striatum and orbitofrontal cortex.

### Interoception and the insula (established)
Interoception is sensing the body's internal state: heartbeat, breathing, gut,
temperature, pain. The pathway runs through the brainstem and thalamus to the
posterior insula, and is re-mapped in the anterior insula (Craig 2009). People who
are better at detecting their own heartbeat show more right anterior insula
activity, and report more intense emotions (Critchley et al. 2004).

### Emotion as prediction (hypothesis)
- **Interoceptive inference** (Seth 2013; Barrett & Simmons 2015): the brain
  predicts its body state, as it predicts the senses; the insula compares
  prediction with input. Emotions are those predictions, shaped by context.
  Regulating the body ahead of need is called **allostasis**.
- **Constructed emotion** (Barrett 2017): categories like "fear" are not fixed
  circuits but concepts the brain builds from body signals and context.
- **Somatic markers** (Damasio): body signals bias decisions before a person
  knows why. The Iowa Gambling Task result (Bechara et al. 1997) supported it, but
  Maia & McClelland (2004) showed participants knew more about the decks than
  claimed, so the evidence is contested.

These are frameworks under active test, not settled mechanisms.

## Relevance to building brain-like AI
| Brain | AI component |
|---|---|
| Fast CS→US association in one or few trials | High-learning-rate value tags for dangerous states |
| Extinction as separate, context-gated memory | Keep old associations and learn context-specific overrides, instead of overwriting (helps against forgetting) |
| Amygdala value beside dopamine RPE | Stimulus-value heads alongside a TD critic |
| Interoception and homeostasis | Reward as reduction of drive: distance of internal variables from set points (homeostatic RL, Keramati & Gutkin 2014) |
| Emotion as a global state | One slow variable that changes exploration, learning rate and attention at once ([[neuromodulators]]) |

## Code: extinction is a second, context-gated memory

A Rescorla-Wagner learner (Rescorla & Wagner 1972) has two weights: one for the
tone, and one for the tone in the extinction context. Fear is conditioned in
context A, then extinguished in context B. Because extinction is stored as a
context-specific inhibitor, fear returns when the tone is played back in A
(renewal, Bouton 2004). Learning rates are illustrative.

```python
import numpy as np

w = np.zeros(2)                        # w[0]: tone -> shock, w[1]: tone-in-context-B inhibitor
alpha = 0.3                            # learning rate

def features(context):                 # the tone is present on every trial below
    return np.array([1.0, 1.0 if context == "B" else 0.0])

def fear(context):
    return max(0.0, w @ features(context))

def trial(context, shock):
    global w
    x = features(context)
    w += alpha * (float(shock) - w @ x) * x   # Rescorla-Wagner: delta rule on prediction error

for _ in range(10):
    trial("A", shock=True)             # conditioning in A
after_conditioning = fear("A")

for _ in range(20):
    trial("B", shock=False)            # extinction in B: both weights share the error,
                                       # so w[0] drops part-way and w[1] goes negative
print(f"fear in A after conditioning {after_conditioning:.2f}")
print(f"after extinction in B: fear in B {fear('B'):.2f}, back in A {fear('A'):.2f}")
print(f"weights: tone {w[0]:.2f}, tone-in-B {w[1]:.2f}")

assert after_conditioning > 0.9
assert fear("B") < 0.1                 # extinguished where it was extinguished
assert fear("A") > 0.3                 # renewal: fear returns in the original context
assert w[1] < 0                        # extinction stored as a separate inhibitor
```

## Open questions
- Whether "fear", "anger" and the rest map to dedicated circuits or are built
  case by case.
- How the anterior insula's body map relates to conscious feeling (see the
  consciousness debate, a **hypothesis** area).
- How much the fast subcortical route matters in humans.
- Which internal set points and drives an artificial agent needs to show useful
  emotion-like behaviour.

## Related
- [[neuromodulators]] - noradrenaline and serotonin, which carry much of an emotional state.
- [[predictive-processing]] - interoceptive inference applies the same prediction scheme to the body.
- [[learning-and-plasticity]] - dopamine RPE, the other value signal.
- [[memory-systems]] - emotional memory beside declarative memory.
- [[brain-structure-overview]] - where the amygdala sits, and the lesion evidence.

## References
- LeDoux (2000) "Emotion circuits in the brain", *Annu Rev Neurosci* 23:155. doi:10.1146/annurev.neuro.23.1.155
- Bechara et al. (1995) "Double dissociation of conditioning and declarative knowledge relative to the amygdala and hippocampus in humans", *Science* 269:1115. doi:10.1126/science.7652558
- Feinstein et al. (2011) "The human amygdala and the induction and experience of fear", *Curr Biol* 21:34. doi:10.1016/j.cub.2010.11.042
- Bouton (2004) "Context and behavioral processes in extinction", *Learn Mem* 11:485. doi:10.1101/lm.78804
- Milad & Quirk (2002) "Neurons in medial prefrontal cortex signal memory for fear extinction", *Nature* 420:70. doi:10.1038/nature01138
- Pessoa & Adolphs (2010) "Emotion processing and the amygdala: from a 'low road' to 'many roads' of evaluating biological significance", *Nat Rev Neurosci* 11:773. doi:10.1038/nrn2920
- Paton, Belova, Morrison & Salzman (2006) "The primate amygdala represents the positive and negative value of visual stimuli during learning", *Nature* 439:865. doi:10.1038/nature04490
- Craig (2009) "How do you feel - now? The anterior insula and human awareness", *Nat Rev Neurosci* 10:59. doi:10.1038/nrn2555
- Critchley, Wiens, Rotshtein, Öhman & Dolan (2004) "Neural systems supporting interoceptive awareness", *Nat Neurosci* 7:189. doi:10.1038/nn1176
- Seth (2013) "Interoceptive inference, emotion, and the embodied self", *Trends Cogn Sci* 17:565. doi:10.1016/j.tics.2013.09.007
- Barrett & Simmons (2015) "Interoceptive predictions in the brain", *Nat Rev Neurosci* 16:419. doi:10.1038/nrn3950
- Barrett (2017) "The theory of constructed emotion: an active inference account of interoception and categorization", *Soc Cogn Affect Neurosci* 12:1. doi:10.1093/scan/nsw154
- Bechara, Damasio, Tranel & Damasio (1997) "Deciding advantageously before knowing the advantageous strategy", *Science* 275:1293. doi:10.1126/science.275.5304.1293
- Maia & McClelland (2004) "A reexamination of the evidence for the somatic marker hypothesis", *PNAS* 101:16075. doi:10.1073/pnas.0406910101
- Keramati & Gutkin (2014) "Homeostatic reinforcement learning for integrating reward collection and physiological stability", *eLife* 3:e04811. doi:10.7554/eLife.04811
- Rescorla & Wagner (1972) "A theory of Pavlovian conditioning: variations in the effectiveness of reinforcement and nonreinforcement", in *Classical Conditioning II*, Appleton-Century-Crofts, pp. 64-99.
