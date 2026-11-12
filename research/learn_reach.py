"""Backprop-free sparse microcircuit controlling a real toy joint loop.

This is an audited reaching *engineering* experiment. No realistic vision,
brain-level neurons, motor planning, or macroscopic anatomical rewiring.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import time
from dataclasses import asdict, replace
from pathlib import Path

from closed_loop_reach import HORIZON, reach_trials, run_episodes
from result_schema import bootstrap_ci, make_result, sign_flip, validate
from structural_plasticity import PlasticityConfig, SparsePlasticPolicy

ARMS = ("evidence", "random_growth", "fixed", "frozen", "privileged", "evidence_delay2")
FIXED_EDGES = ((1, 0), (1, 1), (2, 0), (2, 1))  # no visual target-delta feature
ORACLE_WIRING = ((0, 0), (0, 1), (1, 0), (1, 1))  # privileged prior, *not* oracle policy
SEEDS = tuple(range(301, 311))
TRAIN_EPISODES = 120
EVAL_EPISODES = 80
REVERSE_EPISODES = 40


def policy_for(arm: str, seed: int) -> SparsePlasticPolicy:
    if arm not in ARMS or type(seed) is not int:
        raise ValueError("Invalid policy configuration")
    delayed = arm == "evidence_delay2"
    # These defaults were selected using exploratory seeds 0-5 only. The
    # parameters in feedback-steps are halved for two-step delayed reward.
    cfg = replace(PlasticityConfig(), grow_every=40 if delayed else 80,
                  warmup=40 if delayed else 80, min_prune_age=500 if delayed else 1000,
                  min_error_rate=0.15)
    mode = "random" if arm == "random_growth" else "evidence" if arm in ("evidence", "evidence_delay2") else "off"
    return SparsePlasticPolicy(cfg, seed + 31, growth_mode=mode,
                               learn=arm != "frozen",
                               initial_edges=ORACLE_WIRING if arm == "privileged" else FIXED_EDGES)


def run_seed(seed: int, train_episodes: int = TRAIN_EPISODES,
             eval_episodes: int = EVAL_EPISODES,
             reverse_episodes: int = REVERSE_EPISODES) -> list[dict]:
    """Same task draws, primitive actions, episode horizon and rewiring budget per arm."""
    if type(seed) is not int or seed < 0 or any(type(v) is not int or not 1 <= v <= 10000
                                                for v in (train_episodes, eval_episodes, reverse_episodes)):
        raise ValueError("Invalid experiment budget")
    train = reach_trials("train", seed, train_episodes)
    heldout = reach_trials("eval", seed + 80000, eval_episodes)
    familiar = reach_trials("train", seed + 90000, eval_episodes)
    reversal_dev = reach_trials("dev", seed + 110000, reverse_episodes)
    reversed_eval = reach_trials("eval", seed + 120000, eval_episodes)
    rows = []
    for arm in ARMS:
        begin = time.perf_counter()
        try:
            model = policy_for(arm, seed)
            delay = 2 if arm == "evidence_delay2" else 1
            # Training interactions and reward feedback occur only after body moves.
            early = run_episodes(model, train[:min(20, train_episodes)], learn=model.learn, delay=delay,
                                 explore=True)
            late = run_episodes(model, train[min(20, train_episodes):], learn=model.learn, delay=delay,
                                explore=True) if train_episodes > 20 else early
            checkpoint = model.export_state()
            checkpoint_sha = hashlib.sha256(json.dumps(checkpoint, sort_keys=True).encode()).hexdigest()
            before = model.fingerprint()
            source = run_episodes(model, familiar)
            held = run_episodes(model, heldout)
            reversed_before = run_episodes(model, reversed_eval, inverted_motor=True)
            if before != model.fingerprint():
                raise RuntimeError("Frozen evaluation mutated source checkpoint")
            # Adapt in an independent copy so this experiment cannot modify the
            # frozen original; verify old-task retention afterward.
            adapt_model = SparsePlasticPolicy.from_state(checkpoint)
            run_episodes(adapt_model, reversal_dev, learn=adapt_model.learn, delay=delay,
                         explore=True, inverted_motor=True)
            reversed_after = run_episodes(adapt_model, reversed_eval, inverted_motor=True)
            source_after = run_episodes(adapt_model, familiar)
            successes = {"heldoutSuccess": held.success, "sourceSuccess": source.success,
                         "trainingEarlySuccess": early.success, "trainingLateSuccess": late.success,
                         "reversedBefore": reversed_before.success,
                         "reversedAfter": reversed_after.success,
                         "sourceAfterReversal": source_after.success,
                         "heldoutFinalError": held.final_error,
                         "heldoutProgress": held.progress,
                         "heldoutWrongDirection": held.error_rate,
                         "connections": len(model.edges), "newConnections": model.new_edges,
                         "prunedConnections": model.removed_edges,
                         "synapticProducts": model.synaptic_products,
                         "candidateProducts": model.candidate_products,
                         "feedbackCalls": model.feedback_steps,
                         "firstHitStep": held.mean_time_to_hit,
                         "sourceRetentionDelta": source_after.success - source.success}
            rows.append({"arm": arm, "seed": seed, "split": "eval", "status": "ok",
                         "seconds": time.perf_counter() - begin, "checkpoint": checkpoint_sha,
                         "scores": successes, "connectionTopology": [list(x) for x in sorted(model.edges)]})
        except Exception as exc:
            rows.append({"arm": arm, "seed": seed, "split": "eval", "status": "error",
                         "reason": f"{type(exc).__name__}: {exc}",
                         "seconds": time.perf_counter() - begin, "scores": {}, "checkpoint": None})
    return rows


def experiment(seeds: tuple[int, ...] = SEEDS, *, train_episodes: int = TRAIN_EPISODES,
               eval_episodes: int = EVAL_EPISODES, reverse_episodes: int = REVERSE_EPISODES,
               commit: str | None = None) -> dict:
    if not seeds or len(set(seeds)) != len(seeds) or any(type(s) is not int or s < 0 for s in seeds):
        raise ValueError("Invalid seed list")
    runs = [item for seed in seeds for item in run_seed(seed, train_episodes, eval_episodes, reverse_episodes)]
    record = make_result(
        "brain/closed-loop-sparse-reaching",
        f"python research/learn_reach.py --seeds {' '.join(map(str,seeds))} --train-episodes {train_episodes} "
        f"--eval-episodes {eval_episodes} --reverse-episodes {reverse_episodes}",
        {"seeds": list(seeds), "configuration": asdict(policy_for("evidence", seeds[0]).cfg),
         "initialWiring": [list(p) for p in FIXED_EDGES], "privilegedWiring": [list(p) for p in ORACLE_WIRING],
         "arms": list(ARMS), "holdout": "new target magnitudes from a disjoint seed/split namespace",
         "delayedFeedback": "delay2 has half as many reward calls for equal motor decisions",
         "provenance": "engineered delta-position visual sensor; preexisting S1 proprioception and fixed motor decoder",
         "limitation": "simple one-joint simulator, task-specific shaping reward, incomplete macro-anatomical integration"},
        {"trainingBodyActions": train_episodes * HORIZON,
         "developmentReversalBodyActions": reverse_episodes * HORIZON,
         "sourceFrozenEvalBodyActions": eval_episodes * HORIZON,
         "heldoutFrozenEvalBodyActions": eval_episodes * HORIZON,
         "maxSynapses": 4,
         "trainingFeedbackCalls": {"standard": train_episodes * HORIZON,
                                   "delay2": train_episodes * HORIZON // 2}},
        {"heldoutSuccess": "higher", "sourceSuccess": "higher", "reversedAfter": "higher",
         "sourceRetentionDelta": "higher", "heldoutFinalError": "lower",
         "candidateProducts": "lower"},
        runs, baseline="random_growth", environment={"runtime": platform.python_version(), "body": "SimpleJointBody", "cpu": platform.processor()}, commit=commit)
    errors = validate(record)
    if errors:
        raise ValueError("brain-result/1 invalid: " + "; ".join(errors))
    return record


def summary(record: dict) -> dict:
    arms = record["config"]["arms"]
    seeds = record["config"]["seeds"]
    indexed = {(r["seed"], r["arm"]): r for r in record["runs"] if r["status"] == "ok"}
    if len(indexed) != len(arms) * len(seeds):
        return {"status": "incomplete", "complete": len(indexed), "expected": len(arms)*len(seeds)}
    means = {arm: {m: sum(indexed[s, arm]["scores"][m] for s in seeds) / len(seeds)
                   for m in ("heldoutSuccess", "reversedAfter", "sourceRetentionDelta",
                             "newConnections", "candidateProducts")}
             for arm in arms}
    pairs = [indexed[s, "evidence"]["scores"]["heldoutSuccess"] -
             indexed[s, "random_growth"]["scores"]["heldoutSuccess"] for s in seeds]
    stats = {"pairedDelta": sum(pairs)/len(pairs),
             "ci95": list(bootstrap_ci(pairs, rng=random.Random(112), samples=5000)) if len(seeds)>1 else None,
             "signFlipP": sign_flip(pairs)}
    return {"status": "complete", "mean": means, "evidenceVsRandomGrowth": stats,
            "caveat": "one-joint task with designed relative-target input, not actual neural anatomical learning"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, nargs="+", default=list(SEEDS))
    parser.add_argument("--train-episodes", type=int, default=TRAIN_EPISODES)
    parser.add_argument("--eval-episodes", type=int, default=EVAL_EPISODES)
    parser.add_argument("--reverse-episodes", type=int, default=REVERSE_EPISODES)
    parser.add_argument("--commit", type=str)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    data = experiment(tuple(args.seeds), train_episodes=args.train_episodes,
                      eval_episodes=args.eval_episodes, reverse_episodes=args.reverse_episodes,
                      commit=args.commit)
    print(json.dumps(summary(data), indent=2))
    if args.out:
        args.out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")