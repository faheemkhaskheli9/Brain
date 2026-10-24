// Shared result file for Brain World experiments (#104): the "brain-result/1" format that
// research/result_schema.py validates and summarises. Every run started is a row, failed or not.
// Usage: writeResult(path, resultRecord({ experiment, config, budgets, metrics, baseline, runs }))
import { execSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import { World } from "./brain.js";

export const SCHEMA = "brain-result/1";

export function gitCommit() {
  try { return execSync("git rev-parse --short HEAD", { stdio: ["ignore", "pipe", "ignore"] }).toString().trim(); } catch { return "unknown"; }
}

// One run row. status: ok | failed (did not reach the goal) | timeout (budget used up) | error (crashed).
export const run = ({ arm, seed, split = null, status, reason = null, seconds = null, scores = {}, checkpoint = null }) =>
  ({ arm, seed, split, status, reason, seconds, scores, checkpoint });

export function resultRecord({ experiment, config, budgets, metrics, baseline = null, runs, environment = {} }) {
  return {
    schema: SCHEMA, experiment, commit: gitCommit(), created: new Date().toISOString().replace(/\.\d+Z$/, "Z"),
    command: ["node", ...process.argv.slice(1).map(a => a.replace(/^.*\/(game\/world|research)\//, "$1/"))].join(" "),
    environment: { runtime: `node ${process.version}`, world: `brain.js save v${new World(0).toJSON().version}`, ...environment },
    config, budgets, metrics, ...(baseline && { baseline }), runs,
  };
}

export const writeResult = (path, record) => writeFileSync(path, JSON.stringify(record, null, 1) + "\n");
