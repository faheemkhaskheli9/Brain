"""Auditable preregistered evidence gate for stateful backprop-free option pilots.

This is an evidence checker, not an optimizer and not a source of positive results.
Strongest-control rankings are descriptive, not a frozen-test-tuned comparator.
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
from pathlib import Path

PRIMARY = "flat"
TREATMENT = "options"
ARMS = ("flat", "flat-goal-masked", "options", "options-no-gate",
        "options-no-terminate", "random", "oracle")
TARGET_SEEDS = tuple(range(1, 11))


def paired_interval(differences: list[float], draws: int = 4096) -> tuple[float, float]:
    if not differences:
        raise ValueError("empty paired differences")
    draw = random.Random(112)
    n = len(differences)
    samples = sorted(
        sum(differences[draw.randrange(n)] for _ in range(n)) / n
        for _ in range(draws)
    )
    return samples[int(draws * 0.025)], samples[min(draws - 1, int(draws * 0.975))]


def signflip_p(differences: list[float]) -> float:
    if not differences:
        raise ValueError("empty paired differences")
    observed = abs(sum(differences))
    if len(differences) > 16:
        raise ValueError("exact sign flip requires at most 16 seeds")
    total, exceed = 0, 0
    for signs in itertools.product((-1, 1), repeat=len(differences)):
        total += 1
        if abs(sum(s * d for s, d in zip(signs, differences))) >= observed - 1e-12:
            exceed += 1
    return exceed / total


def audit(record: dict) -> dict:
    if record.get("schema") != "brain-result/1" or (
        record.get("experiment") != "brain-world/stateful-options-pilot"
    ):
        raise ValueError("wrong result schema or experiment")
    seeds = record.get("config", {}).get("seeds")
    if seeds != list(TARGET_SEEDS):
        raise ValueError("confirmatory evidence requires fixed seeds 1..10 in order")
    budget = record.get("budgets", {})
    if not isinstance(budget.get("trainingDecisionsPerArm"), int) or not isinstance(
        budget.get("adaptationDecisionsPerArm"), int
    ) or budget["trainingDecisionsPerArm"] != 10000 or budget["adaptationDecisionsPerArm"] != 2000:
        raise ValueError("confirmatory protocol requires exactly 10000 train / 2000 dev decisions")
    # Historical results allowed a whole final episode past the requested cap.
    # Only explicitly exact-budget runs can pass the new confirmatory gate.
    mode = budget.get("trainingOvershoot")
    if mode == "none (exact cap)":
        exact_budget = True
    elif mode in (None, "episode boundary, logged per run"):
        exact_budget = False
    else:
        raise ValueError("unknown budget protocol")
    indexed: dict[tuple[int, str], dict] = {}
    for row in record.get("runs", []):
        key = (row.get("seed"), row.get("arm"))
        if key in indexed:
            raise ValueError(f"duplicate arm/seed {key}")
        if row.get("status") != "ok" or row.get("split") != "eval":
            raise ValueError(f"missing or failed run {key}")
        indexed[key] = row
    expected = {(seed, arm) for seed in TARGET_SEEDS for arm in ARMS}
    if set(indexed) != expected:
        raise ValueError("incomplete paired arms/seeds")
    for seed in TARGET_SEEDS:
        for arm in ARMS:
            scores = indexed[seed, arm]["scores"]
            for item in ("heldout", "zeroShot", "sourceBefore", "sourceAfter"):
                value = scores[item]["success"]
                if not isinstance(value, (int, float)) or not 0 <= value <= 1:
                    raise ValueError(f"invalid success score {seed}/{arm}/{item}")
            if arm not in ("random", "oracle"):
                for phase, key in (("training", "trainingDecisionsPerArm"),
                                   ("adaptation", "adaptationDecisionsPerArm")):
                    spent = scores[phase]["decisions"]
                    limit = budget[key]
                    allowed = spent == limit if exact_budget else limit <= spent < limit + 81
                    if not isinstance(spent, int) or not allowed:
                        raise ValueError(f"unmatched decision budget {seed}/{arm}/{phase}")
    difference = [
        indexed[seed, TREATMENT]["scores"]["heldout"]["success"]
        - indexed[seed, PRIMARY]["scores"]["heldout"]["success"]
        for seed in TARGET_SEEDS
    ]
    retention = [
        indexed[seed, TREATMENT]["scores"]["sourceAfter"]["success"]
        - indexed[seed, TREATMENT]["scores"]["sourceBefore"]["success"]
        for seed in TARGET_SEEDS
    ]
    shift = sum(difference) / len(difference)
    lo, hi = paired_interval(difference)
    rlo, rhi = paired_interval(retention)
    means = {
        arm: sum(indexed[s, arm]["scores"]["heldout"]["success"]
                 for s in TARGET_SEEDS) / len(TARGET_SEEDS)
        for arm in ARMS
    }
    # A primary comparison must be registered BEFORE observing test arms.
    # The strongest other arm is reported but cannot be retroactively chosen
    # as a new statistical comparator.
    secondary = sorted(
        (arm for arm in ARMS if arm not in (TREATMENT, "oracle")),
        key=lambda a: means[a], reverse=True
    )
    # Require advantage over *every* preregistered budget-matched learned
    # control, rather than selecting whichever happens to lose on frozen test.
    controls = ("flat", "flat-goal-masked", "options-no-gate", "options-no-terminate")
    comparisons = {}
    for control in controls:
        diff = [
            indexed[seed, TREATMENT]["scores"]["heldout"]["success"]
            - indexed[seed, control]["scores"]["heldout"]["success"]
            for seed in TARGET_SEEDS
        ]
        c_lo, c_hi = paired_interval(diff)
        comparisons[control] = {
            "delta": sum(diff) / len(diff), "ci95": [c_lo, c_hi],
            "positive": sum(diff) / len(diff) >= 0.10 and c_lo > 0,
        }
    gate = exact_budget and all(v["positive"] for v in comparisons.values()) and rlo >= -0.05
    return {
        "gate": "pass" if gate else "fail",
        "budget_protocol": "exact" if exact_budget else "legacy-overshoot",
        "primary_comparator": PRIMARY,
        "n_seeds": len(TARGET_SEEDS), "delta": shift,
        "delta_ci95": [lo, hi], "paired_signflip_p": signflip_p(difference),
        "retention_delta": sum(retention) / len(retention),
        "retention_ci95": [rlo, rhi], "matched_controls": comparisons,
        "means": means, "strongest_nonoracle_descriptive": secondary[0],
        "warning": "No learned initiation: positive results would describe engineered-gate options only.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    args = parser.parse_args()
    report = audit(json.loads(args.result.read_text(encoding="utf-8")))
    print(json.dumps(report, indent=2))
    if report["gate"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
