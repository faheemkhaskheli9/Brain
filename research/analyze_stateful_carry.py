"""Pretest baseline selection and seed-clustered paired analysis for carry pilot.

Results remain diagnostic. Never select a winner using held-out scores.
Usage: python research/analyze_stateful_carry.py /tmp/carry-gate-b.json
"""
import json
import random
import sys

from result_schema import bootstrap_ci, sign_flip, validate

EXPERIMENT = "brain-world/stateful-carry-diagnostic"
ARMS = ("flat-brain", "flat-no-goal", "tabular-q", "random-legal",
        "fixed-script", "hand-coded-heuristic")


def analyze(record):
    errors = validate(record)
    if errors:
        raise ValueError("invalid brain-result/1: " + "; ".join(errors))
    if record["experiment"] != EXPERIMENT:
        raise ValueError("unexpected experiment")
    seeds = record["config"]["seeds"]
    if len(set(seeds)) != len(seeds) or not seeds:
        raise ValueError("duplicate or empty seeds")
    expected = {(arm, seed) for arm in ARMS for seed in seeds}
    actual = {(r["arm"], r["seed"]) for r in record["runs"]}
    if actual != expected or len(record["runs"]) != len(expected):
        raise ValueError("incomplete or unexpected arm-by-seed cohort")
    rows = {(r["arm"], r["seed"]): r for r in record["runs"]}
    complete = [a for a in ARMS if all(rows[a, s]["status"] == "ok" for s in seeds)]
    if not complete:
        raise ValueError("no complete eligible arm; report failures without selecting a winner")
    # Development split only; no held-out score access during comparator selection.
    def dev_score(arm):
        values = [rows[arm, s]["scores"]["development"]["success"] for s in seeds]
        if any(not isinstance(x, (float, int)) or not 0 <= x <= 1 for x in values):
            raise ValueError("invalid development success")
        return sum(values) / len(values)
    chosen = max(complete, key=lambda a: (dev_score(a), -ARMS.index(a)))
    comparisons = {}
    for arm in ARMS:
        paired = [s for s in seeds if rows[arm, s]["status"] == "ok" and
                  rows[chosen, s]["status"] == "ok"]
        effects = [rows[arm, s]["scores"]["heldout"]["success"] -
                   rows[chosen, s]["scores"]["heldout"]["success"] for s in paired]
        comparisons[arm] = {
            "paired_seeds": paired,
            "heldout_delta_mean": sum(effects) / len(effects) if effects else None,
            "paired_bootstrap95": bootstrap_ci(effects, random.Random(0)) if effects else None,
            "paired_sign_flip_p": sign_flip(effects) if effects else None,
            "complete": arm in complete,
        }
    return {
        "experimental_unit": "paired_seed; episodes nested in a seed are not independent",
        "confirmatory": False,
        "development_selected_comparator": chosen,
        "development_success": {a: dev_score(a) for a in complete},
        "run_failures": [{"arm": r["arm"], "seed": r["seed"], "reason": r.get("reason")}
                         for r in record["runs"] if r["status"] != "ok"],
        "comparisons": comparisons,
        "warning": "Diagnostic carry environment only. No learned options or confirmatory transfer claim.",
    }


def main(argv):
    if len(argv) != 1:
        print("usage: python research/analyze_stateful_carry.py FILE.json", file=sys.stderr)
        return 2
    with open(argv[0], encoding="utf-8") as handle:
        record = json.load(handle)
    try:
        result = analyze(record)
    except (ValueError, KeyError, TypeError) as exc:
        print("stateful carry analysis invalid: " + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
