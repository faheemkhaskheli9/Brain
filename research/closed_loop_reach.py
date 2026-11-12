"""Closed-loop toy joint reaching with *learned* sparse micro-synaptic commands.

The observable target error comes from a designed 3-channel visual port; S1
proprioception comes from the existing body simulator. The microcircuit is
separate from the macro anatomical graph and does NOT simulate cortical layers.
Training uses verified *post-action progress* reward, never an oracle action.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np

from sensorimotor_bridge import SensorimotorLoop
from structural_plasticity import SparsePlasticPolicy

HORIZON = 16
DT = 0.1
TOLERANCE = 0.07


@dataclass(frozen=True)
class ReachTrial:
    target: float
    distractors: tuple[float, float]
    split: str
    key: str


def reach_trials(split: str, seed: int, count: int) -> tuple[ReachTrial, ...]:
    """Fresh disjoint episode IDs; eval uses held-out target distances.

    The environment's sign mapping and reward remain constant. Holdout is a
    modest magnitude shift, NOT an unseen motion primitive or reversal.
    """
    if split not in ("train", "dev", "eval") or type(seed) is not int or seed < 0 or type(count) is not int or not 1 <= count <= 100000:
        raise ValueError("Invalid split, seed or number of episodes")
    salt = {"train": 1057, "dev": 2029, "eval": 4001}[split]
    rng = random.Random(seed * 10000019 + salt)
    bounds = {"train": (0.19, 0.36), "dev": (0.29, 0.43), "eval": (0.37, 0.52)}[split]
    return tuple(ReachTrial(
        target=(1 if (index + seed) % 2 == 0 else -1) * rng.uniform(*bounds),
        distractors=(rng.choice((-1.0, 1.0)), rng.choice((-1.0, 1.0))),
        split=split,
        key=f"reach:{split}:{seed}:{index}",
    ) for index in range(count))


class ReachBody:
    """One-joint learning interface with explicit public V1 and S1 channels.

    Other joints are kept at zero. `vision` carries an engineered target-error
    representation, NOT actual pixels or a learned visual feature extractor.
    """

    def __init__(self, trial: ReachTrial):
        if not isinstance(trial, ReachTrial) or not -1 <= trial.target <= 1:
            raise ValueError("Invalid reaching task")
        self.trial = trial
        self.loop = SensorimotorLoop()
        self.steps = 0
        self.best_distance = abs(trial.target)
        self.first_hit: int | None = None
        self.progress_reward = 0

    def _vision(self) -> dict:
        delta = float(np.clip(self.trial.target - self.loop.body.positions["L_hip"], -1, 1))
        return {"vision": {"L": [delta, *self.trial.distractors]}}

    def observe(self) -> np.ndarray:
        """24 signed channels; only public sensory packets reach the policy."""
        packets = self.loop.sensors.route({**self._vision(), "proprioception": self.loop.body.proprioception()})
        eye = next(p for p in packets if p.modality == "vision" and p.hemisphere == "L")
        body = next(p for p in packets if p.modality == "proprioception" and p.hemisphere == "L")
        if eye.entry_region != "L_lgn" or eye.cortical_target != "L_v1" or body.cortical_target != "L_s1":
            raise RuntimeError("Unexpected anatomical sensory entry")
        channels = np.zeros(24, dtype=np.float32)
        channels[:3] = eye.values  # delta and two independent nuisance visual features
        channels[3:7] = body.values  # L hip/knee positions, then velocities
        return channels

    def act(self, action: int, *, inverted_motor: bool = False) -> float:
        """Action 0 drives L hip negative; action 1 positive. Reward is AFTER movement."""
        if type(action) is not int or action not in (0, 1) or type(inverted_motor) is not bool:
            raise ValueError("Action must be a discrete learned motor choice")
        if self.steps >= HORIZON:
            raise RuntimeError("Episode step budget exhausted")
        direction = -1.0 if action == 0 else 1.0
        if inverted_motor:
            direction *= -1
        old_error = abs(self.trial.target - self.loop.body.positions["L_hip"])
        outcome = self.loop.step(self._vision(), {"L_motor_pool": [direction, 0.0], "R_motor_pool": [0.0, 0.0]}, dt=DT)
        if len(outcome["proprioceptive_feedback"]) != 2:
            raise RuntimeError("Proprioception was not returned")
        self.steps += 1
        new_error = abs(self.trial.target - self.loop.body.positions["L_hip"])
        self.best_distance = min(self.best_distance, new_error)
        if self.first_hit is None and new_error <= TOLERANCE:
            self.first_hit = self.steps
        reward = 1.0 if new_error < old_error - 1e-8 else -1.0
        self.progress_reward += int(reward)
        return reward


@dataclass(frozen=True)
class ReachScore:
    success: float
    final_error: float
    progress: float
    error_rate: float
    mean_time_to_hit: float | None
    episodes: int


def run_episodes(policy: SparsePlasticPolicy, tasks: tuple[ReachTrial, ...], *,
                 learn: bool = False, delay: int = 1, inverted_motor: bool = False,
                 explore: bool | None = None) -> ReachScore:
    """Fixed interaction count; no early success termination, including for controls."""
    if not tasks or type(learn) is not bool or type(inverted_motor) is not bool or type(delay) is not int or not 1 <= delay <= HORIZON:
        raise ValueError("Invalid experiment settings")
    if learn and not policy.learn:
        raise ValueError("Cannot train a frozen policy")
    if explore is None:
        explore = learn
    if type(explore) is not bool or (learn and not explore):
        raise ValueError("Training requires stochastic action selection")
    if delay > policy.cfg.max_delayed_steps:
        raise ValueError("Delay exceeds policy trace budget")
    before = policy.fingerprint() if not learn and not explore else None
    successes = 0
    error_sum = progress_sum = error_steps = 0.0
    hits = []
    for task in tasks:
        body = ReachBody(task)
        for group in range(0, HORIZON, delay):
            initial_distance = abs(task.target - body.loop.body.positions["L_hip"])
            count = min(delay, HORIZON - group)
            for _ in range(count):
                action = policy.act(body.observe(), explore=explore)
                reward = body.act(action, inverted_motor=inverted_motor)
                error_steps += reward < 0
            if learn:
                final_distance = abs(task.target - body.loop.body.positions["L_hip"])
                policy.feedback(1.0 if final_distance < initial_distance - 1e-8 else -1.0)
        successes += int(body.best_distance <= TOLERANCE)
        if body.first_hit is not None:
            hits.append(body.first_hit)
        error_sum += abs(task.target - body.loop.body.positions["L_hip"])
        progress_sum += body.progress_reward / HORIZON
    if before is not None and before != policy.fingerprint():
        raise RuntimeError("Frozen scoring altered policy parameters or RNG")
    return ReachScore(successes / len(tasks), error_sum / len(tasks),
                      progress_sum / len(tasks), error_steps / (len(tasks) * HORIZON),
                      sum(hits) / len(hits) if hits else None, len(tasks))


if __name__ == "__main__":
    from structural_plasticity import PlasticityConfig

    agent = SparsePlasticPolicy(PlasticityConfig(), 1)
    print(run_episodes(agent, reach_trials("eval", 10, 4)))