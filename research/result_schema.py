"""Shared result format for learning experiments (#104), version 1.

One JSON file per experiment run. Every run of every arm and seed is a row, including failed,
crashed and budget-exhausted ones, so the denominators are always the runs started:

    {"schema": "brain-result/1", "experiment": "sweep", "commit": "4ac4556",
     "created": "2026-10-24T10:00:00Z", "command": "node game/world/sweep.mjs 1 2 --arms ...",
     "environment": {"runtime": "node v22.11.0", "world": "brain.js save v5"},
     "config": {...the full settings...}, "budgets": {"episodes_per_stage": 20000},
     "metrics": {"total": "lower", "kept.read": "higher"},     # metric -> which direction is better
     "baseline": "rehearse30",                                  # arm the others are paired against
     "runs": [{"arm": "rehearse30", "seed": 1, "split": null,
               "status": "ok" | "failed" | "timeout" | "error",
               "reason": null | "read not learned", "seconds": 812.4,
               "scores": {"total": 6123, "kept": {"read": 0.61, ...}}, "checkpoint": null}, ...]}

JavaScript experiments build the file with game/world/result.mjs; Python ones with make_result().
Stdlib only.

    python research/result_schema.py FILE.json ...        # validate, print a per-arm summary
    python research/result_schema.py --check FILE.json    # validate only (exit 1 if invalid)
"""
import json
import math
import random
import sys
from datetime import datetime, timezone

SCHEMA = "brain-result/1"
STATUSES = ("ok", "failed", "timeout", "error")
REQUIRED = {"schema": str, "experiment": str, "commit": str, "created": str, "command": str,
            "environment": dict, "config": dict, "budgets": dict, "metrics": dict, "runs": list}
RUN_REQUIRED = {"arm": str, "seed": int, "status": str, "scores": dict}


def make_result(experiment, command, config, budgets, metrics, runs, baseline=None, environment=None, commit=None):
    """Build a result record (Python experiments). commit defaults to `git rev-parse --short HEAD`."""
    if commit is None:
        import subprocess
        try:
            commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                                    check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            commit = "unknown"
    env = {"runtime": f"python {sys.version.split()[0]}", **(environment or {})}
    r = {"schema": SCHEMA, "experiment": experiment, "commit": commit,
         "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "command": command,
         "environment": env, "config": config, "budgets": budgets, "metrics": metrics, "runs": runs}
    if baseline is not None:
        r["baseline"] = baseline
    return r


def metric(scores, name):
    """A dotted metric name ("kept.read") read from a run's scores, or None if missing."""
    x = scores
    for part in name.split("."):
        if not isinstance(x, dict) or part not in x:
            return None
        x = x[part]
    return x if isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) else None


def is_null(scores, name):
    """True if the dotted metric is present and explicitly null."""
    *path, last = name.split(".")
    for part in path:
        scores = scores.get(part) if isinstance(scores, dict) else None
    return isinstance(scores, dict) and last in scores and scores[last] is None


def validate(r):
    """Return a list of problems (empty if the record is valid)."""
    if not isinstance(r, dict):
        return ["not a JSON object"]
    errs = [f"{k}: missing or not {t.__name__}" for k, t in REQUIRED.items() if not isinstance(r.get(k), t)]
    if errs:
        return errs
    if r["schema"] != SCHEMA:
        errs.append(f"schema: {r['schema']!r}, expected {SCHEMA!r}")
    for name, d in r["metrics"].items():
        if d not in ("higher", "lower"):
            errs.append(f"metrics.{name}: {d!r}, expected 'higher' or 'lower'")
    if not r["runs"]:
        errs.append("runs: empty")
    arms, seen = set(), set()
    for i, run in enumerate(r["runs"]):
        where = f"runs[{i}]"
        if not isinstance(run, dict):
            errs.append(f"{where}: not an object")
            continue
        bad = [k for k, t in RUN_REQUIRED.items() if not isinstance(run.get(k), t) or isinstance(run.get(k), bool)]
        if bad:
            errs.append(f"{where}: {', '.join(bad)} missing or wrong type")
            continue
        arms.add(run["arm"])
        key = (run["arm"], run["seed"], run.get("split"))
        if key in seen:
            errs.append(f"{where}: duplicate arm/seed/split {key}")
        seen.add(key)
        if run["status"] not in STATUSES:
            errs.append(f"{where}: status {run['status']!r}, expected one of {STATUSES}")
        elif run["status"] != "ok" and not run.get("reason"):
            errs.append(f"{where}: status {run['status']} needs a reason")
        elif run["status"] == "ok":
            # A metric may be null (not measurable in this configuration) but not absent or non-numeric.
            missing = [m for m in r["metrics"] if metric(run["scores"], m) is None and not is_null(run["scores"], m)]
            if missing:
                errs.append(f"{where}: ok run lacks metric(s) {', '.join(missing)}")
    if r.get("baseline") is not None and r["baseline"] not in arms:
        errs.append(f"baseline: {r['baseline']!r} is not an arm")
    return errs


