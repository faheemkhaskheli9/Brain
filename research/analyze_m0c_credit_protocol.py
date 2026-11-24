"""Integrity check and preregistered paired contrasts for the M0c frozen-step credit protocol.

Diverged (status "error") rows are preserved and scored as 0 success, never dropped.
Contrasts use exact paired sign-flip tests over seeds with Holm correction.
"""
import itertools
import json
import math
import random
import sys

EXPERIMENT = "brain-world/m0c-frozen-step-credit-protocol"
ARMS = ("native", "aligned", "mask-goal", "yoked-reward",
        "trace-one-step", "no-bootstrap", "no-hidden")
# (label, minuend arm, subtrahend arm) on trained-goal frozen success, at every eval scale.
CONTRASTS = (
    ("goal-use", "native", "mask-goal"),
    ("reward-contingency", "native", "yoked-reward"),
    ("eligibility", "native", "trace-one-step"),
    ("bootstrap", "native", "no-bootstrap"),
    ("gain-layout", "aligned", "native"),
    ("hidden-layer", "native", "no-hidden"),
)
ALPHA = 0.05


def bootstrap(values, draws=10000):
    generator = random.Random(20261124)
    n = len(values)
    x = sorted(sum(values[generator.randrange(n)] for _ in range(n)) / n
               for _ in range(draws))
    return [x[int(0.025 * (draws - 1))], x[int(0.975 * (draws - 1))]]


def sign_flip_p(diffs):
    """Two-sided paired sign-flip p-value; exact up to 16 seeds."""
    n = len(diffs)
    observed = abs(sum(diffs))
    if n <= 16:
        flips = itertools.product((1, -1), repeat=n)
        total = 2 ** n
    else:
        generator = random.Random(20261124)
        total = 20000
        flips = ([generator.choice((1, -1)) for _ in range(n)] for _ in range(total))
    hits = sum(abs(sum(s * d for s, d in zip(signs, diffs))) >= observed - 1e-12
               for signs in flips)
    return hits / total


def holm(pvalues):
    order = sorted(range(len(pvalues)), key=lambda i: pvalues[i])
    adjusted, running = [0.0] * len(pvalues), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(pvalues) - rank) * pvalues[i]))
        adjusted[i] = running
    return adjusted


def _check_score(score, goals, repeats):
    n = len(goals) * repeats
    if (score["episodes"] != n or not 0 <= score["deliveries"] <= n or
            score["success"] != score["deliveries"] / n or
            sorted(score["perGoal"]) != sorted(",".join(map(str, g)) for g in goals)):
        raise ValueError("score episode/goal mismatch")


def validate(record):
    if record.get("schema") != "brain-result/1" or record.get("experiment") != EXPERIMENT:
        raise ValueError("wrong schema or experiment")
    c = record["config"]
    seeds, dev, budget, repeats = c["seeds"], c["devSeeds"], c["budget"], c["repeats"]
    goals = c["goals"]
    if c["arms"] != list(ARMS) or set(seeds) & set(dev) or not seeds or not dev:
        raise ValueError("invalid design or dev/eval seed overlap")
    keys = [",".join(map(str, g)) for split in goals.values() for g in split]
    if len(set(keys)) != len(keys):
        raise ValueError("goal splits overlap")
    selection, rows = {}, {}
    for row in record["runs"]:
        arm, scale = row["arm"].split("@x")
        scale = float(scale)
        scale = int(scale) if scale.is_integer() else scale
        if row["split"] == "dev-selection":
            k = (scale, row["seed"])
            if arm != "native" or row["seed"] not in dev or k in selection:
                raise ValueError("invalid selection row")
            if row["status"] == "ok":
                s = row["scores"]
                _check_score(s["dev"], goals["dev"], repeats)
                if s["training"]["decisions"] != budget:
                    raise ValueError("selection budget mismatch")
                selection[k] = s["dev"]["success"]
            else:
                selection[k] = 0.0
        elif row["split"] == "eval":
            k = (scale, arm, row["seed"])
            if arm not in ARMS or row["seed"] not in seeds or k in rows:
                raise ValueError("unexpected or duplicate eval row")
            rows[k] = row
        else:
            raise ValueError("unknown split")
    grid = c["scaleGrid"]
    if set(selection) != {(s, d) for s in grid for d in dev}:
        raise ValueError("missing selection row")
    means = {s: sum(selection[s, d] for d in dev) / len(dev) for s in grid}
    def pick(options):
        top = options[0]
        for s in options:
            if means[s] > means[top] + 1e-12:
                top = s
        return top
    best = pick(grid)
    if best != c["selection"]["selected"]:
        raise ValueError("selected scale does not follow the preregistered rule")
    second = pick([s for s in grid if s != 1]) if best == 1 else best
    if c["evalScales"] != [1, second]:
        raise ValueError("eval scales must be x1 and the selected (or best other) scale")
    for scale in c["evalScales"]:
        for arm in ARMS:
            for seed in seeds:
                row = rows.get((scale, arm, seed))
                if row is None:
                    raise ValueError("missing eval row")
                if row["status"] != "ok":
                    continue
                s = row["scores"]
                t = s["training"]
                if (t["decisions"] != budget or s["onlineOracleQueries"] != 0 or
                        s["modelBytes"] <= 0 or not math.isfinite(t["meanActorStep"])):
                    raise ValueError("invalid budget, oracle use or step telemetry")
                for when in ("before", "after"):
                    _check_score(s[when]["train"], goals["train"], repeats)
                    _check_score(s[when]["heldout"], goals["heldout"], repeats)
                if s["primary"] != s["after"]["train"]:
                    raise ValueError("primary metric is not trained-goal success")
                if arm == "mask-goal" and (s["goalSensitivity"]["startL1"] != 0 or
                                           s["goalSensitivity"]["carryingL1"] != 0):
                    raise ValueError("goal mask bypass detected")
                if arm == "aligned" and s["fanIn"]["gainIndicesUsed"] != 0:
                    raise ValueError("aligned layout still drives gain inputs")
    return rows, means, best


