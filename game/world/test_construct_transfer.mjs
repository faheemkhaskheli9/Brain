import assert from "node:assert/strict";
import {partitions,signature,runSeed,ARMS} from "./construct_transfer.mjs";
import {comboKey} from "./construct.mjs";
const cfg={trainSteps:8,adaptSteps:8,trainTasks:4,adaptTasks:3,evalTasks:3,repeats:1};
const p=partitions(7,cfg.trainTasks,cfg.adaptTasks,cfg.evalTasks);
assert.equal(p.train.length,4);assert.equal(p.adapt.length,3);assert.equal(p.heldout.length,3);
const trainedKeys=new Set(p.train.map(comboKey)), adapt=new Set(p.adapt.map(signature));
assert.ok([...p.adapt,...p.heldout].every(t=>!trainedKeys.has(comboKey(t))));
assert.ok(p.heldout.every(t=>!adapt.has(signature(t))));
const a=runSeed(7,cfg),b=runSeed(7,cfg);
assert.equal(a.digest,b.digest);
assert.deepEqual(a.rows.map(r=>r.arm),ARMS);
for(let i=0;i<a.rows.length;i++){
  const x=a.rows[i],y=b.rows[i];
  assert.equal(x.status,"ok",x.reason);
  assert.deepEqual(x.scores,y.scores);
  for(const k of ["zeroShot","adapted","newDrawing","oldBefore","oldAfter"])
    assert.ok(x.scores[k]>=0&&x.scores[k]<=1,k);
  if(["pretrained","goal-masked","frozen"].includes(x.arm))
    assert.ok(x.scores.trainDecisions>=cfg.trainSteps);
  if(x.arm==="scratch")assert.equal(x.scores.trainDecisions,0);
  if(x.arm!=="random-valid")assert.ok(x.scores.adaptDecisions>=cfg.adaptSteps);
  if(x.arm==="frozen")assert.equal(x.scores.gain,0);
}
console.log("construction transfer pilot controls: OK");
