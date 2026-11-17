"""Reproducible paired fixed-task calibration analysis, no AGI or transfer claim."""
import argparse
import json
from pathlib import Path

from analyze_m0c_controls import paired_ci
from check_m0c_calibration import ARMS, check


def summarize(record):
    rows = check(record)
    seeds = record["config"]["seeds"]
    results = {}
    for arm in ARMS:
        # The ordered checkpoint curve is the canonical evidence; avoid
        # relying on convenience before/after aliases missing from minimal fixtures.
        before = [rows[s, arm]["curve"][0]["calibration"]["success"] for s in seeds]
        after = [rows[s, arm]["curve"][-1]["calibration"]["success"] for s in seeds]
        variants = [
            rows[s, arm]["curve"][-1]["diagnosticVariants"]["success"] for s in seeds
        ]
        gain = [a - b for a, b in zip(after, before)]
        results[arm] = {
            "beforeSuccess": sum(before) / len(seeds),
            "afterSuccess": sum(after) / len(seeds),
            "afterCi95": paired_ci(after),
            "pairedGain": sum(gain) / len(seeds),
            "pairedGainCi95": paired_ci(gain),
            "variantSuccess": sum(variants) / len(seeds),
            "variantCi95": paired_ci(variants),
            "totalTrainingDecisions": sum(rows[s, arm]["trainDecisions"] for s in seeds),
            "totalTrainingEnvironmentSteps": sum(
                rows[s, arm]["trainEnvSteps"] for s in seeds
            ),
            "successfulTrainingPickups": sum(
                rows[s, arm]["training"]["pickups"] for s in seeds
            ),
            "successfulTrainingDeliveries": sum(
                rows[s, arm]["training"]["successes"] for s in seeds
            ),
        }
    difference = [
        rows[s, "flat-brain"]["curve"][-1]["calibration"]["success"] -
        rows[s, "q-relative"]["curve"][-1]["calibration"]["success"]
        for s in seeds
    ]
    return {
        "schema": "brain-m0c-fixed-calibration-analysis/1",
        "sourceCommit": record["commit"],
        "sourceExperiment": record["experiment"],
        "seeds": seeds,
        "checkpointDecisions": record["config"]["checkpoints"],
        "metric": "physical delivered item (same repeated training task)",
        "arms": results,
        "brainMinusRelativeQ": sum(difference) / len(seeds),
        "brainMinusRelativeQCi95": paired_ci(difference),
        "promotionDecision": "HOLD: no sealed structural transfer or retention evidence",
        "limitations": [
            "single repeatedly trained geometry, not independent transfer",
            "relative Q embeds supplied goal-coordinate expertise",
            "potential shaping is supplied feedback and not part of native rewards",
            "different model sizes/inductive biases, no controlled causal conclusion",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = json.loads(args.result.read_text(encoding="utf-8"))
    analysis = summarize(result)
    body = json.dumps(analysis, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(body, encoding="utf-8")
    for name, a in analysis["arms"].items():
        print(name, "before", round(a["beforeSuccess"], 4),
              "after", round(a["afterSuccess"], 4),
              "after CI95", a["afterCi95"],
              "nearby", round(a["variantSuccess"], 4))
    print("Brain vs relative Q:", analysis["brainMinusRelativeQ"],
          analysis["brainMinusRelativeQCi95"])
    print(analysis["promotionDecision"])


if __name__ == "__main__":
    main()
