"""Integrity check and preregistered tests for the M0c own-step and wide-goal transfer protocol.

Diverged (status "error") rows are preserved and scored as 0 success, never dropped.
Part A: each arm at its own dev-selected matched step. Part B: 19 trained goals, 5 interior
heldout goals, goal-blind ceiling 1/5. Exact paired sign-flip tests, Holm over 5 tests.
"""
import json
import sys

from analyze_m0c_matched_step import (ALPHA, _check_score, _check_training, _parse, bootstrap,
                                      holm, sign_flip_p)

EXPERIMENT = "brain-world/m0c-own-step-transfer-protocol"
ARMS = ("native", "mask-goal", "trace-one-step", "no-hidden")
WIDE_ARMS = ("native", "mask-goal", "flag-only")
OWN_CONTRASTS = (
    ("hidden-layer", "native", "no-hidden"),
    ("eligibility", "native", "trace-one-step"),
    ("goal-use", "native", "mask-goal"),
)
START = (2, 0)


def _pick(curve, grid):
    top = grid[0]
    for e in grid:
        if curve[e] > curve[top] + 1e-12:
            top = e
    return top


def _check_wide(goals):
    train = [tuple(g) for g in goals["train"]]
    held = [tuple(g) for g in goals["heldout"]]
    cells = train + held
    if (len(train) != 19 or len(held) != 5 or len(set(cells)) != 24 or START in cells or
            any(not (1 <= x <= 3 and 1 <= y <= 3) for x, y in held) or
            any(not (0 <= x <= 4 and 0 <= y <= 4) for x, y in cells)):
        raise ValueError("wide goal split invalid")


def _selection(rows, arms, grid, dev, goals, split_key, budget, repeats):
    got = {}
    for row in rows:
        arm, eta = _parse(row["arm"])
        k = (arm, eta, row["seed"])
        if arm not in arms or eta not in grid or row["seed"] not in dev or k in got:
            raise ValueError("invalid selection row")
        if row["status"] == "ok":
            s = row["scores"]
            _check_score(s["dev"], goals[split_key], repeats, arm == "mask-goal")
            _check_training(s["training"], budget, eta)
            got[k] = s["dev"]["success"]
        else:
            got[k] = 0.0
    if set(got) != {(a, e, d) for a in arms for e in grid for d in dev}:
        raise ValueError("missing selection row")
    return {a: {e: sum(got[a, e, d] for d in dev) / len(dev) for e in grid} for a in arms}


def _eval(rows, etas, seeds, goals, budget, repeats):
    got = {}
    for row in rows:
        arm, eta = _parse(row["arm"])
        if arm not in etas or eta != etas[arm] or row["seed"] not in seeds or (arm, row["seed"]) in got:
            raise ValueError("eval row outside the preregistered arm/step")
        got[arm, row["seed"]] = row
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
    if set(got) != {(a, s) for a in etas for s in seeds}:
        raise ValueError("missing eval row")
    return got


def validate(record):
    if record.get("schema") != "brain-result/1" or record.get("experiment") != EXPERIMENT:
        raise ValueError("wrong schema or experiment")
    c = record["config"]
    seeds, dev, repeats = c["seeds"], c["devSeeds"], c["repeats"]
    own, wide = c["own"], c["wide"]
    if (c["arms"] != list(ARMS) or c["wideArms"] != list(WIDE_ARMS) or c["family"] != "one-drop" or
            not seeds or not dev or set(seeds) & set(dev) or
            any(len(set(g)) != len(g) or not g for g in (own["etaGrid"], wide["etaGrid"]))):
        raise ValueError("invalid design or dev/eval seed overlap")
    keys = [",".join(map(str, g)) for split in c["goals"].values() for g in split]
    if len(set(keys)) != len(keys):
        raise ValueError("goal splits overlap")
    _check_wide(c["wideGoals"])
    by = {}
    for row in record["runs"]:
        by.setdefault(row["split"], []).append(row)
    if set(by) != {"own-selection", "own-eval", "wide-selection", "wide-eval"}:
        raise ValueError("unknown or missing split")
    curves = _selection(by["own-selection"], ARMS, own["etaGrid"], dev, c["goals"], "dev",
                        own["budget"], repeats)
    own_eta = {a: _pick(curves[a], own["etaGrid"]) for a in ARMS}
    if own_eta != own["ownEta"]:
        raise ValueError("own step sizes do not follow the preregistered rule")
    wide_curve = _selection(by["wide-selection"], ("native",), wide["etaGrid"], dev,
                            c["wideGoals"], "train", wide["budget"], repeats)["native"]
    selected = _pick(wide_curve, wide["etaGrid"])
    if selected != wide["selected"]:
        raise ValueError("wide step size does not follow the preregistered rule")
    own_rows = _eval(by["own-eval"], own_eta, seeds, c["goals"], own["budget"], repeats)
    wide_rows = _eval(by["wide-eval"], {a: selected for a in WIDE_ARMS}, seeds, c["wideGoals"],
                      wide["budget"], repeats)
    return {"ownRows": own_rows, "wideRows": wide_rows, "ownEta": own_eta, "curves": curves,
            "wideCurve": wide_curve, "wideEta": selected}


def _value(row, split):
    return row["scores"]["after"][split]["success"] if row["status"] == "ok" else 0.0


