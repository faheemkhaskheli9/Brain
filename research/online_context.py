"""Online public-reward change response for two pre-trained sparse policies.

No phase/boundary labels, parallel counterfactual simulator resets, or updates
of the stored policies. Switching uses only previously *observed* rewards.
This is an engineered sequential controller, not a biological context model.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class OnlineConfig:
    window: int = 4
    low_mean: float = -0.5
    min_dwell: int = 7
    max_switches: int = 64

    def __post_init__(self):
        if (type(self.window) is not int or not 2 <= self.window <= 32
                or type(self.min_dwell) is not int or not 1 <= self.min_dwell <= 256
                or type(self.max_switches) is not int or not 0 <= self.max_switches <= 1024):
            raise ValueError('Invalid reward history or switching budget')
        if (isinstance(self.low_mean, bool) or not isinstance(self.low_mean, (float, int))
                or not math.isfinite(self.low_mean) or not -1.0 <= self.low_mean < 0.0):
            raise ValueError('Expected finite negative reward threshold')


DEFAULT_CONFIG = OnlineConfig()


class OnlineRewardSelector:
    """Select between two frozen checkpoints by detecting poor *past* reward.

    Each action is produced by the current stored controller. Only the public
    reward of that actual action is observed; no unchosen controller is run,
    no explicit context-change event or known target is passed to this class.
    """

    def __init__(self, config: OnlineConfig = DEFAULT_CONFIG, *, initial: int = 0):
        if not isinstance(config, OnlineConfig) or type(initial) is not int or initial not in (0, 1):
            raise ValueError('Invalid selector configuration or initial slot')
        self.config = config
        self.active = initial
        self.actions = 0
        self.switches = 0
        self._last_switch = 0
        self._history: deque[float] = deque(maxlen=config.window)
        self._pending = False

    def select(self) -> int:
        if self._pending:
            raise RuntimeError('Previous action has no observed outcome')
        self._pending = True
        return self.active

    def feedback(self, reward: float) -> bool:
        if not self._pending:
            raise RuntimeError('Cannot update selector without a real action')
        if (isinstance(reward, bool) or not isinstance(reward, (float, int))
                or not math.isfinite(reward) or not -1.0 <= reward <= 1.0):
            raise ValueError('Public reward must be finite in [-1, 1]')
        self._pending = False
        self.actions += 1
        self._history.append(float(reward))
        if (len(self._history) == self.config.window
                and self.actions - self._last_switch >= self.config.min_dwell
                and sum(self._history) / len(self._history) <= self.config.low_mean
                and self.switches < self.config.max_switches):
            self.active = 1 - self.active
            self._history.clear()
            self._last_switch = self.actions
            self.switches += 1
            return True
        return False

    def snapshot(self) -> dict:
        if self._pending:
            raise RuntimeError('Cannot snapshot before receiving the action outcome')
        return {'format': 'online-reward-selector/1', 'config': {
            'window': self.config.window, 'low_mean': self.config.low_mean,
            'min_dwell': self.config.min_dwell, 'max_switches': self.config.max_switches},
            'active': self.active, 'actions': self.actions, 'switches': self.switches,
            'last_switch': self._last_switch, 'history': list(self._history)}

    @classmethod
    def from_state(cls, state: dict) -> 'OnlineRewardSelector':
        if not isinstance(state, dict) or set(state) != {'format', 'config', 'active', 'actions',
                                                         'switches', 'last_switch', 'history'}:
            raise ValueError('Malformed online selector state')
        if state['format'] != 'online-reward-selector/1' or not isinstance(state['config'], dict):
            raise ValueError('Unknown selector format')
        try:
            cfg = OnlineConfig(**state['config'])
            obj = cls(cfg, initial=state['active'])
            actions, switches, last = (state['actions'], state['switches'], state['last_switch'])
            if any(type(v) is not int for v in (actions, switches, last)) or not (
                    0 <= switches <= cfg.max_switches and 0 <= last <= actions and switches <= actions):
                raise ValueError('Invalid selector counters')
            history = state['history']
            if (not isinstance(history, list) or len(history) > cfg.window
                    or any(isinstance(x, bool) or not isinstance(x, (float, int))
                           or not math.isfinite(x) or not -1 <= x <= 1 for x in history)):
                raise ValueError('Invalid reward history')
            if switches and (actions - last < 0):
                raise ValueError('Invalid last switch')
            obj.actions, obj.switches, obj._last_switch = actions, switches, last
            obj._history.extend(float(x) for x in history)
            return obj
        except (TypeError, KeyError) as exc:
            raise ValueError('Invalid selector fields') from exc