"""Experiment comparison dashboard (#107): reads brain-result/1 files (#104), never prose.

One static HTML page: per file, the commit, command, budgets and full config; per arm (and split)
runs started and ok, each metric's mean with a bootstrap 95% interval and the paired difference to
the baseline arm with its sign-flip p; every seed's status, reason and values, failed runs included;
a dot plot of the per-seed values. Files of the same experiment whose budgets, world version or
config (seeds aside) differ are flagged as not comparable, and so are missing, unreadable and
invalid files: they are listed, never dropped silently.

Exports hold exactly what the page shows: --csv one row per run and metric (the values the
summaries are computed from), --json the records as read plus their summaries and flags.
Stdlib only.

    python research/dashboard.py [FILE.json ...] [--html OUT.html] [--csv OUT.csv] [--json OUT.json]

With no files it reads research/results/*.json. With no output it prints the files and flags.
"""
import csv
import glob
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import result_schema as rs  # noqa: E402

CSV_FIELDS = ["file", "experiment", "commit", "created", "arm", "split", "seed", "status", "reason", "metric",
              "better", "value"]


def load(paths):
    """[(path, record or None, problems)] in the order given. A record is kept only if valid."""
    out = []
    for p in paths:
        try:
            with open(p, encoding="utf-8") as fh:
                r = json.load(fh)
        except FileNotFoundError:
            out.append((p, None, ["missing"]))
            continue
        except (OSError, ValueError) as e:
            out.append((p, None, [f"unreadable: {e}"]))
            continue
        errs = rs.validate(r)
        out.append((p, None if errs else r, errs))
    return out


def flags(loaded):
    """Problems a reader must see: bad files, and same-experiment files that are not comparable."""
    out = [f"{p}: {'; '.join(errs)}" for p, r, errs in loaded if r is None]
    by_exp = {}
    for p, r, _ in loaded:
        if r is not None:
            by_exp.setdefault(r["experiment"], []).append((p, r))
    for exp, files in by_exp.items():
        if len(files) < 2:
            continue
        for what, get in [("budgets", lambda r: r["budgets"]),
                          ("world version", lambda r: r["environment"].get("world")),
                          ("config (seeds aside)", lambda r: {k: v for k, v in r["config"].items() if k != "seeds"})]:
            seen = {}
            for p, r in files:
                seen.setdefault(json.dumps(get(r), sort_keys=True), []).append(os.path.basename(p))
            if len(seen) > 1:
                out.append(f"{exp}: {what} differ between " + " / ".join(", ".join(v) for v in seen.values())
                           + "; do not compare these files directly")
    return out


def rows(loaded):
    """One row per run and metric of every valid file: the exact values the summaries use."""
    out = []
    for p, r, _ in loaded:
        if r is None:
            continue
        for run in r["runs"]:
            for m, better in r["metrics"].items():
                out.append({"file": os.path.basename(p), "experiment": r["experiment"], "commit": r["commit"],
                            "created": r["created"], "arm": run["arm"], "split": run.get("split"), "seed": run["seed"],
                            "status": run["status"], "reason": run.get("reason"), "metric": m, "better": better,
                            "value": rs.metric(run["scores"], m)})
    return out


def write_csv(path, data):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, CSV_FIELDS, lineterminator="\n")
        w.writeheader()
        for row in data:
            w.writerow({k: "" if row[k] is None else row[k] for k in CSV_FIELDS})


def export_json(loaded):
    return {"files": [{"file": p, "problems": errs, "record": r, "summary": rs.summary(r) if r else None}
                      for p, r, errs in loaded],
            "flags": flags(loaded)}


def fmt(x):
    return "–" if x is None else f"{x:.3g}"


def dots(values_by_arm, width=260):
    """Inline SVG: one row per arm, one dot per seed, a bar at the mean."""
    vals = [v for vs in values_by_arm.values() for _, v in vs]
    if not vals:
        return ""
    lo, hi = min(vals), max(vals)
    span = hi - lo or 1
    x = lambda v: 70 + (v - lo) / span * (width - 80)   # noqa: E731
    h, parts = 16, []
    for i, (arm, vs) in enumerate(values_by_arm.items()):
        y = 10 + i * h
        parts.append(f'<text x="0" y="{y + 4}">{html.escape(arm[:10])}</text>')
        for seed, v in vs:
            parts.append(f'<circle cx="{x(v):.1f}" cy="{y}" r="3"><title>seed {seed}: {v:.4g}</title></circle>')
        if vs:
            m = sum(v for _, v in vs) / len(vs)
            parts.append(f'<line class="mean" x1="{x(m):.1f}" x2="{x(m):.1f}" y1="{y - 6}" y2="{y + 6}"/>')
    hgt = 10 + len(values_by_arm) * h
    parts.append(f'<text x="70" y="{hgt + 8}">{fmt(lo)}</text><text x="{width}" y="{hgt + 8}" text-anchor="end">{fmt(hi)}</text>')
    return f'<svg class="dots" viewBox="0 0 {width + 4} {hgt + 12}" role="img">{"".join(parts)}</svg>'


