# Identical-transition TD update test (2026-11-18)

**Status: executed, exploratory; M1-M8 stay on HOLD.** Follow-up to [the sensor and credit results](m0c-sensory-credit-results-2026-11-18.md), which listed this as the next test for #112. It is a one-task diagnostic of the existing backprop-free Brain actor and critic, not transfer.

## Design

For each of seeds 1-10, the native three-action learner trains for 4,000 physical decisions on the fixed pickup/move/drop task while its transitions are logged (public observation, action, reward, next observation, episode end). That one stream is then replayed with forced actions into fresh learners with the **same initial weights**. Arms differ only in the update rule, so state visitation cannot differ:

| Arm | Rule |
|---|---|
| replay-native | unchanged Brain rule (a test asserts it reproduces the logging learner's weights exactly) |
| replay-no-bootstrap | next-state critic value dropped |
| replay-trace-one-step | previous-step eligibility cleared each step |
| replay-zero-feedback | reward set to 0 |
| replay-shuffled | same transitions, order shuffled (breaks trace credit) |

Scoring is frozen: 12 repeats on the training task, same evaluation as before. 0 oracle queries. Brain source and GAINS are untouched.

## Result (delivery success after replay, mean of 10 seeds)

| Arm | Success | 95% CI | Paired difference vs native (p) |
|---|---:|---|---|
| replay-native | 11.67% | [3.3%, 21.7%] | - |
| replay-no-bootstrap | 1.67% | [0%, 4.2%] | -10.0 pp (0.125) |
| replay-trace-one-step | 1.67% | [0%, 4.2%] | -10.0 pp (0.062) |
| replay-zero-feedback | 2.50% | [0%, 5.0%] | -9.2 pp (0.125) |
| replay-shuffled | 2.50% | [0%, 5.8%] | -9.2 pp (0.062) |

## Reading

- With visitation held identical, every ablation scores near chance; the native rule is the only arm above it. This is consistent with the earlier ablations, and rules out visitation differences as their only explanation.
- The paired sign-flip p values are 0.062-0.125 with n = 10, so **none is significant**. The effect is directional, not established.
- The native arm itself is weak (11.7%, CI reaches 3%): the update rule learns this task slowly even on its own transitions. The logged stream comes from the native learner, so it favours the native rule's own visitation; a stream from a different behaviour policy was not tested.
- One task, one geometry, no varied goals, no retention, no held-out transfer. This is not evidence of skill composition.

## Reproduce

```
node game/world/test_stateful_replay_td.mjs
node game/world/stateful_replay_td.mjs 1 2 3 4 5 6 7 8 9 10 --out research/results/m0c-identical-replay-10seed-2026-11-18.json
python research/result_schema.py research/results/m0c-identical-replay-10seed-2026-11-18.json
```

Next: randomized goals, a different behaviour policy for the logged stream, retention, then a fresh held-out family. #112 stays open.
