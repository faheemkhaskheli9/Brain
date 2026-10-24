// A common environment interface to Brain World (issue #118), so a baseline or a conventional RL
// learner sees exactly what the creature sees and nothing more:
//   obs      World.sense() output, the Float32Array the creature's brain encodes (retina, legs,
//            cochlea, fovea, pen, board, fovea memory). No positions, target or task name.
//   allowed  the action set the body allows this step (ACT_SETS: body, habit or pen), as for the creature
//   reward, done, success   the World's own reward and termination (time limit included)
// The World runs unchanged with a PolicyBrain in place of the creature's Brain. When an episode
// ends, the returned obs is already the first of the next episode (auto-reset).
// Rooms are drawn from the same seeded RNG the agent samples from, so two agents on one seed see
// the same distribution of rooms, not the same sequence.
import { World, STAGES, ACT_SETS, BODY, PEN } from "./brain.js";

const N_ACTIONS = BODY.length + PEN.length;

// Stands in for Brain inside World: encode passes the senses through, act returns the action the
// caller chose, learn and the memory/context hooks do nothing (one context slot).
export class PolicyBrain {
  constructor() {
    this.next = -1; this.pi = new Float32Array(N_ACTIONS); this.ev = new Float32Array(1); this.eP = new Float32Array(1);
    this.learning = true; this.greedy = false;
  }
  encode(x) { return x; }
  act(h, allowed) {
    if (!allowed.includes(this.next)) throw new Error(`action ${this.next} not allowed here; allowed: ${allowed.join(", ")}`);
    this.pi.fill(0); this.pi[this.next] = 1;
    return this.next;
  }
  learn() {}
  infer() { return 0; }
  commit() {}
  consolidate() {}
  sleep() {}
}

export class Env {
  // skill: a STAGES key, evaluated as the graduated creature is (perform mode: the gait reflex on,
  // no curriculum, no episodic store). seed: the World seed.
  constructor(seed, skill) {
    this.world = new World(seed);
    this.world.brain = new PolicyBrain();
    this.world.graduated = true; this.world.stage = STAGES.length - 1;
    this.world.perform(skill, false);
    this.world.h = this.world.x;
    this.steps = 0; this.episodes = 0; this.successes = 0;
  }
  get obs() { return this.world.x; }
  // The body's action set, computed as World.step does (board: pen; else the habit set once graduated).
  get allowed() { return ACT_SETS[this.world.board ? 2 : 1]; }
  get rand() { return this.world.rand; }
  step(action) {
    this.world.brain.next = action;
    const { reward, done, success } = this.world.step();
    this.steps++;
    if (done) { this.episodes++; this.successes += success ? 1 : 0; }
    this.world.h = this.world.x;
    return { obs: this.world.x, allowed: this.allowed, reward, done, success };
  }
}
