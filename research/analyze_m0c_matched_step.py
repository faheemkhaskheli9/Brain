"""Integrity check and preregistered contrasts for the M0c matched-step, one-drop credit protocol.

Diverged (status "error") rows are preserved and scored as 0 success, never dropped.
Contrasts use exact paired sign-flip tests over seeds (integer dynamic programme) with Holm
correction over 3 contrasts x 2 step sizes.
"""
import json
import random
import sys

EXPERIMENT = "brain-world/m0c-matched-step-credit-protocol"
ARMS = ("native", "mask-goal", "trace-one-step", "no-hidden")
# (label, minuend arm, subtrahend arm) on trained-goal frozen success, at both eval step sizes.
CONTRASTS = (
    ("goal-use", "native", "mask-goal"),
    ("eligibility", "native", "trace-one-step"),
    ("hidden-layer", "native", "no-hidden"),
)
ALPHA = 0.05
STEP_TOLERANCE = 1e-9


def bootstrap(values, draws=10000):
    generator = random.Random(20261125)
    n = len(values)
    x = sorted(sum(values[generator.randrange(n)] for _ in range(n)) / n
               for _ in range(draws))
    return [x[int(0.025 * (draws - 1))], x[int(0.975 * (draws - 1))]]


def sign_flip_p(diffs, denominator):
    """Exact two-sided paired sign-flip p-value. Each diff must be an integer / denominator."""
    ints = [round(d * denominator) for d in diffs]
    if any(abs(i - d * denominator) > 1e-6 for i, d in zip(ints, diffs)):
        raise ValueError("differences are not on the episode grid")
    counts = {0: 1}
    for v in ints:
        nxt = {}
        for total, c in counts.items():
            for signed in (v, -v):
                nxt[total + signed] = nxt.get(total + signed, 0) + c
        counts = nxt
    observed = abs(sum(ints))
    return sum(c for total, c in counts.items() if abs(total) >= observed) / 2 ** len(ints)


def holm(pvalues):
    order = sorted(range(len(pvalues)), key=lambda i: pvalues[i])
    adjusted, running = [0.0] * len(pvalues), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(pvalues) - rank) * pvalues[i]))
        adjusted[i] = running
    return adjusted


def _check_score(score, goals, repeats, goal_blind=False):
    n = len(goals) * repeats
    if (score["episodes"] != n or not 0 <= score["deliveries"] <= n or
            score["success"] != score["deliveries"] / n or
            score["goalBlindCeiling"] != 1 / len(goals) or
            sorted(score["perGoal"]) != sorted(",".join(map(str, g)) for g in goals)):
        raise ValueError("score episode/goal mismatch")
    if goal_blind and (score["maxGoalsPerRepeat"] > 1 or
                       score["success"] > 1 / len(goals) + 1e-12):
        raise ValueError("goal-blind arm exceeds the 1/k ceiling: goal leak")


def _check_training(t, budget, eta):
    if (t["decisions"] != budget or t["eta"] != eta or
            not t["maxStepRelDev"] < STEP_TOLERANCE or
            not abs(t["meanActorStep"] - eta) <= STEP_TOLERANCE * eta):
        raise ValueError("training budget or matched step violated")


def _parse(label):
    arm, eta = label.split("@eta")
    return arm, float(eta)


