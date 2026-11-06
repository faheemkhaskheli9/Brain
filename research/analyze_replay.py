"""Pre-registered paired-seed comparison for opt-in Brain World replay (#152).

All attempted seeds stay in the denominator. This reports whether the fixed
acceptance rule passes; it does not edit experiments, select hyperparameters,
or silently drop timeout/error runs.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from result_schema import bootstrap_ci, sign_flip, validate

SKILLS = ("grasp", "listen", "read", "write")
BASELINE = "sleep-uniform"
ARMS = ("sleep-no-replay", BASELINE, "sleep-td", "sleep-td-shuffle",
        "sleep-td-mix", "sleep-failure")
MIN_GAIN = 0.03
MAX_SKILL_DROP = -0.03
MAX_TIME_RATIO = 1.25


def _retention(row: dict) -> dict[str, float]:
    kept = row["scores"].get("kept")
    if not isinstance(kept, dict) or any(
        not isinstance(kept.get(k), (int, float)) or not math.isfinite(kept[k])
        or kept[k] < 0 or kept[k] > 1 for k in SKILLS
    ):
        raise ValueError(f"missing/nonfinite retained skills: {row['arm']}/{row['seed']}")
    return {k: kept[k] for k in SKILLS}


def analyze(record: dict) -> dict:
    """Return all-seed graduation counts, paired differences and rule verdicts."""
    issues = validate(record)
    if issues:
        raise ValueError("invalid brain-result/1: " + "; ".join(issues))
    if record["experiment"] != "brain-world/sweep":
        raise ValueError("expected brain-world/sweep record")
    config, budget = record["config"], record["budgets"]
    seeds = config.get("seeds")
    arms = config.get("arms")
    if (not isinstance(seeds, list) or not seeds
            or len(seeds) != len(set(seeds))
            or not isinstance(arms, dict) or BASELINE not in arms
            or any(a not in ARMS for a in arms)):
        raise ValueError("invalid or mixed replay arms/seeds")
    if budget.get("episodes_per_stage") != 20000 or budget.get("scored_episodes") != 4000:
        raise ValueError("training/scoring budget differs from preregistration")
    gains = config.get("gains", {})
    expected = {"memCap": 2048, "sleepSize": 200,
                "sleepPriorityAlpha": 0.6, "sleepUniformMix": 0.2,
                "sleepImportanceBeta": 1}
    if any(gains.get(k) != v for k, v in expected.items()):
        raise ValueError("replay settings differ from preregistration")
    for arm, settings in arms.items():
        if settings.get("replay") != 0.1 or settings.get("sleepActor", False):
            raise ValueError("unequal online rehearsal or replaying actor")
        if settings.get("sleepEvery") != (0 if arm == "sleep-no-replay" else 20):
            raise ValueError("unequal sleep cadence")
    rows = {}
    for row in record["runs"]:
        key = (row["arm"], row["seed"])
        if row.get("split") is not None or key in rows:
            raise ValueError("unexpected split or duplicate arm/seed")
        rows[key] = row
    expected_rows = {(arm, seed) for arm in arms for seed in seeds}
    if set(rows) != expected_rows:
        raise ValueError("missing/unexpected arm/seed rows (including failures)")
    base = {s: rows[BASELINE, s] for s in seeds}
    output = {"experiment": record["experiment"], "commit": record["commit"],
              "seeds": seeds, "baseline": BASELINE, "by_arm": {}}
    for arm in arms:
        cohort = [rows[arm, s] for s in seeds]
        completed = sum(row["status"] == "ok" for row in cohort)
        paired = [(base[s], rows[arm, s]) for s in seeds
                  if base[s]["status"] == rows[arm, s]["status"] == "ok"]
        deltas, skill_deltas, times = [], {k: [] for k in SKILLS}, []
        for before, after in paired:
            b, a = _retention(before), _retention(after)
            for k in SKILLS:
                skill_deltas[k].append(a[k] - b[k])
            deltas.append(sum(a[k] - b[k] for k in SKILLS) / len(SKILLS))
            for row in (before, after):
                if not isinstance(row.get("seconds"), (int, float)) or not math.isfinite(row["seconds"]) or row["seconds"] <= 0:
                    raise ValueError("missing/nonpositive wall-clock time for a graduated seed")
            times.append((before["seconds"], after["seconds"]))
        if arm == BASELINE:
            for row in cohort:
                if row["status"] == "ok":
                    _retention(row)
        ci = bootstrap_ci(deltas, rng=random.Random(152), samples=5000)
        mean = sum(deltas) / len(deltas) if deltas else None
        skills = {k: sum(ds) / len(ds) if ds else None for k, ds in skill_deltas.items()}
        wall_ratio = (sum(pair[1] for pair in times) / sum(pair[0] for pair in times)) if times else None
        baseline_complete = sum(row["status"] == "ok" for row in base.values())
        success = (arm != BASELINE and len(paired) >= 2 and completed >= baseline_complete
                   and mean is not None and mean >= MIN_GAIN
                   and ci is not None and ci[0] > 0
                   and all(x is not None and x >= MAX_SKILL_DROP for x in skills.values())
                   and wall_ratio is not None and wall_ratio <= MAX_TIME_RATIO)
        output["by_arm"][arm] = {
            "started": len(cohort), "graduated": completed,
            "timeouts": sum(row["status"] == "timeout" for row in cohort),
            "errors": sum(row["status"] == "error" for row in cohort),
            "paired_n": len(paired), "mean_paired_retention_gain": mean,
            "paired_ci95": list(ci) if ci else None,
            "paired_sign_flip_p": sign_flip(deltas) if deltas else None,
            "per_skill_paired_gain": skills,
            "paired_wall_time_ratio": wall_ratio,
            "passes_preregistered_rule": bool(success),
        }
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result", type=Path, help="brain-result/1 sweep JSON")
    args = parser.parse_args()
    try:
        output = analyze(json.loads(args.result.read_text(encoding="utf-8")))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(1, f"invalid replay experiment: {exc}\n")
    print(json.dumps(output, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
