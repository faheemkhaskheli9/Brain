---
title: What brain disorders teach (Parkinson's, Alzheimer's, epilepsy, computational psychiatry)
category: function
tags: [parkinsons, dopamine, deep-brain-stimulation, alzheimers, hippocampus, epilepsy, excitation-inhibition, split-brain, schizophrenia, autism, precision, depression, addiction, computational-psychiatry, reinforcement-learning]
use_cases:
  - what do brain disorders reveal about how the healthy brain works
  - how does dopamine loss in Parkinson's disease change learning and action
  - what is computational psychiatry
  - are schizophrenia and autism explained by altered prediction or precision
  - model depression or addiction as a reinforcement learning problem
status: draft
last_verified: 2026-10-11
sources:
  - https://doi.org/10.1016/S0896-6273(03)00568-3
  - https://doi.org/10.1007/BF00308809
  - https://doi.org/10.1111/epi.12550
  - https://doi.org/10.1016/j.tics.2011.11.018
  - https://doi.org/10.1038/nn.4238
  - https://doi.org/10.1016/j.biopsych.2018.05.015
---

# What brain disorders teach (Parkinson's, Alzheimer's, epilepsy, computational psychiatry)

> **Not medical advice.** This file explains what disorders reveal about brain
> function and how they are modelled computationally. It is not a guide to
> diagnosis, treatment or medication. Anyone with symptoms or questions about care
> should see a qualified clinician.

## Summary
Disorders are the brain's natural experiments: when one system fails, what is lost
shows what it did. **Parkinson's disease** removes dopamine and shows its role in
starting actions and learning from reward. **Alzheimer's disease** starts in the
hippocampal region and shows how new memories depend on it while old ones do not.
**Epilepsy** shows what happens when excitation escapes inhibition, and its surgery
gave us the split brain. **Computational psychiatry** goes further and writes
psychiatric conditions as changes to the parameters of learning and inference
models; most of those mappings are still **hypotheses**.

## How it works

### Parkinson's disease: dopamine, action and learning
- **Established:** the motor signs (slowness of movement, rigidity, resting tremor)
  follow the loss of dopamine neurons in the substantia nigra pars compacta, which
  supply the striatum (Dauer & Przedborski 2003). In the basal ganglia model this
  tips the balance from the direct "Go" pathway to the indirect "NoGo" pathway
  ([[action-selection-and-motor-control]]).