def sign_flip(diffs, rng=None, exact_max=16, samples=20000):
    """Two-sided paired sign-flip p for the mean difference: exact up to exact_max pairs, else sampled."""
    n = len(diffs)
    if n == 0:
        return float("nan")
    obs = abs(sum(diffs)) - 1e-9
    if n <= exact_max:
        hits = sum(abs(sum(-d if m >> i & 1 else d for i, d in enumerate(diffs))) >= obs for m in range(1 << n))
        return hits / (1 << n)
    rng = rng or random.Random(0)
    hits = sum(abs(sum(d if rng.random() < 0.5 else -d for d in diffs)) >= obs for _ in range(samples))
    return (hits + 1) / (samples + 1)


def bootstrap_ci(xs, rng=None, samples=5000, level=0.95):
    """Percentile bootstrap interval for the mean (None for fewer than two values)."""
    if len(xs) < 2:
        return None
    rng = rng or random.Random(0)
    means = sorted(sum(rng.choice(xs) for _ in xs) / len(xs) for _ in range(samples))
    lo = means[int((1 - level) / 2 * samples)]
    hi = means[min(samples - 1, int((1 + level) / 2 * samples))]
    return lo, hi


def summary(r):
    """Per arm (and per split, when runs have one: scores from different tasks are never pooled):
    runs started, ok, and per metric the mean over ok runs with a bootstrap 95% interval; against
    the baseline arm in the same split, the paired mean difference over seeds ok in both, with its
    sign-flip p."""
    groups = list(dict.fromkeys((run.get("split"), run["arm"]) for run in r["runs"]))
    base = r.get("baseline")
    ok = {g: {x["seed"]: x for x in r["runs"] if (x.get("split"), x["arm"]) == g and x["status"] == "ok"} for g in groups}
    out = []
    for split, a in groups:
        runs = [x for x in r["runs"] if (x.get("split"), x["arm"]) == (split, a)]
        statuses = {s: sum(x["status"] == s for x in runs) for s in STATUSES if any(x["status"] == s for x in runs)}
        row = {"arm": a, "split": split, "started": len(runs), "statuses": statuses, "metrics": {}}
        mine, ref = ok[split, a], ok.get((split, base), {})
        for m in r["metrics"]:
            xs = [v for v in (metric(x["scores"], m) for x in mine.values()) if v is not None]
            row["metrics"][m] = {"n": len(xs), "mean": sum(xs) / len(xs) if xs else None, "ci95": bootstrap_ci(xs)}
            if base and a != base:
                shared = [k for k in mine if k in ref and metric(mine[k]["scores"], m) is not None
                          and metric(ref[k]["scores"], m) is not None]
                d = [metric(mine[k]["scores"], m) - metric(ref[k]["scores"], m) for k in shared]
                row["metrics"][m]["vs_baseline"] = {"n": len(d), "diff": sum(d) / len(d) if d else None,
                                                    "p": sign_flip(d) if d else None}
        out.append(row)
    return out


def format_summary(r, rows):
    f = lambda x: "-" if x is None else f"{x:.4g}"   # noqa: E731
    lines = [f"{r['experiment']} at {r['commit']}, {len(r['runs'])} runs; budgets {json.dumps(r['budgets'])}"]
    for row in rows:
        st = ", ".join(f"{k} {v}" for k, v in row["statuses"].items())
        where = f" [{row['split']}]" if row["split"] is not None else ""
        lines.append(f"{row['arm']}{where}: {row['statuses'].get('ok', 0)}/{row['started']} ok ({st})")
        for m, s in row["metrics"].items():
            ci = f" [{f(s['ci95'][0])}, {f(s['ci95'][1])}]" if s["ci95"] else ""
            line = f"  {m} ({r['metrics'][m]} is better): {f(s['mean'])}{ci}, n {s['n']}"
            v = s.get("vs_baseline")
            if v and v["n"]:
                line += f"; vs {r['baseline']} {v['diff']:+.4g} (p {v['p']:.3f}, n {v['n']})"
            lines.append(line)
    return "\n".join(lines)


def main(argv):
    check = "--check" in argv
    paths = [a for a in argv if a != "--check"]
    if not paths:
        print("usage: python research/result_schema.py [--check] FILE.json ...")
        return 2
    bad = 0
    for p in paths:
        with open(p, encoding="utf-8") as fh:
            r = json.load(fh)
        errs = validate(r)
        if errs:
            bad += 1
            print(f"{p}: invalid\n  " + "\n  ".join(errs))
        elif check:
            print(f"{p}: ok")
        else:
            print(format_summary(r, summary(r)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
