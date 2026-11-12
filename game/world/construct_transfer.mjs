// Backprop-free construction transfer *pilot*, not evidence of AGI or reusable options.
// Existing constraint-family splits are frozen; adapt and final-evaluation instances are disjoint.
import {createHash} from "node:crypto";
import {pathToFileURL} from "node:url";
import {Brain, rng} from "./brain.js";
import {assertDisjoint, comboKey, generate, solutions, valid} from "./construct.mjs";
import {playEpisode, frozenScore, PROVENANCE} from "./construct_learner.mjs";
import {pictureClass} from "./novelty.mjs";
import {randomLegal} from "./novelty_fair.mjs";
import {resultRecord, run, writeResult} from "./result.mjs";

export const ARMS = Object.freeze(["pretrained", "scratch", "goal-masked", "frozen", "random-valid"]);
export const signature = t => comboKey(t) + ":" + t.points.map(([r,c]) => r * 5 + c).join(",");
const unique = arr => {
  const seen = new Set();
  return arr.filter(t => {const k = signature(t); if (seen.has(k)) return false; seen.add(k); return true;});
};

export function partitions(seed, trainN, adaptN, evalN) {
  assertDisjoint();
  if (![trainN, adaptN, evalN].every(n => Number.isInteger(n) && n > 0)) throw Error("invalid task counts");
  const train = unique(generate(seed, "train", trainN * 6).tasks).slice(0, trainN);
  const rest = unique(generate(seed + 100003, "eval", (adaptN + evalN) * 6).tasks);
  const adapt = rest.slice(0, adaptN), heldout = rest.slice(adaptN, adaptN + evalN);
  if (train.length !== trainN || adapt.length !== adaptN || heldout.length !== evalN)
    throw Error("insufficient unique tasks; cannot pad a split with repeats");
  const old = new Set(train.map(comboKey)), a = new Set(adapt.map(signature));
  if ([...adapt, ...heldout].some(t => old.has(comboKey(t))) ||
      heldout.some(t => a.has(signature(t)))) throw Error("construction train/adapt/eval overlap");
  return {train, adapt, heldout};
}

// Frozen measurement must neither update weights nor consume the training RNG stream.
function score(brain, tasks, repeats, seed, opts = {}) {
  const state = brain.rand.state;
  brain.rand.state = seed >>> 0;
  try { return frozenScore(brain, tasks, repeats, opts); }
  finally { brain.rand.state = state; }
}
function train(brain, tasks, budget, revealGoal, seed, learn = true) {
  const choose = rng(seed >>> 0);
  let decisions = 0, episodes = 0, wins = 0;
  while (decisions < budget) {
    const task = tasks[Math.floor(choose() * tasks.length)];
    const e = playEpisode(brain, task, {learn, revealGoal});
    decisions += e.decisions; episodes++; wins += Number(e.success);
  }
  return {decisions, episodes, success: wins / episodes};
}
function randomScore(tasks, repeats, seed, excluded) {
  // Compare novelty against the same complete training-solution exclusion used by learners.
  const R = rng(seed >>> 0), seen = new Set(excluded);
  let wins = 0, novel = 0, decisions = 0;
  for (const task of tasks) for (let i = 0; i < repeats; i++) {
    const strokes = randomLegal(R, task.budget);
    decisions += strokes.length;
    if (valid(task, strokes)) {
      wins++; const picture = pictureClass(strokes);
      if (!seen.has(picture)) {seen.add(picture); novel++;}
    }
  }
  return {success: wins / (tasks.length * repeats), novel: novel / (tasks.length * repeats), decisions};
}