- **Supported:** dopamine also teaches. Patients off medication learned better from
  negative outcomes and on medication better from positive ones, as a Go/NoGo model
  with dopamine prediction errors predicts (Frank, Seeberger & O'Reilly 2004).
- **Established:** high-frequency **deep brain stimulation (DBS)** of the
  subthalamic nucleus improves motor symptoms in advanced disease (Limousin et al.
  1998), and in a randomised trial improved quality of life more than medication
  alone (Deuschl et al. 2006). *How* DBS works (blocking, jamming or retuning
  pathological activity) is still an **open question**.

### Alzheimer's disease: hippocampus first
- **Established:** neurofibrillary tangles appear first in the transentorhinal and
  entorhinal region, then the hippocampus, and only later across neocortex (Braak &
  Braak 1991). This matches the early symptom: trouble forming new episodic memories.
- **Established lesion evidence:** removing both medial temporal lobes left patient
  H.M. unable to form new long-term memories (Scoville & Milner 1957). Damage of
  this kind spares older memories more than recent ones (temporally graded
  retrograde amnesia), the classic evidence for **systems consolidation** from
  hippocampus to cortex (Squire & Alvarez 1995; [[memory-systems]]).
- **Hypothesis, debated:** the amyloid cascade hypothesis says amyloid-β
  accumulation drives the rest of the disease (Hardy & Higgins 1992).

### Epilepsy: excitation, inhibition and the split brain
- **Established definition:** the International League Against Epilepsy defines
  epilepsy by unprovoked seizures and their recurrence risk (Fisher et al. 2014).
- **Supported, simplified:** seizures arise when excitation outruns inhibition.
  Mutations in ion channels and changes in GABA and glutamate signalling are known
  causes, but "E/I imbalance" compresses many different mechanisms (Staley 2015).
  The healthy balance is described in [[neural-coding-and-computation]].
- **Established:** cutting the corpus callosum to stop seizures spreading produced
  **split-brain** patients, in whom each hemisphere can process and respond to
  information the other does not have (Gazzaniga 2005).

### Schizophrenia and autism as altered precision (hypotheses)
In predictive processing, perception weights prediction errors by their
**precision**, a confidence in each signal ([[predictive-processing]]).
- **Supported:** people with schizophrenia show raised presynaptic dopamine
  synthesis capacity in the striatum (Howes & Kapur 2009). **Hypothesis:** this
  makes irrelevant events feel significant, "aberrant salience", seeding delusions
  (Kapur 2003).
- **Hypothesis:** psychosis is a failure of precision weighting, with too little
  weight on prior beliefs relative to sensory errors in some levels and too much in
  others (Adams et al. 2013; Sterzer et al. 2018). **Supported** piece: people who
  hear voices were more likely to report conditioned tones that were not played,
  and models fit this as overweighted perceptual priors (Powers, Mathys & Corlett 2017).
- **Hypothesis (autism):** autistic perception reflects weak or less-used priors
  (Pellicano & Burr 2012), or high, inflexible precision of sensory prediction
  errors (Lawson, Rees & Friston 2014; Van de Cruys et al. 2014). These are
  competing accounts of perceptual differences, not of a disease.

### Depression, addiction and compulsivity as reinforcement-learning changes
**Computational psychiatry** fits learning and decision models to behaviour and
asks which parameter differs (Montague et al. 2012; Huys, Maia & Frank 2016).
- **Supported:** in a meta-analysis of reward-learning tasks, anhedonia and stress
  related more to lower **reward sensitivity** than to a lower learning rate (Huys et
  al. 2013).
- **Hypothesis:** drugs of abuse produce a dopamine increase that cannot be
  predicted away, so the TD error never reaches zero and drug-associated values keep
  growing (Redish 2004).
- **Supported:** in a large online sample, a compulsivity symptom dimension went
  with less **model-based** (goal-directed) control (Gillan et al. 2016), measured
  with the two-step task (Daw et al. 2011).

## Relevance to building brain-like AI
- **Lesions as ablations.** Each disorder is an ablation study: remove one signal
  (dopamine, hippocampus, inhibition) and see which ability fails. The same method
  tests whether a brain-like model divides labour like a brain.
- **Hyperparameters can fail like disorders.** A learning signal with too little
  gain learns slowly (code below); one that cannot be cancelled inflates values
  (Redish); bad precision weighting over-trusts either priors or data. These are
  useful failure modes to test an agent against.
- **Missing inhibition is a stability bug.** Recurrent models need inhibition or
  normalisation, or activity runs away, much like a seizure.

## Code
A TD learner where dopamine scales the prediction-error update. Lowering dopamine
gain, a crude stand-in for Parkinson's, slows learning of a cue's value. This toy
leaves out tonic dopamine and action selection.

```python
import numpy as np

rng = np.random.default_rng(0)

def trials_to_learn(da_gain, n_states=5, alpha=0.1, gamma=0.95, max_trials=2000):
    """TD(0) on a chain cue -> ... -> reward; dopamine = da_gain * delta.
    Returns trials until the cue's value reaches 90% of its true value."""
    V = np.zeros(n_states + 1)                 # last entry is terminal
    target = gamma ** (n_states - 1)           # true value of the cue state
    for trial in range(1, max_trials + 1):
        for s in range(n_states):
            r = float(s == n_states - 1 and rng.random() < 0.9) / 0.9  # mean 1
            delta = r + gamma * V[s + 1] - V[s]  # reward prediction error
            V[s] += alpha * da_gain * delta      # dopamine scales plasticity
        if V[0] >= 0.9 * target:
            return trial
    return max_trials

healthy = np.mean([trials_to_learn(1.0) for _ in range(20)])
low_da = np.mean([trials_to_learn(0.3) for _ in range(20)])
print(f"trials to learn the cue value: gain 1.0 -> {healthy:.0f}, gain 0.3 -> {low_da:.0f}")
assert low_da > 1.5 * healthy   # lower dopamine gain -> slower learning
```

## Open questions
- How deep brain stimulation works at the circuit level.
- Whether amyloid, tau or something upstream drives Alzheimer's progression.
- Whether precision-weighting accounts of psychosis and autism make predictions
  that competing accounts do not, and at which level of the hierarchy.
- Whether model parameters fitted to behaviour are stable enough within a person
  to be useful clinically; this is a research question, not a current practice.

## Related
- [[action-selection-and-motor-control]] - Go/NoGo pathways that dopamine loss unbalances.
- [[learning-and-plasticity]] - dopamine as a TD error.
- [[neuromodulators]] - dopamine, serotonin and noradrenaline systems involved in these disorders.
- [[predictive-processing]] - precision weighting behind the psychosis and autism hypotheses.
- [[memory-systems]] - hippocampus and consolidation, damaged early in Alzheimer's.
- [[decision-making]] - value-based choice and exploration, the behaviours computational psychiatry fits.

## References
- Dauer & Przedborski (2003) "Parkinson's disease: mechanisms and models", *Neuron* 39:889. doi:10.1016/S0896-6273(03)00568-3
- Frank, Seeberger & O'Reilly (2004) "By carrot or by stick: cognitive reinforcement learning in parkinsonism", *Science* 306:1940. doi:10.1126/science.1102941
- Limousin et al. (1998) "Electrical stimulation of the subthalamic nucleus in advanced Parkinson's disease", *N Engl J Med* 339:1105. doi:10.1056/NEJM199810153391603
- Deuschl et al. (2006) "A randomized trial of deep-brain stimulation for Parkinson's disease", *N Engl J Med* 355:896. doi:10.1056/NEJMoa060281
- Braak & Braak (1991) "Neuropathological stageing of Alzheimer-related changes", *Acta Neuropathol* 82:239. doi:10.1007/BF00308809
- Scoville & Milner (1957) "Loss of recent memory after bilateral hippocampal lesions", *J Neurol Neurosurg Psychiatry* 20:11. doi:10.1136/jnnp.20.1.11
- Squire & Alvarez (1995) "Retrograde amnesia and memory consolidation: a neurobiological perspective", *Curr Opin Neurobiol* 5:169. doi:10.1016/0959-4388(95)80023-9
- Hardy & Higgins (1992) "Alzheimer's disease: the amyloid cascade hypothesis", *Science* 256:184. doi:10.1126/science.1566067
- Fisher et al. (2014) "ILAE official report: a practical clinical definition of epilepsy", *Epilepsia* 55:475. doi:10.1111/epi.12550
- Staley (2015) "Molecular mechanisms of epilepsy", *Nat Neurosci* 18:367. doi:10.1038/nn.3947
- Gazzaniga (2005) "Forty-five years of split-brain research and still going strong", *Nat Rev Neurosci* 6:653. doi:10.1038/nrn1723
- Howes & Kapur (2009) "The dopamine hypothesis of schizophrenia: version III - the final common pathway", *Schizophr Bull* 35:549. doi:10.1093/schbul/sbp006
- Kapur (2003) "Psychosis as a state of aberrant salience", *Am J Psychiatry* 160:13. doi:10.1176/appi.ajp.160.1.13
- Adams, Stephan, Brown, Frith & Friston (2013) "The computational anatomy of psychosis", *Front Psychiatry* 4:47. doi:10.3389/fpsyt.2013.00047
- Sterzer et al. (2018) "The predictive coding account of psychosis", *Biol Psychiatry* 84:634. doi:10.1016/j.biopsych.2018.05.015
- Powers, Mathys & Corlett (2017) "Pavlovian conditioning-induced hallucinations result from overweighting of perceptual priors", *Science* 357:596. doi:10.1126/science.aan3458
- Pellicano & Burr (2012) "When the world becomes 'too real': a Bayesian explanation of autistic perception", *Trends Cogn Sci* 16:504. doi:10.1016/j.tics.2012.08.009
- Lawson, Rees & Friston (2014) "An aberrant precision account of autism", *Front Hum Neurosci* 8:302. doi:10.3389/fnhum.2014.00302
- Van de Cruys et al. (2014) "Precise minds in uncertain worlds: predictive coding in autism", *Psychol Rev* 121:649. doi:10.1037/a0037665
- Montague, Dolan, Friston & Dayan (2012) "Computational psychiatry", *Trends Cogn Sci* 16:72. doi:10.1016/j.tics.2011.11.018
- Huys, Maia & Frank (2016) "Computational psychiatry as a bridge from neuroscience to clinical applications", *Nat Neurosci* 19:404. doi:10.1038/nn.4238
- Huys, Pizzagalli, Bogdan & Dayan (2013) "Mapping anhedonia onto reinforcement learning: a behavioural meta-analysis", *Biol Mood Anxiety Disord* 3:12. doi:10.1186/2045-5380-3-12
- Redish (2004) "Addiction as a computational process gone awry", *Science* 306:1944. doi:10.1126/science.1102384
- Gillan et al. (2016) "Characterizing a psychiatric symptom dimension related to deficits in goal-directed control", *eLife* 5:e11305. doi:10.7554/eLife.11305
- Daw, Gershman, Seymour, Dayan & Dolan (2011) "Model-based influences on humans' choices and striatal prediction errors", *Neuron* 69:1204. doi:10.1016/j.neuron.2011.02.027