def validate(record):
    if record.get("schema") != "brain-result/1" or record.get("experiment") != EXPERIMENT:
        raise ValueError("wrong schema or experiment")
    c = record["config"]
    seeds, dev, budget, repeats = c["seeds"], c["devSeeds"], c["budget"], c["repeats"]
    goals, grid = c["goals"], c["etaGrid"]
    if (c["arms"] != list(ARMS) or set(seeds) & set(dev) or not seeds or not dev or
            c["family"] != "one-drop" or len(set(grid)) != len(grid) or len(grid) < 2):
        raise ValueError("invalid design or dev/eval seed overlap")
    keys = [",".join(map(str, g)) for split in goals.values() for g in split]
    if len(set(keys)) != len(keys):
        raise ValueError("goal splits overlap")
    selection, rows = {}, {}
    for row in record["runs"]:
        arm, eta = _parse(row["arm"])
        if arm not in ARMS or eta not in grid:
            raise ValueError("unexpected arm or step size")
        if row["split"] == "dev-selection":
            k = (arm, eta, row["seed"])
            if row["seed"] not in dev or k in selection:
                raise ValueError("invalid selection row")
            if row["status"] == "ok":
                s = row["scores"]
                _check_score(s["dev"], goals["dev"], repeats, arm == "mask-goal")
                _check_training(s["training"], budget, eta)
                selection[k] = s["dev"]["success"]
            else:
                selection[k] = 0.0
        elif row["split"] == "eval":
            k = (eta, arm, row["seed"])
            if row["seed"] not in seeds or k in rows:
                raise ValueError("unexpected or duplicate eval row")
            rows[k] = row
        else:
            raise ValueError("unknown split")
    if set(selection) != {(a, e, d) for a in ARMS for e in grid for d in dev}:
        raise ValueError("missing selection row")
    curves = {a: {e: sum(selection[a, e, d] for d in dev) / len(dev) for e in grid}
              for a in ARMS}

    def pick(arm, options):
        top = options[0]
        for e in options:
            if curves[arm][e] > curves[arm][top] + 1e-12:
                top = e
        return top
    best = pick("native", grid)
    second = pick("native", [e for e in grid if e != best])
    if [best, second] != c["evalEtas"] or c["selection"]["selected"] != best:
        raise ValueError("eval step sizes do not follow the preregistered rule")
    for eta in c["evalEtas"]:
        for arm in ARMS:
            for seed in seeds:
                row = rows.get((eta, arm, seed))
                if row is None:
                    raise ValueError("missing eval row")
                if row["status"] != "ok":
                    continue
                s = row["scores"]
                _check_training(s["training"], budget, eta)
                if s["onlineOracleQueries"] != 0 or s["modelBytes"] <= 0:
                    raise ValueError("oracle use or empty model")
                for when in ("before", "after"):
                    for split in ("train", "heldout"):
                        _check_score(s[when][split], goals[split], repeats, arm == "mask-goal")
                if s["primary"] != s["after"]["train"]:
                    raise ValueError("primary metric is not trained-goal success")
                if arm == "mask-goal" and (s["goalSensitivity"]["startL1"] != 0 or
                                           s["goalSensitivity"]["carryingL1"] != 0):
                    raise ValueError("goal mask bypass detected")
    if len(rows) != len(c["evalEtas"]) * len(ARMS) * len(seeds):
        raise ValueError("eval rows outside the preregistered step sizes")
    per_arm_best = {a: pick(a, grid) for a in ARMS}
    return rows, curves, best, second, per_arm_best


def _value(row, split):
    if row["status"] != "ok":
        return 0.0
    return row["scores"]["after"][split]["success"]


