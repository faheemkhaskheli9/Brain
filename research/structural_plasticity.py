"""Backprop-free local reward learning with bounded activity-driven micro-synapse turnover.

Separately engineered small policy population, NOT human neural anatomy.
Synapses are created only between eligible within-model input and action units;
the 78-region anatomical graph is immutable. No dense N×N weight matrix.
"""

from __future__ import annotations

import math
import random
from dataclasses import asdict
from collections import deque
from dataclasses import dataclass
from numbers import Real

import numpy as np


@dataclass
class Synapse:
    weight: float
    born_at: int = 0
    eligibility: float = 0.0
    updates: int = 0


@dataclass(frozen=True)
class PlasticityConfig:
    inputs: int = 24
    actions: int = 2
    max_edges: int = 4
    max_fanout: int = 2
    learning_rate: float = 0.06
    eligibility_decay: float = 0.8
    activity_threshold: float = 0.01
    weight_bound: float = 4.0
    grow_every: int = 80
    warmup: int = 80
    candidate_decay: float = 0.99
    candidate_min_score: float = 0.75
    growth_strength: float = 0.04
    min_prune_age: int = 50
    max_candidates: int = 64
    min_error_rate: float = 0.12
    error_window: int = 80
    max_delayed_steps: int = 16

    def __post_init__(self) -> None:
        ints = ('inputs', 'actions', 'max_edges', 'max_fanout', 'grow_every', 'max_candidates',
                'error_window', 'max_delayed_steps')
        ints_nonnegative = ('warmup', 'min_prune_age')
        for key in ints + ints_nonnegative:
            val = getattr(self, key)
            if type(val) is not int or val < (0 if key in ints_nonnegative else 1):
                raise ValueError(f'{key} is not a valid integer')
        if self.actions < 2 or self.max_edges > self.inputs * self.actions or self.max_fanout > self.actions:
            raise ValueError('Inconsistent network size/capacity')
        for key in ('learning_rate', 'eligibility_decay', 'activity_threshold', 'weight_bound',
                    'candidate_decay', 'candidate_min_score', 'growth_strength', 'min_error_rate'):
            val = getattr(self, key)
            if isinstance(val, bool) or not isinstance(val, Real) or not math.isfinite(val):
                raise ValueError(f'{key} must be a finite real number')
        if not (0 < self.learning_rate <= 1 and 0 <= self.eligibility_decay < 1
                and 0 <= self.activity_threshold < 1 and self.weight_bound > 0
                and 0 <= self.candidate_decay < 1 and self.candidate_min_score > 0
                and 0 < self.growth_strength <= self.weight_bound and 0 <= self.min_error_rate <= 1):
            raise ValueError('Invalid hyperparameters')


