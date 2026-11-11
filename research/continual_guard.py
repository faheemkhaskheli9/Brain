"""Integrity gates for committed continual-learning experiments (#154).

These are reproducible data-integrity checks, NOT a replacement for re-running the
live learner. Full scientific benchmarking remains in heldout.mjs/reversal.mjs.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from result_schema import validate

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/results/continual-baseline-v1.json"


def _git_blob_sha(raw: bytes) -> str:
    """Git SHA-1 blob ID pins the exact archived experiment, including failed rows."""
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def _fraction(value) -> bool:
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and 0 <= value <= 1)


def _score_error(prefix: str, value, errors: list[str]) -> None:
    if not _fraction(value):
        errors.append(f"{prefix}: must be finite and between 0 and 1")


def check_checkpoint(run: dict, root: Path = ROOT) -> list[str]:
    """Validate a checkpoint reference if one is present; absent refs are not invented."""
    ref = run.get("checkpoint")
    if ref is None:
        return []
    if not isinstance(ref, dict) or not isinstance(ref.get("path"), str):
        return ["checkpoint: expected path and sha256"]
    name, digest = ref["path"], ref.get("sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        return ["checkpoint: invalid sha256"]
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts:
        return ["checkpoint: path must stay inside repository"]
    path = root / relative
    if path.is_symlink() or not path.is_file():
        return ["checkpoint: missing file or symlink"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        return ["checkpoint: sha256 mismatch"]
    return []


def check_record(record: dict, spec: dict) -> list[str]:
    """Validate semantics beyond brain-result/1 and protect known negative results."""
    errors = validate(record)
    if errors:
        return errors
    kind = spec["kind"]
    if record["experiment"] != spec["experiment"] or record.get("baseline") != spec["baseline"]:
        errors.append("experiment or baseline changed")
    seeds = set(spec["seeds"])
    expected = {(arm, seed) for arm in spec["arms"] for seed in seeds}
    expected -= {tuple(item) for item in spec.get("not_started", [])}
    actual = {(r["arm"], r["seed"]) for r in record["runs"]}
    if actual != expected:
        errors.append(f"arm/seed coverage changed: missing {sorted(expected - actual)}, extra {sorted(actual - expected)}")
    for r in record["runs"]:
        key = f"{r['arm']}/{r['seed']}"
        if r["status"] != spec.get("statuses", {}).get(key, "ok"):
            errors.append(f"{key}: failure/timeout status changed")
        errors += [f"{key}: {e}" for e in check_checkpoint(r)]
    config, budgets = record["config"], record["budgets"]
    if set(config.get("seeds", [])) != seeds:
        errors.append("configuration seeds changed")
    if kind == "heldout":
        splits = config.get("splits", {})
        layout = splits.get("layout", {})
        if layout != {"train": [0, 1], "dev": [2], "eval": [3]}:
            errors.append("layout splits changed or overlap")
        glyph = splits.get("glyph", {})
        if (set(glyph.get("train", [])) & set(glyph.get("eval", []))
                or len(glyph.get("train", [])) != 3 or len(glyph.get("eval", [])) != 3):
            errors.append("glyph train/eval overlap or wrong size")
        tone = splits.get("tone", {})
        if tone.get("train") == tone.get("eval") or not tone.get("eval"):
            errors.append("tone train/eval overlap")
        if budgets.get("adapt_episodes") != 2000 or budgets.get("eval_episodes") != 300:
            errors.append("held-out evaluation/adaptation budget changed")
        for r in record["runs"]:
            if r["status"] != "ok" or r["arm"] != "pretrained":
                continue
            scores = r["scores"]
            for axis, source in (("tone", "listen"), ("glyph", "copy")):
                row = scores.get(axis)
                if not isinstance(row, dict):
                    errors.append(f"{r['seed']}: missing {axis} results")
                    continue
                before, after, forgetting = (row.get(f"{source}Before"),
                                             row.get(f"{source}After"), row.get("forgetting"))
                _score_error(f"{r['seed']} {axis} sourceBefore", before, errors)
                _score_error(f"{r['seed']} {axis} sourceAfter", after, errors)
                if all(isinstance(v, (int, float)) for v in (before, after, forgetting)):
                    if abs((before - after) - forgetting) > 1e-6:
                        errors.append(f"{r['seed']} {axis} forgetting inconsistent with retention")
                for m in ("zeroShot", "adapted"):
                    _score_error(f"{r['seed']} {axis}.{m}", row.get(m), errors)
            for skill in ("grasp", "listen", "read"):
                layout_scores = scores.get("layout", {}).get(skill, {})
                for split in ("train", "dev", "eval"):
                    _score_error(f"{r['seed']} {skill}.{split}", layout_scores.get(split), errors)
                train, evaluation = layout_scores.get("train"), layout_scores.get("eval")
                gap = scores.get("gap", {}).get(skill)
                if all(isinstance(v, (int, float)) for v in (train, evaluation, gap)):
                    if abs((evaluation - train) - gap) > 1e-6:
                        errors.append(f"{r['seed']} {skill}: eval/train gap inconsistent")
    elif kind == "reversal":
        block_count = budgets.get("blocks")
        if block_count != 8 or budgets.get("episodes_per_block") != 300:
            errors.append("reversal block budget changed")
        if config.get("window") != 20 or config.get("late") != 50:
            errors.append("reversal metric window changed")
        for r in record["runs"]:
            if r["status"] != "ok":
                continue
            scores = r["scores"]
            blocks = scores.get("blocks")
            if not isinstance(blocks, list) or len(blocks) != 8:
                errors.append(f"{r['arm']}/{r['seed']}: missing reversal blocks")
                continue
            for i, b in enumerate(blocks):
                if b.get("key") != ("reverse" if i % 2 == 0 else "listen") or b.get("n") != 300:
                    errors.append(f"{r['arm']}/{r['seed']}: reversed-rule block sequence changed")
                for m in ("first", "ok"):
                    _score_error(f"{r['arm']}/{r['seed']} block {i} {m}", b.get(m), errors)
            listen_returns = [b["first"] for b in blocks[2:] if b["key"] == "listen"]
            if len(listen_returns) != 3 or not isinstance(scores.get("retention"), (int, float)):
                errors.append(f"{r['arm']}/{r['seed']}: missing retention")
            elif abs(sum(listen_returns) / 3 - scores["retention"]) > 0.001:
                errors.append(f"{r['arm']}/{r['seed']}: retention disagrees with per-block data")
    elif kind == "replay":
        # 10-seed sampler comparison (#152): every control arm, equal budgets, timeouts kept.
        if budgets.get("episodes_per_stage") != 20000 or budgets.get("scored_episodes") != 4000:
            errors.append("replay training/scoring budget changed")
        for arm, settings in config.get("arms", {}).items():
            if settings.get("replay") != 0.1 or settings.get("sleepActor", False):
                errors.append(f"{arm}: unequal online rehearsal or replaying actor")
        for r in record["runs"]:
            if r["status"] != "ok":
                continue
            kept = r["scores"].get("kept")
            if not isinstance(kept, dict):
                errors.append(f"{r['arm']}/{r['seed']}: missing retention")
                continue
            for skill in ("grasp", "listen", "read", "write"):
                _score_error(f"{r['arm']}/{r['seed']} kept.{skill}", kept.get(skill), errors)
    elif kind == "rl-multitask":
        # Shared-network comparator (#153): no task ID, creature-matched budget, all skills scored.
        if "no task ID" not in str(config.get("taskInput", "")):
            errors.append("shared learner input no longer excludes the task ID")
        if budgets.get("matchCreature") is not True or budgets.get("evalEpisodesPerSkill") != 300:
            errors.append("multi-task budget matching or evaluation size changed")
        skills = spec["splits"]
        seen = {}
        for r in record["runs"]:
            seen.setdefault((r["arm"], r["seed"]), []).append(r.get("split"))
            if r["status"] == "ok":
                _score_error(f"{r['arm']}/{r['seed']} {r.get('split')} success",
                             r["scores"].get("success"), errors)
        for key, splits in seen.items():
            if sorted(splits) != sorted(skills):
                errors.append(f"{key[0]}/{key[1]}: skill coverage changed")
        effective = budgets.get("effectivePerSeed", {})
        for r in record["runs"]:
            if r["arm"].startswith("shared-") or r["arm"] == "separate":
                want = effective.get(str(r["seed"]))
                got = r["scores"].get("trainSteps")
                # An episode may overshoot the budget, never undershoot it.
                if not isinstance(want, int) or not isinstance(got, int) or got < want:
                    errors.append(f"{r['arm']}/{r['seed']} {r.get('split')}: trained under the matched budget")
    else:
        errors.append(f"unsupported experiment kind {kind}")
    return errors


def check_files(manifest: Path = MANIFEST) -> list[str]:
    """Check all pinned result files; upgrading a baseline requires reviewing manifest."""
    specs = json.loads(manifest.read_text(encoding="utf-8"))["fixtures"]
    errors = []
    for spec in specs:
        path = ROOT / spec["path"]
        raw = path.read_bytes()
        if _git_blob_sha(raw) != spec["git_blob_sha"]:
            errors.append(f"{spec['path']}: archived fixture bytes changed (review before updating pin)")
        try:
            record = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"{spec['path']}: invalid JSON: {exc}")
            continue
        errors.extend(f"{spec['path']}: {e}" for e in check_record(record, spec))
    return errors


if __name__ == "__main__":
    problems = check_files()
    for problem in problems:
        print("FAIL", problem)
    print(f"Continual-learning archive integrity: {'FAIL' if problems else 'OK'}")
    raise SystemExit(bool(problems))
