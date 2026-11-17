"""Failure-aware, matched-seed M0c analysis (Python stdlib, no score thresholds)."""
import argparse
import json
import random
from pathlib import Path

ARMS = ("flat", "flat-goal-masked", "tabular-absolute", "tabular-relative",
        "uniform-random", "public-maze-heuristic")
TRAINED = frozenset(ARMS[:4])


def paired_ci(values, draws=10000, seed=20261117):
    if not values:
        raise ValueError("cannot bootstrap absent seeds")
    rng = random.Random(seed)
    n = len(values)
    samples = sorted(
        sum(values[rng.randrange(n)] for _ in range(n)) / n
        for _ in range(draws)
    )
    return [samples[int(0.025 * (draws - 1))],
            samples[int(0.975 * (draws - 1))]]


def analyze(result):
    if result.get("schema") != "brain-result/1":
        raise ValueError("wrong schema")
    cfg = result["config"]
    seeds = cfg["seeds"]
    if (len(seeds) != 10 or sorted(seeds) != list(range(1, 11))
            or list(cfg["arms"]) != list(ARMS)):
        raise ValueError("requires the ten precommitted seeds and all arms")
    rows = {}
    for row in result["runs"]:
        k = (row["arm"], row["seed"])
        if row["arm"] not in ARMS or row["seed"] not in seeds or k in rows:
            raise ValueError("missing, extra or repeated arm/seed row")
        if row["status"] != "ok":
            raise ValueError("failed run must remain in raw record, not count as success")
        metrics = row["scores"]
        for partition in ("source", "development", "heldout"):
            scored = metrics[partition]
            if (not 0 <= scored["success"] <= 1
                    or scored["decisions"] != scored["envSteps"]
                    or scored["episodes"] < 1):
                raise ValueError("invalid outcome or missing environment action")
        expected = cfg["trainSteps"] if row["arm"] in TRAINED else 0
        if (metrics["trainDecisions"] != expected
                or metrics["trainEnvSteps"] != expected
                or metrics["oracleQueries"] != 0):
            raise ValueError("unmatched training budget or privileged policy calls")
        if metrics["heldout"]["episodes"] != cfg["evalTasks"] * cfg["repeats"]:
            raise ValueError("heldout episode count mismatch")
        rows[k] = metrics
    if len(rows) != len(ARMS) * len(seeds):
        raise ValueError("missing arm/seed results")
    manifests = cfg["manifests"]
    audits = cfg["generatorAudits"]
    for seed in seeds:
        manifest = manifests[str(seed)]
        audit = audits[str(seed)]
        counts = manifest["counts"]
        if cfg["protocol"] != "legacy":
            for split in ("train", "dev", "heldout"):
                if counts[split]["duplicates"] != 0:
                    raise ValueError("stress task structural duplication")
            if not (audit["totalOfflineOracleQueries"] >=
                    cfg["trainTasks"] + cfg["devTasks"] + cfg["evalTasks"]):
                raise ValueError("unaccounted feasibility queries")
        for split, count in (("train", cfg["trainTasks"]),
                             ("dev", cfg["devTasks"]), ("heldout", cfg["evalTasks"])):
            if counts[split]["tasks"] != count:
                raise ValueError("wrong split task count")
    arms = {}
    for arm in ARMS:
        dev = [rows[arm, s]["development"]["success"] for s in seeds]
        heldout = [rows[arm, s]["heldout"]["success"] for s in seeds]
        paired = [heldout[i] - rows["uniform-random", s]["heldout"]["success"]
                  for i, s in enumerate(seeds)]
        arms[arm] = {
            "developmentSuccess": sum(dev) / len(dev),
            "heldoutSuccess": sum(heldout) / len(heldout),
            "heldoutCi95": paired_ci(heldout),
            "deltaVsRandom": sum(paired) / len(paired),
            "deltaVsRandomCi95": paired_ci(paired),
            "trainDecisionsTotal": sum(rows[arm, s]["trainDecisions"] for s in seeds),
            "heldoutDecisionsTotal": sum(
                rows[arm, s]["heldout"]["decisions"] for s in seeds
            ),
        }
    comparators = [a for a in ARMS if a != "flat"]
    best = max(comparators, key=lambda a: (
        arms[a]["developmentSuccess"], -comparators.index(a)
    ))
    differences = [
        rows["flat", s]["heldout"]["success"] - rows[best, s]["heldout"]["success"]
        for s in seeds
    ]
    return {
        "schema": "brain-m0c-analysis/1",
        "protocol": cfg["protocol"],
        "seeds": seeds,
        "trainStepsPerLearnedArm": cfg["trainSteps"],
        "primaryMetric": "physical heldout delivery success",
        "arms": arms,
        "bestNonFlatOnDevelopment": best,
        "flatMinusBestHeldoutDelta": sum(differences) / len(differences),
        "flatMinusBestHeldoutCi95": paired_ci(differences),
        "promotion": "HOLD: exploratory legacy or authored structural family; "
                     "no sealed 20-seed confirmation, no justified M1 claim.",
        "limitations": "CI checks trace integrity, not scientific superiority. "
                       "Authored 5x5 topology; relative-Q and public maze "
                       "heuristic are engineered priors.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report = analyze(json.loads(args.result.read_text(encoding="utf-8")))
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    print("M0c", report["protocol"], "development comparator",
          report["bestNonFlatOnDevelopment"], "flat delta",
          report["flatMinusBestHeldoutDelta"], report["flatMinusBestHeldoutCi95"])
    for arm, metrics in report["arms"].items():
        print(arm, "development", metrics["developmentSuccess"],
              "heldout", metrics["heldoutSuccess"], "95% CI",
              metrics["heldoutCi95"], "delta vs random",
              metrics["deltaVsRandom"])


if __name__ == "__main__":
    main()
