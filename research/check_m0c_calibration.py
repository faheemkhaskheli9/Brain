"""M0c same-task diagnostic fail-closed integrity gate. Not a success threshold."""
import argparse
import json

ARMS = ("flat-brain", "q-absolute", "q-relative", "q-relative-explore50",
        "q-relative-potential", "q-relative-no-reward", "uniform-random")


def check(record):
    if record.get("schema") != "brain-result/1":
        raise ValueError("wrong result schema")
    cfg = record.get("config", {})
    seeds = cfg.get("seeds")
    checkpoints = cfg.get("checkpoints")
    if (not isinstance(seeds, list) or not seeds or len(set(seeds)) != len(seeds)
            or not isinstance(checkpoints, list)
            or len(checkpoints) < 2 or checkpoints[0] != 0
            or checkpoints != sorted(set(checkpoints))
            or cfg.get("arms") != list(ARMS)):
        raise ValueError("invalid precommitted design")
    indexed = {}
    for r in record["runs"]:
        key = (r["seed"], r["arm"])
        if (r["seed"] not in seeds or r["arm"] not in ARMS
                or key in indexed):
            raise ValueError("repeated/unexpected row")
        if r["status"] != "ok":
            raise ValueError("failed run must remain visible; cannot be promoted")
        s = r["scores"]
        expected = 0 if r["arm"] == "uniform-random" else checkpoints[-1]
        if (s["trainDecisions"] != expected or s["trainEnvSteps"] != expected
                or s["oracleQueries"] != 0):
            raise ValueError("budget error or uncharged privileged step")
        if len(s["curve"]) != len(checkpoints):
            raise ValueError("missing checkpoint")
        for step, budget in zip(s["curve"], checkpoints):
            if step["decisions"] != budget:
                raise ValueError("wrong checkpoint budget")
            for partition, n in [("calibration", cfg["repeats"]),
                                 ("diagnosticVariants",
                                  cfg["repeats"] * len(cfg["diagnosticVariants"]))]:
                scores = step[partition]
                if (scores["episodes"] != n
                        or scores["envSteps"] != scores["decisions"]
                        or scores["failed"] != n - scores["deliveries"]
                        or scores["success"] != scores["deliveries"] / n):
                    raise ValueError("unpaid episode or outcome")
        indexed[key] = s
    if len(indexed) != len(seeds) * len(ARMS):
        raise ValueError("missing arm/seed result")
    return indexed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    with open(args.path, encoding="utf-8") as stream:
        record = json.load(stream)
    runs = check(record)
    for arm in ARMS:
        matching = [runs[s, arm] for s in record["config"]["seeds"]]
        start = sum(m["before"]["calibration"]["success"] for m in matching) / len(matching)
        end = sum(m["after"]["calibration"]["success"] for m in matching) / len(matching)
        variant = sum(m["after"]["diagnosticVariants"]["success"] for m in matching) / len(matching)
        pickups = sum(m["training"]["pickups"] for m in matching)
        print(arm, "before", round(start, 4), "after", round(end, 4),
              "variant", round(variant, 4), "train_pickups", pickups)


if __name__ == "__main__":
    main()
