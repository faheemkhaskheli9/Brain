"""Integrity and paired exploratory summary for backprop-free M0c credit probes."""
import json
import math
import random
import sys

ARMS = ("native-three", "native-two", "mask-goal", "zero-feedback",
        "trace-one-step", "no-bootstrap")


def bootstrap(values, draws=10000):
    if not values:
        raise ValueError("missing paired seeds")
    generator = random.Random(20261118)
    n = len(values)
    x = sorted(sum(values[generator.randrange(n)] for _ in range(n)) / n
               for _ in range(draws))
    return [x[int(0.025 * (draws - 1))], x[int(0.975 * (draws - 1))]]


def validate(record):
    if record.get("schema") != "brain-result/1":
        raise ValueError("wrong result schema")
    config = record.get("config", {})
    seeds = config.get("seeds")
    budgets = config.get("checkpoints")
    repeats = config.get("repeats")
    if (not isinstance(seeds, list) or not seeds or
            any(not isinstance(s, int) or s < 0 for s in seeds) or
            len(set(seeds)) != len(seeds) or
            config.get("arms") != list(ARMS) or
            not isinstance(budgets, list) or len(budgets) < 2 or
            budgets[0] != 0 or budgets != sorted(set(budgets)) or
            not isinstance(repeats, int) or repeats < 1):
        raise ValueError("invalid preregistered design")
    rows = {}
    for row in record.get("runs", []):
        k = (row["seed"], row["arm"])
        if row["seed"] not in seeds or row["arm"] not in ARMS or k in rows:
            raise ValueError("unexpected or duplicate arm/seed")
        if row["status"] != "ok":
            raise ValueError("failed arm/seed must be preserved and investigated")
        s = row["scores"]
        if (s["trainDecisions"] != budgets[-1] or
                s["trainEnvSteps"] != budgets[-1] or
                s["learningUpdates"] != budgets[-1] or
                s["onlineOracleQueries"] != 0 or s["modelBytes"] <= 0):
            raise ValueError("invalid physical/learning budget or privileged oracle")
        if len(s["curve"]) != len(budgets):
            raise ValueError("checkpoint omission")
        for point, budget in zip(s["curve"], budgets):
            if point["decisions"] != budget:
                raise ValueError("non-precommitted checkpoint")
            for metric, n in (("calibration", repeats),
                              ("diagnosticVariants", 2 * repeats)):
                scored = point[metric]
                if (scored["episodes"] != n or
                        scored["decisions"] != scored["envSteps"] or
                        scored["failed"] + scored["deliveries"] != n or
                        scored["success"] != scored["deliveries"] / n or
                        not math.isfinite(scored["entropy"]) or
                        not 0 <= scored["entropy"] <= 1):
                    raise ValueError("evaluation leakage, success or charge mismatch")
            audit = point["sensory"]
            if (audit["directActorInputWidth"] < audit["rawInputWidth"] or
                    audit["rawInputWidth"] < 84 or
                    not 0 <= audit["goalCounterfactualL1"] <= 2.01 or
                    not 0 <= audit["carryingGoalCounterfactualL1"] <= 2.01):
                raise ValueError("missing public input access or invalid saliency")
            if row["arm"] == "mask-goal" and (
                    audit["goalCounterfactualL1"] != 0 or
                    audit["carryingGoalCounterfactualL1"] != 0):
                raise ValueError("goal mask bypass detected")
        rows[k] = s
    if len(rows) != len(seeds) * len(ARMS):
        raise ValueError("missing arm/seed row")
    return rows


def summarize(record):
    rows = validate(record)
    seeds = record["config"]["seeds"]
    arms = {}
    for arm in ARMS:
        before = [rows[s, arm]["curve"][0]["calibration"]["success"] for s in seeds]
        final = [rows[s, arm]["curve"][-1]["calibration"]["success"] for s in seeds]
        variants = [rows[s, arm]["curve"][-1]["diagnosticVariants"]["success"]
                    for s in seeds]
        diff = [a - b for a, b in zip(final, before)]
        goal = [rows[s, arm]["curve"][-1]["sensory"]["goalCounterfactualL1"]
                for s in seeds]
        arms[arm] = {
            "beforeSuccess": sum(before) / len(seeds),
            "finalSuccess": sum(final) / len(seeds),
            "finalCi95": bootstrap(final),
            "gain": sum(diff) / len(seeds),
            "gainCi95": bootstrap(diff),
            "nearbyVariants": sum(variants) / len(seeds),
            "goalSensitivityL1": sum(goal) / len(seeds),
            "averageTrainMeanAbsTD": sum(rows[s, arm]["trainMeanAbsTD"]
                                         for s in seeds) / len(seeds),
            "totalTrainingDeliveries": sum(rows[s, arm]["trainDeliveries"]
                                           for s in seeds),
        }
    return {"schema": "brain-m0c-credit-audit/1",
            "sourceCommit": record["commit"],
            "seeds": seeds, "checkpoints": record["config"]["checkpoints"],
            "arms": arms, "advancement": "HOLD: repeated-task mechanistic diagnostic, no sealed transfer",
            "limits": "Two-step arm has a different objective; goal mask on fixed geometry "
                      "does not test goal following; action trajectories diverge after learning."}


def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        raise SystemExit("usage: python research/analyze_m0c_credit_probe.py RESULT [OUT]")
    with open(sys.argv[1], encoding="utf-8") as stream:
        record = json.load(stream)
    summary = summarize(record)
    if len(sys.argv) == 3:
        with open(sys.argv[2], "w", encoding="utf-8") as stream:
            json.dump(summary, stream, indent=2, sort_keys=True)
            stream.write("\n")
    for arm, score in summary["arms"].items():
        print(arm, "before", round(score["beforeSuccess"], 4),
              "after", round(score["finalSuccess"], 4),
              "95% CI", score["finalCi95"], "mean goal L1",
              round(score["goalSensitivityL1"], 5))
    print(summary["advancement"])


if __name__ == "__main__":
    main()