def _value(row, metric):
    if row["status"] != "ok":
        return 0.0
    return row["scores"]["after"][metric]["success"]


def summarize(record):
    rows, means, best = validate(record)
    focus = record["config"]["evalScales"][1]
    c = record["config"]
    seeds = c["seeds"]
    arms, tests = {}, []
    for scale in c["evalScales"]:
        for arm in ARMS:
            group = [rows[scale, arm, s] for s in seeds]
            ok = [r for r in group if r["status"] == "ok"]
            train = [_value(r, "train") for r in group]
            held = [_value(r, "heldout") for r in group]
            arms[f"{arm}@x{scale}"] = {
                "errors": len(group) - len(ok),
                "trainSuccess": sum(train) / len(seeds), "trainCi95": bootstrap(train),
                "heldoutSuccess": sum(held) / len(seeds), "heldoutCi95": bootstrap(held),
                "perSeedTrain": train,
                "meanActorStep": (sum(r["scores"]["training"]["meanActorStep"] for r in ok) /
                                  len(ok)) if ok else None,
                "carryingGoalL1": (sum(r["scores"]["goalSensitivity"]["carryingL1"]
                                       for r in ok) / len(ok)) if ok else None,
            }
        for label, a, b in CONTRASTS:
            d = [_value(rows[scale, a, s], "train") - _value(rows[scale, b, s], "train")
                 for s in seeds]
            tests.append({"scale": scale, "contrast": label, "minuend": a, "subtrahend": b,
                          "meanDiff": sum(d) / len(d), "ci95": bootstrap(d),
                          "p": sign_flip_p(d)})
    for t, adj in zip(tests, holm([t["p"] for t in tests])):
        t["pHolm"] = adj
        t["significant"] = adj < ALPHA
    goal = next(t for t in tests if t["scale"] == focus and t["contrast"] == "goal-use")
    held = [_value(rows[focus, "native", s], "heldout") -
            _value(rows[focus, "mask-goal", s], "heldout") for s in seeds]
    return {
        "schema": "brain-m0c-frozen-step-credit/1", "sourceCommit": record["commit"],
        "seeds": seeds, "devSelection": {"meanDevSuccessByScale": means, "selected": best,
                         "focusScale": focus},
        "arms": arms, "contrasts": tests,
        "heldoutGoalUse": {"meanDiff": sum(held) / len(held), "ci95": bootstrap(held)},
        "falsifier": {
            "goalConditionalAtSelectedStep": goal["significant"] and goal["meanDiff"] > 0,
            "heldoutAboveGoalBlind": bootstrap(held)[0] > 0,
        },
        "advancement": "HOLD M1-M8: one toy 5x5 family; heldout goals share geometry",
    }


def main():
    if len(sys.argv) not in (2, 3):
        raise SystemExit("usage: python research/analyze_m0c_credit_protocol.py RESULT [OUT]")
    with open(sys.argv[1], encoding="utf-8") as stream:
        summary = summarize(json.load(stream))
    if len(sys.argv) == 3:
        with open(sys.argv[2], "w", encoding="utf-8") as stream:
            json.dump(summary, stream, indent=2, sort_keys=True)
            stream.write("\n")
    print("selected scale", summary["devSelection"]["selected"],
          summary["devSelection"]["meanDevSuccessByScale"])
    for arm, s in summary["arms"].items():
        print(f"{arm:22} train {s['trainSuccess']:.3f} heldout {s['heldoutSuccess']:.3f}"
              f" errors {s['errors']}")
    for t in summary["contrasts"]:
        print(f"x{t['scale']} {t['contrast']:18} diff {t['meanDiff']:+.3f}"
              f" CI {t['ci95']} pHolm {t['pHolm']:.4f}")
    print("falsifier", summary["falsifier"], summary["advancement"])


if __name__ == "__main__":
    main()
