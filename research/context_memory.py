"""Bounded checkpoint-based context memory for the toy sparse motor policy.

Engineering approximation, NOT a hippocampus or a discovered context model.
Stores independent local-plasticity policies, probes them using public
post-action reward and retrieves without reading the simulator's hidden
motor inversion flag. Probing requires extra *real simulator interactions*.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Callable

from closed_loop_reach import ReachBody, ReachTrial
from structural_plasticity import SparsePlasticPolicy


@dataclass(frozen=True)
class Retrieval:
    index: int
    scores: tuple[float, ...]
    probe_actions: int
    probe_rewards: int
    checkpoint_bytes: int


class SparseContextMemory:
    """Capacity-limited set of learned microcircuits with outcome-based retrieval.

    Growth/pruning still happens inside SparsePlasticPolicy while training;
    storing a checkpoint alone does *not* learn any new synaptic weight.
    All snapshots use safe JSON serialization with validated restore.
    """

    FORMAT = 'brain-context-memory/1'

    def __init__(self, *, capacity: int = 2):
        if type(capacity) is not int or not 1 <= capacity <= 8:
            raise ValueError('capacity must be an integer from 1 to 8')
        self.capacity = capacity
        self._slots: list[str] = []

    @property
    def size(self) -> int:
        return len(self._slots)

    @property
    def checkpoint_bytes(self) -> int:
        return sum(len(s.encode('utf-8')) for s in self._slots)

    def add(self, policy: SparsePlasticPolicy) -> int:
        """Commit a *detached* snapshot between feedback windows."""
        if not isinstance(policy, SparsePlasticPolicy):
            raise TypeError('Expected a sparse learned policy')
        if self.size >= self.capacity:
            raise RuntimeError('Context memory capacity reached: explicit eviction required')
        snapshot = json.dumps(policy.export_state(), sort_keys=True, separators=(',', ':'), allow_nan=False)
        candidate = SparsePlasticPolicy.from_state(json.loads(snapshot))
        if candidate.fingerprint() != policy.fingerprint():
            raise ValueError('Policy checkpoint failed round trip')
        if self._slots:
            first = json.loads(self._slots[0])
            if candidate.cfg != SparsePlasticPolicy.from_state(first).cfg:
                raise ValueError('Policy configuration differs between context memories')
        self._slots.append(snapshot)
        return self.size - 1

    def policy(self, index: int) -> SparsePlasticPolicy:
        if type(index) is not int or index not in range(self.size):
            raise IndexError('Unknown context checkpoint')
        return SparsePlasticPolicy.from_state(json.loads(self._slots[index]))

    def digest(self) -> str:
        return hashlib.sha256(json.dumps(self.export_state(), sort_keys=True).encode()).hexdigest()

    def export_state(self) -> dict:
        return {'format': self.FORMAT, 'capacity': self.capacity,
                'slots': [json.loads(slot) for slot in self._slots]}

    @classmethod
    def from_state(cls, data: dict) -> 'SparseContextMemory':
        if not isinstance(data, dict) or set(data) != {'format', 'capacity', 'slots'} or data['format'] != cls.FORMAT:
            raise ValueError('Unknown context memory format')
        memory = cls(capacity=data['capacity'])
        slots = data['slots']
        if not isinstance(slots, list) or len(slots) > memory.capacity:
            raise ValueError('Invalid or oversized checkpoint slots')
        for source in slots:
            if not isinstance(source, dict):
                raise ValueError('Malformed memory slot')
            memory.add(SparsePlasticPolicy.from_state(source))
        return memory

    def retrieve(self, probes: tuple[ReachTrial, ...],
                 make_body: Callable[[ReachTrial], ReachBody], *, steps: int = 3) -> Retrieval:
        """Choose best frozen policy via *observed rewards* on DEV probes.

        The caller supplies a factory connected to a real world/body. The
        hidden inversion flag is never passed into this memory module.
        Every slot receives the same trials, each with a fresh body. Neither
        the probes nor their expected answers enter policy weight updates.
        Evaluation tasks must be distinct from development probes.
        """
        if not self.size or not isinstance(probes, tuple) or not 1 <= len(probes) <= 32:
            raise ValueError('Need 1-32 development probe trials and at least one saved policy')
        if type(steps) is not int or not 1 <= steps <= 8:
            raise ValueError('Probe steps must be in [1, 8]')
        if not callable(make_body):
            raise TypeError('Need a simulator/environment body factory')
        if any(not isinstance(t, ReachTrial) or t.split != 'dev' for t in probes):
            raise ValueError('Never use training or frozen evaluation tasks for context selection')
        before = self.digest()
        scores = []
        for index in range(self.size):
            policy = self.policy(index)
            total = 0.0
            for trial in probes:
                body = make_body(trial)
                if not isinstance(body, ReachBody):
                    raise TypeError('Factory must return ReachBody')
                for _ in range(steps):
                    choice = policy.act(body.observe(), explore=False)
                    # Use *only reward* and public sensory/motor signals.
                    total += body.act(choice)
            scores.append(total / (len(probes) * steps))
        if self.digest() != before:
            raise RuntimeError('Context inference mutated memory snapshots')
        # Deterministic tie: prefer oldest saved policy.
        best = max(range(self.size), key=lambda i: (scores[i], -i))
        return Retrieval(best, tuple(scores), self.size * len(probes) * steps,
                         self.size * len(probes) * steps, self.checkpoint_bytes)