"""A *single persistent* toy body across target and hidden-motor-rule changes.

Only target metadata and per-goal scoring counters change. Joint positions,
velocities and the actual SensorimotorLoop NEVER reset in the stream.
This is not a physical robot, natural visual encoder or neural cortex.
"""
from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass

from closed_loop_reach import HORIZON, TOLERANCE, ReachBody, ReachTrial
from online_context import OnlineConfig


class ContinuousReachBody(ReachBody):
    """Keep the physical simulator alive; update only the target and statistics."""

    def __init__(self, trial: ReachTrial):
        super().__init__(trial)
        self.targets_seen = 1
        self.physical_steps = 0
        self.body_identity = id(self.loop.body)

    def set_target(self, trial: ReachTrial) -> bool:
        """New public target, no joint reinitialization. Return preceding goal hit."""
        if not isinstance(trial, ReachTrial) or not -1 <= trial.target <= 1:
            raise ValueError('Invalid new target')
        if self.steps != HORIZON:
            raise RuntimeError('Target changes must follow full goal-action budget')
        previous_hit = self.first_hit is not None
        self.trial = trial
        self.steps = 0
        self.best_distance = abs(trial.target - self.loop.body.positions['L_hip'])
        self.first_hit = 0 if self.best_distance <= TOLERANCE else None
        self.progress_reward = 0
        self.targets_seen += 1
        if id(self.loop.body) != self.body_identity:
            raise RuntimeError('Physical body was replaced')
        return previous_hit

    def act(self, action: int, *, inverted_motor: bool = False) -> float:
        reward = super().act(action, inverted_motor=inverted_motor)
        self.physical_steps += 1
        return reward


@dataclass(frozen=True)
class FeedbackStats:
    active: int
    switches: int
    actions: int
    rewards_delivered: int
    pending_rewards: int


class DelayedRewardSelector:
    """Switch only after receiving real, earlier rewards with explicit latency.

    `choose()` consumes reward deliveries due at the current action clock,
    then selects a policy. `feedback()` records the outcome of *that*
    physical action; it cannot influence any choice until due. No hidden
    context, resets, counterfactual action or invented reward enters.

    The window threshold matches OnlineRewardSelector for delay=1, except
    a reward arriving after the last action remains pending (reported).
    """

    def __init__(self, config: OnlineConfig, *, delay: int = 1, initial: int = 0):
        if not isinstance(config, OnlineConfig) or type(delay) is not int or not 1 <= delay <= 16:
            raise ValueError('Invalid delay / selector config')
        if type(initial) is not int or initial not in (0, 1):
            raise ValueError('Initial context slot must be zero or one')
        self.config, self.delay, self.active = config, delay, initial
        self.actions = self.switches = self.delivered = 0
        self._last_switch = 0
        self._pending_action = False
        self._observations: deque[float] = deque(maxlen=config.window)
        self._queue: deque[tuple[int, float]] = deque()

    def choose(self) -> int:
        if self._pending_action:
            raise RuntimeError('Feedback of the last physical action is missing')
        while self._queue and self._queue[0][0] <= self.actions:
            _, reward = self._queue.popleft()
            self.delivered += 1
            self._observations.append(reward)
            if (len(self._observations) == self.config.window
                    and self.actions - self._last_switch >= self.config.min_dwell
                    and sum(self._observations) / len(self._observations) <= self.config.low_mean
                    and self.switches < self.config.max_switches):
                self.active = 1 - self.active
                self._last_switch = self.actions
                self.switches += 1
                self._observations.clear()
        self._pending_action = True
        return self.active

    def feedback(self, reward: float) -> None:
        if not self._pending_action:
            raise RuntimeError('Reward cannot precede a physical action')
        if isinstance(reward, bool) or not isinstance(reward, (int, float)) or not math.isfinite(reward) or not -1 <= reward <= 1:
            raise ValueError('Reward must be finite in [-1, 1]')
        # Store only a *real* action's public reward. Its due time is t+delay.
        self._queue.append((self.actions + self.delay, float(reward)))
        self.actions += 1
        self._pending_action = False

    def stats(self) -> FeedbackStats:
        if self._pending_action:
            raise RuntimeError('Cannot inspect statistics before recording outcome')
        return FeedbackStats(self.active, self.switches, self.actions,
                             self.delivered, len(self._queue))