CSS = """:root{--ink:#222;--muted:#666;--line:#ddd;--bg:#fff;--warn:#fff4e5;--dot:#4a55c8}
@media (prefers-color-scheme:dark){:root{--ink:#e8e8e8;--muted:#aaa;--line:#444;--bg:#151515;--warn:#3a2c12;--dot:#9aa4ff}}
body{font:14px/1.45 system-ui,sans-serif;color:var(--ink);background:var(--bg);margin:0 auto;max-width:1100px;padding:16px}
table{border-collapse:collapse;margin:8px 0 16px;display:block;overflow-x:auto}td,th{border-bottom:1px solid var(--line);
padding:3px 8px;text-align:left;vertical-align:top}th{font-weight:600}.warn{background:var(--warn);padding:8px 12px}
.muted{color:var(--muted)}pre{white-space:pre-wrap;font-size:12px}.dots{width:280px;font-size:10px;fill:var(--ink)}
.dots circle{fill:var(--dot);fill-opacity:.6}.dots .mean{stroke:var(--ink);stroke-width:2}.bad{color:#c33}"""


def page(loaded):
    e = html.escape
    out = ["<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>",
           f"<title>Experiment results</title><style>{CSS}</style><h1>Experiment results</h1>",
           "<p class=muted>Built from brain-result/1 files by research/dashboard.py. Means over ok runs with "
           "bootstrap 95% intervals; differences are paired by seed against the baseline arm (sign-flip p).</p>"]
    fl = flags(loaded)
    if fl:
        out.append("<div class=warn><b>Check before comparing</b><ul>" + "".join(f"<li>{e(f)}</li>" for f in fl) + "</ul></div>")
    for p, r, _ in loaded:
        if r is None:
            continue
        out.append(f"<h2>{e(r['experiment'])} <span class=muted>{e(os.path.basename(p))}</span></h2>")
        out.append(f"<p>commit <code>{e(r['commit'])}</code>, {e(r['created'])}, {e(json.dumps(r['environment']))}<br>"
                   f"<code>{e(r['command'])}</code><br>budgets <code>{e(json.dumps(r['budgets']))}</code>"
                   + (f", baseline <b>{e(r['baseline'])}</b>" if r.get("baseline") else "") + "</p>")
        out.append(f"<details><summary>config</summary><pre>{e(json.dumps(r['config'], indent=1))}</pre></details>")
        summ = rs.summary(r)
        head = "".join(f"<th>{e(m)} <span class=muted>({e(d)})</span></th>" for m, d in r["metrics"].items())
        out.append(f"<table><tr><th>arm</th><th>ok / started</th>{head}</tr>")
        for row in summ:
            where = f" [{e(str(row['split']))}]" if row["split"] is not None else ""
            cells = []
            for m in r["metrics"]:
                s = row["metrics"][m]
                ci = f" [{fmt(s['ci95'][0])}, {fmt(s['ci95'][1])}]" if s["ci95"] else ""
                v = s.get("vs_baseline")
                vs = f"<br><span class=muted>{v['diff']:+.3g}, p {v['p']:.3f}, n {v['n']}</span>" if v and v["n"] else ""
                cells.append(f"<td>{fmt(s['mean'])}{ci} <span class=muted>n {s['n']}</span>{vs}</td>")
            st = ", ".join(f"{k} {n}" for k, n in row["statuses"].items())
            out.append(f"<tr><td>{e(row['arm'])}{where}</td><td>{row['statuses'].get('ok', 0)} / {row['started']}"
                       f" <span class=muted>{e(st)}</span></td>{''.join(cells)}</tr>")
        out.append("</table><details><summary>per-metric seeds</summary>")
        for m in r["metrics"]:
            by_arm = {}
            for run in r["runs"]:
                v = rs.metric(run["scores"], m) if run["status"] == "ok" else None
                arm = run["arm"] + (f" [{run['split']}]" if run.get("split") is not None else "")
                by_arm.setdefault(arm, [])
                if v is not None:
                    by_arm[arm].append((run["seed"], v))
            out.append(f"<p>{e(m)}<br>{dots(by_arm)}</p>")
        out.append("</details><details><summary>every run</summary><table><tr><th>arm</th><th>seed</th><th>status</th>"
                   + "".join(f"<th>{e(m)}</th>" for m in r["metrics"]) + "<th>seconds</th></tr>")
        for run in r["runs"]:
            cls = "" if run["status"] == "ok" else " class=bad"
            reason = f" ({e(run['reason'])})" if run.get("reason") else ""
            vals = "".join(f"<td>{fmt(rs.metric(run['scores'], m))}</td>" for m in r["metrics"])
            out.append(f"<tr{cls}><td>{e(run['arm'])}</td><td>{run['seed']}</td><td>{e(run['status'])}{reason}</td>"
                       f"{vals}<td>{fmt(run.get('seconds'))}</td></tr>")
        out.append("</table></details>")
    return "\n".join(out) + "\n"


def main(argv):
    opts, paths, i = {}, [], 0
    while i < len(argv):
        if argv[i] in ("--html", "--csv", "--json"):
            if i + 1 >= len(argv):
                print(f"{argv[i]} needs a file name")
                return 2
            opts[argv[i]] = argv[i + 1]
            i += 2
        else:
            paths.append(argv[i])
            i += 1
    paths = paths or sorted(glob.glob(os.path.join(HERE, "results", "*.json")))
    loaded = load(paths)
    if "--html" in opts:
        with open(opts["--html"], "w", encoding="utf-8") as fh:
            fh.write(page(loaded))
    if "--csv" in opts:
        write_csv(opts["--csv"], rows(loaded))
    if "--json" in opts:
        with open(opts["--json"], "w", encoding="utf-8") as fh:
            json.dump(export_json(loaded), fh, indent=1)
            fh.write("\n")
    for p, r, errs in loaded:
        print(f"{p}: {'ok' if r else 'skipped: ' + '; '.join(errs)}")
    for f in flags(loaded):
        print(f"flag: {f}")
    return 1 if any(r is None for _, r, _ in loaded) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