def _arm_summary(rows, arms, seeds):
    out = {}
    for arm in arms:
        group = [rows[arm, s] for s in seeds]
        train = [_value(r, "train") for r in group]
        held = [_value(r, "heldout") for r in group]
        out[arm] = {"eta": _parse(group[0]["arm"])[1],
                    "errors": sum(r["status"] != "ok" for r in group),
                    "trainSuccess": sum(train) / len(seeds), "trainCi95": bootstrap(train),
                    "heldoutSuccess": sum(held) / len(seeds), "heldoutCi95": bootstrap(held),
                    "perSeedTrain": train, "perSeedHeldout": held}
    return out


def summarize(record):
    v = validate(record)
    c = record["config"]
    seeds, repeats = c["seeds"], c["repeats"]
    own_rows, wide_rows = v["ownRows"], v["wideRows"]
    top = max(c["own"]["etaGrid"])
    tests = []
    for name, a, b in OWN_CONTRASTS:
        d = [_value(own_rows[a, s], "train") - _value(own_rows[b, s], "train") for s in seeds]
        tests.append({"part": "own", "contrast": name, "minuend": f"{a}@{v['ownEta'][a]}",
                      "subtrahend": f"{b}@{v['ownEta'][b]}", "meanDiff": sum(d) / len(d),
                      "ci95": bootstrap(d),
                      "p": sign_flip_p(d, len(c["goals"]["train"]) * repeats),
                      "gridEdge": v["ownEta"][a] == top or v["ownEta"][b] == top})
    wk = {split: len(c["wideGoals"][split]) for split in ("train", "heldout")}
    held_denom = wk["heldout"] * repeats
    above = [_value(wide_rows["native", s], "heldout") - 1 / wk["heldout"] for s in seeds]
    tests.append({"part": "wide", "contrast": "heldout-above-goal-blind", "minuend": "native",
                  "subtrahend": f"1/{wk['heldout']}", "meanDiff": sum(above) / len(above),
                  "ci95": bootstrap(above), "p": sign_flip_p(above, held_denom)})
    gu = [_value(wide_rows["native", s], "heldout") - _value(wide_rows["mask-goal", s], "heldout")
          for s in seeds]
    tests.append({"part": "wide", "contrast": "heldout-goal-use", "minuend": "native",
                  "subtrahend": "mask-goal", "meanDiff": sum(gu) / len(gu), "ci95": bootstrap(gu),
                  "p": sign_flip_p(gu, held_denom)})
    for t, adj in zip(tests, holm([t["p"] for t in tests])):
        t["pHolm"] = adj
        t["significant"] = adj < ALPHA

    def diff(a, b, split):
        d = [_value(wide_rows[a, s], split) - (b if isinstance(b, float) else
                                               _value(wide_rows[b, s], split)) for s in seeds]
        return {"meanDiff": sum(d) / len(d), "ci95": bootstrap(d)}
    get = {t["contrast"]: t for t in tests}

    def verdict(t):
        if t["gridEdge"]:
            return "inconclusive (grid edge)"
        if t["significant"]:
            return "supported" if t["meanDiff"] > 0 else "reversed"
        return "not supported"
    transfer = get["heldout-above-goal-blind"]
    return {
        "schema": "brain-m0c-own-step-transfer/1", "sourceCommit": record["commit"], "seeds": seeds,
        "own": {"ownEta": v["ownEta"], "meanDevSuccessByEta": v["curves"],
                "arms": _arm_summary(own_rows, ARMS, seeds)},
        "wide": {"selected": v["wideEta"], "meanDevSuccessByEta": v["wideCurve"],
                 "goalBlindCeiling": {k: 1 / n for k, n in wk.items()},
                 "arms": _arm_summary(wide_rows, WIDE_ARMS, seeds),
                 "descriptive": {
                     "nativeTrainAboveCeiling": diff("native", 1 / wk["train"], "train"),
                     "flagOnlyHeldoutAboveCeiling": diff("flag-only", 1 / wk["heldout"], "heldout"),
                     "nativeMinusFlagOnlyHeldout": diff("native", "flag-only", "heldout"),
                 }},
        "tests": tests,
        "falsifier": {
            "hiddenLayerAtOwnStep": verdict(get["hidden-layer"]),
            "eligibilityAtOwnStep": verdict(get["eligibility"]),
            "goalUseAtOwnStep": verdict(get["goal-use"]),
            "heldoutTransfer": transfer["significant"] and transfer["meanDiff"] > 0 and
            transfer["ci95"][0] > 0,
        },
        "advancement": "HOLD M1-M8: one toy 5x5 family; heldout goals share geometry",
    }


def main():
    if len(sys.argv) not in (2, 3):
        raise SystemExit("usage: python research/analyze_m0c_own_step_transfer.py RESULT [OUT]")
    with open(sys.argv[1], encoding="utf-8") as stream:
        summary = summarize(json.load(stream))
    if len(sys.argv) == 3:
        with open(sys.argv[2], "w", encoding="utf-8") as stream:
            json.dump(summary, stream, indent=2, sort_keys=True)
            stream.write("\n")
    print("own eta", summary["own"]["ownEta"], "wide eta", summary["wide"]["selected"])
    for part in ("own", "wide"):
        for arm, s in summary[part]["arms"].items():
            print(f"{part} {arm:15} eta {s['eta']} train {s['trainSuccess']:.3f}"
                  f" heldout {s['heldoutSuccess']:.3f} errors {s['errors']}")
    for t in summary["tests"]:
        print(f"{t['contrast']:25} diff {t['meanDiff']:+.3f} CI [{t['ci95'][0]:+.3f},"
              f" {t['ci95'][1]:+.3f}] pHolm {t['pHolm']:.4f}")
    print("descriptive", summary["wide"]["descriptive"])
    print("falsifier", summary["falsifier"], summary["advancement"])


if __name__ == "__main__":
    main()