def summarize(record):
    rows, curves, best, second, per_arm_best = validate(record)
    c = record["config"]
    seeds, goals = c["seeds"], c["goals"]
    denom = {split: len(goals[split]) * c["repeats"] for split in ("train", "heldout")}
    ceiling = {split: 1 / len(goals[split]) for split in ("train", "heldout")}
    arms, tests = {}, []
    for eta in c["evalEtas"]:
        for arm in ARMS:
            group = [rows[eta, arm, s] for s in seeds]
            ok = [r for r in group if r["status"] == "ok"]
            train = [_value(r, "train") for r in group]
            held = [_value(r, "heldout") for r in group]
            arms[f"{arm}@eta{eta}"] = {
                "errors": len(group) - len(ok),
                "trainSuccess": sum(train) / len(seeds), "trainCi95": bootstrap(train),
                "heldoutSuccess": sum(held) / len(seeds), "heldoutCi95": bootstrap(held),
                "perSeedTrain": train, "perSeedHeldout": held,
                "carryingGoalL1": (sum(r["scores"]["goalSensitivity"]["carryingL1"]
                                       for r in ok) / len(ok)) if ok else None,
            }
        for name, a, b in CONTRASTS:
            d = [_value(rows[eta, a, s], "train") - _value(rows[eta, b, s], "train")
                 for s in seeds]
            tests.append({"eta": eta, "contrast": name, "minuend": a, "subtrahend": b,
                          "meanDiff": sum(d) / len(d), "ci95": bootstrap(d),
                          "p": sign_flip_p(d, denom["train"])})
    for t, adj in zip(tests, holm([t["p"] for t in tests])):
        t["pHolm"] = adj
        t["significant"] = adj < ALPHA

    def above(eta, arm, split):
        d = [_value(rows[eta, arm, s], split) - ceiling[split] for s in seeds]
        return {"meanDiff": sum(d) / len(d), "ci95": bootstrap(d)}

    def get(eta, name):
        return next(t for t in tests if t["eta"] == eta and t["contrast"] == name)
    goal = get(best, "goal-use")
    native_above = above(best, "native", "train")
    held = [_value(rows[best, "native", s], "heldout") -
            _value(rows[best, "mask-goal", s], "heldout") for s in seeds]
    mechanisms = {}
    for name in ("eligibility", "hidden-layer"):
        a, b = get(best, name), get(second, name)
        same = a["significant"] and b["significant"] and (a["meanDiff"] > 0) == (b["meanDiff"] > 0)
        mechanisms[name] = ("supported" if same else
                            "step-size dependent" if a["significant"] or b["significant"]
                            else "not supported")
    return {
        "schema": "brain-m0c-matched-step-credit/1", "sourceCommit": record["commit"],
        "seeds": seeds,
        "devSelection": {"meanDevSuccessByEta": curves, "selected": best, "second": second,
                         "perArmBest": per_arm_best},
        "goalBlindCeiling": ceiling, "arms": arms, "contrasts": tests,
        "nativeAboveCeiling": {"train": native_above,
                               "heldout": above(best, "native", "heldout")},
        "heldoutGoalUse": {"meanDiff": sum(held) / len(held), "ci95": bootstrap(held)},
        "falsifier": {
            "goalConditionalAtSelectedStep": (goal["significant"] and goal["meanDiff"] > 0 and
                                              native_above["ci95"][0] > 0),
            "heldoutAboveGoalBlind": bootstrap(held)[0] > 0,
            "mechanisms": mechanisms,
        },
        "advancement": "HOLD M1-M8: one toy 5x5 family; heldout goals share geometry",
    }


def main():
    if len(sys.argv) not in (2, 3):
        raise SystemExit("usage: python research/analyze_m0c_matched_step.py RESULT [OUT]")
    with open(sys.argv[1], encoding="utf-8") as stream:
        summary = summarize(json.load(stream))
    if len(sys.argv) == 3:
        with open(sys.argv[2], "w", encoding="utf-8") as stream:
            json.dump(summary, stream, indent=2, sort_keys=True)
            stream.write("\n")
    d = summary["devSelection"]
    print("selected eta", d["selected"], "second", d["second"], "per-arm best", d["perArmBest"])
    for arm, s in summary["arms"].items():
        print(f"{arm:26} train {s['trainSuccess']:.3f} heldout {s['heldoutSuccess']:.3f}"
              f" errors {s['errors']}")
    for t in summary["contrasts"]:
        print(f"eta {t['eta']} {t['contrast']:13} diff {t['meanDiff']:+.3f}"
              f" CI [{t['ci95'][0]:+.3f}, {t['ci95'][1]:+.3f}] pHolm {t['pHolm']:.4f}")
    print("native above 1/k", summary["nativeAboveCeiling"])
    print("falsifier", summary["falsifier"], summary["advancement"])


if __name__ == "__main__":
    main()
