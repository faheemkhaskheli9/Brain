"""Validate and summarize fixed-log credit replay without conflating update size with skill.

The comparisons are paired by the stream seed. They describe weight/policy
movement on *supplied off-policy transitions*, not successful learned control.
"""
import argparse
import json
import math
import random
from collections import defaultdict
from pathlib import Path

from result_schema import validate

ARMS = (
    "native", "trace-one-step", "no-bootstrap", "actor-frozen",
    "critic-frozen", "reward-shifted", "zero-feedback",
)
METRICS = ("actorDeltaL1", "criticDeltaL1", "probeChangeL1", "meanAbsTD")
CONTROLS = ("trace-one-step", "no-bootstrap", "reward-shifted")


def _mean(xs):
    return sum(xs) / len(xs)


def paired_interval(xs, ys, *, seed=20261118, draws=10000):
    """Mean paired contrast and seeded 95% percentile interval over streams."""
    if len(xs) != len(ys) or not xs:
        raise ValueError("unpaired inputs")
    differences = [a - b for a, b in zip(xs, ys, strict=True)]
    rng = random.Random(seed)
    n = len(differences)
    values = sorted(
        sum(differences[rng.randrange(n)] for _ in range(n)) / n
        for _ in range(draws)
    )
    return {
        "mean": _mean(differences),
        "ci95": [values[int(0.025 * draws)], values[int(0.975 * draws) - 1]],
        "perSeed": differences,
    }


def analyze(record):
    problems = validate(record)
    if problems:
        raise ValueError("schema: " + "; ".join(problems))
    if record.get("experiment") != "brain-world/m0d-matched-public-transition-credit-replay":
        raise ValueError("wrong experiment type")
    declared_arms = record["config"].get("arms")
    seeds = record["config"].get("seeds")
    if declared_arms != list(ARMS) or not isinstance(seeds, list) or not seeds or (
        len(seeds) != len(set(seeds))
    ) or any(not isinstance(s, int) or s < 0 for s in seeds):
        raise ValueError("invalid declared arms or seeds")
    grouped = defaultdict(dict)
    for row in record["runs"]:
        if row["seed"] not in seeds or row["arm"] not in ARMS or row["status"] != "ok":
            raise ValueError("unknown seed/arm or unsuccessful row")
        grouped[row["seed"]][row["arm"]] = row["scores"]
    if set(grouped) != set(seeds):
        raise ValueError("missing seed")
    per_arm = {arm: {metric: [] for metric in METRICS} for arm in ARMS}
    for seed in sorted(seeds):
        cohort = grouped[seed]
        if set(cohort) != set(ARMS):
            raise ValueError(f"missing arm for seed {seed}")
        if len({x["streamHash"] for x in cohort.values()}) != 1:
            raise ValueError(f"mismatched logged experience seed {seed}")
        for field in ("recordedEnvironmentSteps", "recordedEpisodes",
                      "recordedSuccesses", "recordedInvalid", "originalRewardSum"):
            if len({x[field] for x in cohort.values()}) != 1:
                raise ValueError(f"different public source {field} seed {seed}")
        if len({json.dumps(x["beforeProbe"], sort_keys=True)
                for x in cohort.values()}) != 1:
            raise ValueError("different initial actor policy")
        expected = next(iter(cohort.values()))["recordedEnvironmentSteps"]
        for arm, x in cohort.items():
            if x["replayDecisions"] != expected or x["replayEnvironmentSteps"] != 0 or (
                x["policyOracleQueries"] != 0 or x["policyEnvironmentInteractions"] != 0
            ):
                raise ValueError(f"uncounted replay update or interaction: {seed}/{arm}")
            for metric in METRICS:
                value = x[metric]
                if not isinstance(value, (int, float)) or (
                    not math.isfinite(value) or value < 0
                ):
                    raise ValueError(f"invalid metric {metric}: {seed}/{arm}")
                per_arm[arm][metric].append(value)
        if cohort["actor-frozen"]["actorDeltaL1"] != 0 or (
            cohort["critic-frozen"]["criticDeltaL1"] != 0
        ) or any(
            cohort["zero-feedback"][metric] != 0
            for metric in ("actorDeltaL1", "criticDeltaL1", "meanAbsTD",
                           "probeChangeL1")
        ):
            raise ValueError("negative controls failed")

    contrasts = {
        metric: {
            arm: paired_interval(per_arm["native"][metric], per_arm[arm][metric])
            for arm in CONTROLS
        }
        for metric in ("actorDeltaL1", "criticDeltaL1", "probeChangeL1")
    }
    return {
        "status": "diagnostic-only-not-transfer",
        "seedCount": len(seeds),
        "seeds": sorted(seeds),
        "records": len(record["runs"]),
        "sourceCommit": record["commit"],
        "perArmMean": {
            arm: {metric: _mean(per_arm[arm][metric]) for metric in METRICS}
            for arm in ARMS
        },
        "nativeMinusControls": contrasts,
        "interpretation": "parameter/policy L1 on forced off-policy experiences, not goal success",
        "bootstrap": "10,000 paired-seed resamples, Python random.Random(20261118)",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    data = json.loads(args.result.read_text(encoding="utf-8"))
    summary = analyze(data)
    result = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(result, encoding="utf-8")
    print(result)