class SparsePlasticPolicy:
    """Sparse stochastic actor with local pre/post eligibility * reward modulation.

    `growth_mode='evidence'`: rank candidate synapses by signed reward-modulated
    activity correlation; `random`: grow from same observed candidate pool, but
    choose a random missing link; `off`: fixed topology. The budget is fixed
    across arms, and growth never modifies global region-to-region anatomy.
    """

    def __init__(self, config: PlasticityConfig, seed: int, *, growth_mode: str = 'evidence',
                 learn: bool = True, initial_edges: tuple[tuple[int, int], ...] = ()) -> None:
        if type(seed) is not int or type(learn) is not bool or growth_mode not in ('evidence', 'random', 'off'):
            raise ValueError('Invalid seed, learning switch, or growth mode')
        if len(initial_edges) > config.max_edges or len(set(initial_edges)) != len(initial_edges):
            raise ValueError('Initial topology is oversized or has duplicates')
        self.cfg = config
        self.rng = random.Random(seed)
        self.growth_mode = growth_mode
        self.learn = learn
        self.edges: dict[tuple[int, int], Synapse] = {}
        for pair in initial_edges:
            self._check_edge(pair)
            if sum(1 for i, _ in self.edges if i == pair[0]) >= config.max_fanout:
                raise ValueError('Initial topology exceeds input fanout')
            self.edges[pair] = Synapse(self.rng.uniform(-0.02, 0.02))
        # Candidate cache: key -> (score, last_reward_step). Bounded, NOT NxN.
        self.candidates: dict[tuple[int, int], tuple[float, int]] = {}
        self.pending_traces: dict[tuple[int, int], float] = {}
        self._touched: set[tuple[int, int]] = set()
        self._pending = 0
        self.recent_errors: deque[int] = deque(maxlen=config.error_window)
        self.baseline = 0.0
        self.feedback_steps = 0
        self.new_edges = 0
        self.removed_edges = 0
        self.candidate_evictions = 0
        self.synaptic_products = 0
        self.candidate_products = 0

    def _check_edge(self, pair: tuple[int, int]) -> None:
        if (not isinstance(pair, tuple) or len(pair) != 2 or
                any(type(v) is not int for v in pair) or
                not 0 <= pair[0] < self.cfg.inputs or not 0 <= pair[1] < self.cfg.actions):
            raise ValueError('Invalid microcircuit synapse endpoints')

    @property
    def density(self) -> float:
        return len(self.edges) / (self.cfg.inputs * self.cfg.actions)

    def _candidate_score(self, key: tuple[int, int]) -> float:
        score, when = self.candidates[key]
        return score * self.cfg.candidate_decay ** (self.feedback_steps - when)

    def _reserve_candidate(self, key: tuple[int, int]) -> None:
        if key in self.pending_traces:
            return
        if key in self.candidates:
            self.pending_traces[key] = 0.0
            return
        if len(self.candidates) + len(self.pending_traces) >= self.cfg.max_candidates:
            victims = [candidate for candidate in self.candidates if candidate not in self.pending_traces]
            if not victims:
                return
            victim = min(victims, key=lambda entry: (abs(self._candidate_score(entry)), entry))
            del self.candidates[victim]
            self.candidate_evictions += 1
        self.pending_traces[key] = 0.0

    def act(self, observation: np.ndarray, *, explore: bool = True) -> int:
        if self._pending >= self.cfg.max_delayed_steps or (self._pending and not explore):
            raise RuntimeError('Pending reward window exceeds budget or frozen decision is unsafe')
        if not isinstance(observation, np.ndarray) or observation.shape != (self.cfg.inputs,):
            raise ValueError('Wrong input shape')
        if (not np.issubdtype(observation.dtype, np.floating) or
                not np.all(np.isfinite(observation)) or np.any(np.abs(observation) > 1)):
            raise ValueError('Expected finite normalized floating-point features')
        if type(explore) is not bool:
            raise ValueError('explore must be bool')
        active = {i: float(x) for i, x in enumerate(observation) if abs(x) > self.cfg.activity_threshold}
        logits = [0.0] * self.cfg.actions
        for (i, j), syn in self.edges.items():
            if i in active:
                logits[j] += active[i] * syn.weight
                self.synaptic_products += 1
        normalizer = max(logits)
        exp_logits = [math.exp(val - normalizer) for val in logits]
        total = sum(exp_logits)
        probs = [p / total for p in exp_logits]
        choice = self.rng.choices(range(self.cfg.actions), weights=probs, k=1)[0] if explore else max(
            range(self.cfg.actions), key=lambda j: (probs[j], -j))
        if explore and self.learn:
            for key in self._touched:
                self.edges[key].eligibility *= self.cfg.eligibility_decay
            for key in self.pending_traces:
                self.pending_traces[key] *= self.cfg.eligibility_decay
            for i, value in active.items():
                for j in range(self.cfg.actions):
                    key = i, j
                    local_tag = value * ((1.0 if j == choice else 0.0) - probs[j])
                    if key in self.edges:
                        self.edges[key].eligibility += local_tag
                        self._touched.add(key)
                    elif self.growth_mode != 'off':
                        self._reserve_candidate(key)
                        if key in self.pending_traces:
                            self.pending_traces[key] += local_tag
                            self.candidate_products += 1
            self._pending += 1
        return choice

    def feedback(self, reward: float) -> None:
        if not self._pending:
            raise RuntimeError('No pending exploratory choice')
        if isinstance(reward, bool) or not isinstance(reward, Real) or not math.isfinite(reward) or not -1 <= reward <= 1:
            raise ValueError('Reward must be finite in [-1, 1]')
        modulator = float(reward) - self.baseline
        for key in self._touched:  # Update only locally active, existing connections.
            syn = self.edges[key]
            syn.weight = max(-self.cfg.weight_bound, min(self.cfg.weight_bound,
                             syn.weight + self.cfg.learning_rate * modulator * syn.eligibility))
            syn.updates += 1
            syn.eligibility = 0.0
        if self.growth_mode != 'off':
            for key, trace in self.pending_traces.items():
                if key in self.candidates:
                    score = self._candidate_score(key)
                else:
                    score = 0.0
                self.candidates[key] = (score + trace * modulator, self.feedback_steps + 1)
        self.recent_errors.append(int(reward <= 0))
        self.baseline = 0.99 * self.baseline + 0.01 * float(reward)
        self.feedback_steps += 1
        self._touched.clear()
        self.pending_traces.clear()
        self._pending = 0
        if (self.growth_mode != 'off' and self.feedback_steps >= self.cfg.warmup
                and self.feedback_steps % self.cfg.grow_every == 0):
            self.rewire()

    def rewire(self) -> bool:
        """Form a useful candidate link if recent outcomes indicate a need.

        Removes a mature weak connection first when at capacity; no dense scan.
        `random` uses observed candidates but ignores their credit scores.
        """
        if not self.learn or self.growth_mode == 'off' or self._pending:
            return False
        if (len(self.recent_errors) < min(self.cfg.error_window, self.cfg.warmup)
                or sum(self.recent_errors) / len(self.recent_errors) < self.cfg.min_error_rate):
            return False
        possible = [(key, self._candidate_score(key)) for key in self.candidates
                    if key not in self.edges]
        if self.growth_mode == 'evidence':
            possible = [(key, score) for key, score in possible
                        if abs(score) >= self.cfg.candidate_min_score]
            possible.sort(key=lambda row: (-abs(row[1]), row[0]))
        else:
            self.rng.shuffle(possible)
        for key, score in possible:
            i, _ = key
            fanout = sum(1 for source, _ in self.edges if source == i)
            if len(self.edges) == self.cfg.max_edges or fanout == self.cfg.max_fanout:
                if fanout == self.cfg.max_fanout:
                    victims = [(edge, syn) for edge, syn in self.edges.items()
                               if edge[0] == i and self.feedback_steps - syn.born_at >= self.cfg.min_prune_age]
                else:
                    victims = [(edge, syn) for edge, syn in self.edges.items()
                               if self.feedback_steps - syn.born_at >= self.cfg.min_prune_age]
                if not victims:
                    continue
                victim = min(victims, key=lambda row: (abs(row[1].weight), row[0]))[0]
                del self.edges[victim]
                self.removed_edges += 1
                self.candidates.pop(victim, None)
            # The initialization sign for evidence growth is *learned from rewards*;
            # random growth gets an independent random sign (no credit leakage).
            sign = (1.0 if score >= 0 else -1.0) if self.growth_mode == 'evidence' else self.rng.choice((-1.0, 1.0))
            self.edges[key] = Synapse(sign * self.cfg.growth_strength, born_at=self.feedback_steps)
            self.new_edges += 1
            del self.candidates[key]
            return True
        return False

    def reset(self) -> None:
        """Abandon pending trial without contaminating the next episode."""
        self._pending = 0
        self.pending_traces.clear()
        for key in self._touched:
            self.edges[key].eligibility = 0.0
        self._touched.clear()

    def fingerprint(self) -> tuple:
        """Training state audit for frozen evaluations (excluding operation counters)."""
        if self._pending:
            raise RuntimeError('Cannot snapshot with pending feedback')
        return (tuple(sorted((k, v.weight, v.born_at, v.updates) for k, v in self.edges.items())),
                tuple(sorted(self.candidates.items())), self.baseline, self.feedback_steps,
                tuple(self.recent_errors), self.rng.getstate())

    def export_state(self) -> dict:
        """Save sparse synapses and RNG without pickle or a dense tensor.

        Only checkpoint between rewarded episodes, not during a pending trace.
        """
        self.fingerprint()  # fail if feedback is pending
        return {
            'format': 'brain-sparse-local-plasticity/1',
            'config': asdict(self.cfg), 'growth_mode': self.growth_mode, 'learn': self.learn,
            'edges': [[i, j, syn.weight, syn.born_at, syn.updates]
                      for (i, j), syn in sorted(self.edges.items())],
            'candidates': [[i, j, value, when]
                           for (i, j), (value, when) in sorted(self.candidates.items())],
            'baseline': self.baseline, 'feedback_steps': self.feedback_steps,
            'recent_errors': list(self.recent_errors),
            'rng': [self.rng.getstate()[0], list(self.rng.getstate()[1]), self.rng.getstate()[2]],
            'total_new_edges': self.new_edges, 'total_removed_edges': self.removed_edges,
        }

    @classmethod
    def from_state(cls, data: dict) -> 'SparsePlasticPolicy':
        """Restore a validated JSON-compatible checkpoint; reject malformed topology."""
        if not isinstance(data, dict) or data.get('format') != 'brain-sparse-local-plasticity/1':
            raise ValueError('Unknown sparse policy checkpoint')
        try:
            cfg = PlasticityConfig(**data['config'])
            instance = cls(cfg, 0, growth_mode=data['growth_mode'], learn=data['learn'])
            feedback_steps = data['feedback_steps']
            if type(feedback_steps) is not int or feedback_steps < 0:
                raise ValueError('Bad checkpoint step')
            seen = set()
            for i, j, weight, born, updates in data['edges']:
                pair = i, j
                instance._check_edge(pair)
                if pair in seen or len(seen) >= cfg.max_edges:
                    raise ValueError('Duplicate or oversized checkpoint topology')
                if type(born) is not int or type(updates) is not int or not 0 <= born <= feedback_steps or updates < 0:
                    raise ValueError('Bad synapse metadata')
                if isinstance(weight, bool) or not isinstance(weight, Real) or not math.isfinite(weight) or abs(weight) > cfg.weight_bound:
                    raise ValueError('Bad synaptic weight')
                seen.add(pair)
                instance.edges[pair] = Synapse(float(weight), born, updates=updates)
            if any(sum(1 for i, _ in seen if i == source) > cfg.max_fanout for source, _ in seen):
                raise ValueError('Checkpoint exceeds input fanout')
            for i, j, score, when in data['candidates']:
                pair = i, j
                instance._check_edge(pair)
                if pair in instance.edges or pair in instance.candidates or len(instance.candidates) >= cfg.max_candidates:
                    raise ValueError('Bad checkpoint candidate cache')
                if isinstance(score, bool) or not isinstance(score, Real) or not math.isfinite(score) or type(when) is not int or not 0 <= when <= feedback_steps:
                    raise ValueError('Bad cached score')
                instance.candidates[pair] = (float(score), when)
            baseline = data['baseline']
            if isinstance(baseline, bool) or not isinstance(baseline, Real) or not math.isfinite(baseline) or abs(baseline) > 1:
                raise ValueError('Bad reward baseline')
            instance.baseline = float(baseline)
            errors = data['recent_errors']
            if not isinstance(errors, list) or len(errors) > cfg.error_window or any(type(v) is not int or v not in (0, 1) for v in errors):
                raise ValueError('Bad recent errors')
            instance.recent_errors.extend(errors)
            if type(data['total_new_edges']) is not int or type(data['total_removed_edges']) is not int or min(data['total_new_edges'], data['total_removed_edges']) < 0:
                raise ValueError('Bad growth counters')
            instance.new_edges = data['total_new_edges']
            instance.removed_edges = data['total_removed_edges']
            instance.feedback_steps = feedback_steps
            state = data['rng']
            if not isinstance(state, list) or len(state) != 3 or not isinstance(state[1], list):
                raise ValueError('Bad RNG state')
            instance.rng.setstate((state[0], tuple(state[1]), state[2]))
            return instance
        except (KeyError, TypeError, IndexError, OverflowError) as exc:
            raise ValueError('Invalid sparse policy checkpoint fields') from exc