export function runSeed(seed, cfg = {}) {
  const {trainSteps = 10000, adaptSteps = 2000, trainTasks = 64, adaptTasks = 12,
    evalTasks = 30, repeats = 5} = cfg;
  if (!Number.isSafeInteger(seed) || seed < 0 ||
      ![trainSteps,adaptSteps,trainTasks,adaptTasks,evalTasks,repeats].every(n => Number.isInteger(n) && n > 0))
    throw Error("invalid budget or seed");
  const {train: old, adapt, heldout} = partitions(seed,trainTasks,adaptTasks,evalTasks);
  const digest = createHash("sha256").update(JSON.stringify({
    train: old.map(signature), adapt: adapt.map(signature), heldout: heldout.map(signature)
  })).digest("hex");
  const known = new Set(old.flatMap(t => solutions(t)).map(pictureClass));
  const rows = [];
  for (const arm of ARMS) {
    const start = Date.now();
    try {
      if (arm === "random-valid") {
        const r = randomScore(heldout,repeats,seed * 13 + 59,known);
        rows.push(run({arm,seed,split:"unseen-combinations",status:"ok",seconds:(Date.now()-start)/1000,
          scores:{zeroShot:r.success,adapted:r.success,gain:0,newDrawing:r.novel,oldBefore:0,oldAfter:0,
            forgetting:0,trainDecisions:0,adaptDecisions:0,evalDecisions:r.decisions}}));
        continue;
      }
      const brain = new Brain(rng(seed * 7919 + 41));
      const revealGoal = arm !== "goal-masked";
      let trained = {decisions:0,success:0};
      if (arm !== "scratch") trained = train(brain,old,trainSteps,revealGoal,seed*1741+17);
      // Common adaptation RNG seed even though the learned policies differ.
      brain.rand.state = (seed ^ 0x9e3779b9) >>> 0;
      const familiar = old.slice(0,Math.min(old.length,evalTasks));
      const oldBefore = score(brain,familiar,repeats,seed*101+7,{revealGoal});
      const initial = score(brain,heldout,repeats,seed*103+11,{revealGoal,seen:known});
      const adaptedTraining = train(brain,adapt,adaptSteps,revealGoal,seed*1777+19,arm!=="frozen");
      const final = score(brain,heldout,repeats,seed*103+11,{revealGoal,seen:known});
      const oldAfter = score(brain,familiar,repeats,seed*101+7,{revealGoal});
      rows.push(run({arm,seed,split:"unseen-combinations",status:"ok",seconds:(Date.now()-start)/1000,
        scores:{zeroShot:initial.success,adapted:final.success,gain:final.success-initial.success,
          newDrawing:final.novel,oldBefore:oldBefore.success,oldAfter:oldAfter.success,
          forgetting:oldBefore.success-oldAfter.success,trainDecisions:trained.decisions,
          adaptDecisions:adaptedTraining.decisions,
          evalDecisions:oldBefore.decisions+initial.decisions+final.decisions+oldAfter.decisions,
          trainingSuccess:trained.success,adaptationSuccess:adaptedTraining.success}}));
    } catch(e) {
      rows.push(run({arm,seed,split:"unseen-combinations",status:"error",
        reason:String(e?.message||e),seconds:(Date.now()-start)/1000,scores:{}}));
    }
  }
  return {rows,digest};
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = process.argv.slice(2);
  const option = (flag,def) => {const i=args.indexOf(flag);return i<0?def:args.splice(i,2)[1];};
  const trainSteps=Number(option("--train-steps","10000")), adaptSteps=Number(option("--adapt-steps","2000"));
  const trainTasks=Number(option("--train-tasks","64")),adaptTasks=Number(option("--adapt-tasks","12"));
  const evalTasks=Number(option("--eval-tasks","30")),repeats=Number(option("--repeats","5"));
  const out=option("--out",null), seeds=args.length?args.map(Number):[1,2,3];
  if (!out || !seeds.length || new Set(seeds).size!==seeds.length ||
      seeds.some(s=>!Number.isSafeInteger(s)||s<0) ||
      ![trainSteps,adaptSteps,trainTasks,adaptTasks,evalTasks,repeats].every(Number.isInteger) ||
      Math.min(trainSteps,adaptSteps,trainTasks,adaptTasks,evalTasks,repeats)<1)
    throw Error("usage: node game/world/construct_transfer.mjs --out FILE.json [--train-steps N] [--adapt-steps N] [seed ...]");
  const cfg={trainSteps,adaptSteps,trainTasks,adaptTasks,evalTasks,repeats};
  const groups=seeds.map(seed=>{try{return runSeed(seed,cfg);}catch(e){
    return {digest:null,rows:ARMS.map(arm=>run({arm,seed,split:"unseen-combinations",
      status:"error",reason:String(e?.message||e),scores:{}}))};}});
  const runs=groups.flatMap(g=>g.rows);
  writeResult(out,resultRecord({experiment:"brain-world/construction-transfer-pilot",
    baseline:"scratch",runs,config:{...cfg,seeds,arms:ARMS,
      partitionHashes:Object.fromEntries(seeds.map((seed,i)=>[seed,groups[i].digest])),
      split:"constraint-family-disjoint train/eval; adaptation and final task instances distinct",
      provenance:PROVENANCE,
      limitations:"Pilot only: no independent sealed stress generator; not proof of skill composition; no shared conventional-backprop arm. Report total pretrain plus adaptation, not adaptation alone."},
    budgets:{pretrainDecisions:trainSteps,adaptDecisions:adaptSteps,evalEpisodes:evalTasks*repeats},
    metrics:{zeroShot:"higher",adapted:"higher",newDrawing:"higher",gain:"higher",
      oldBefore:"higher",oldAfter:"higher",forgetting:"lower",
      trainDecisions:"lower",adaptDecisions:"lower",evalDecisions:"lower"}}));
  for(const arm of ARMS){
    const r=runs.filter(x=>x.arm===arm&&x.status==="ok");
    const avg=r.length?r.reduce((a,x)=>a+x.scores.adapted,0)/r.length:NaN;
    console.log(arm,"adapted",avg.toFixed(3),"completed",r.length,"/",seeds.length);
  }
  if(runs.some(r=>r.status!=="ok"))process.exitCode=1;
}
