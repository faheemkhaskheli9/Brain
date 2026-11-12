"""Tiny deterministic association task for falsifiable local synaptic learning.

A hidden verifier determines whether an action matches the signed auditory-like
cue. The actor receives ONLY the public feature vector, never the target label.
Different split namespaces and seeds yield disjoint reproducible instances.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Trial:
    features: tuple[float, ...]
    answer: int  # verifier-only; never passed to the policy
    split: str
    key: str

    def observe(self) -> np.ndarray:
        return np.asarray(self.features, dtype=np.float32)

    def reward(self, action: int) -> int:
        if type(action) is not int or action not in (0, 1):
            raise ValueError('Action must be 0 or 1')
        return 1 if action == self.answer else -1


def trials(split: str, seed: int, count: int) -> tuple[Trial, ...]:
    """Train/dev/test use disjoint RNG streams; no old #112 tasks are reused."""
    if split not in ('train', 'dev', 'eval') or type(seed) is not int or type(count) is not int or count < 1:
        raise ValueError('Invalid split, seed or trial count')
    salt = {'train': 103, 'dev': 211, 'eval': 421}[split]
    rng = random.Random(seed * 10000019 + salt)
    out = []
    for idx in range(count):
        sign = (-1 if rng.random() < 0.5 else 1)
        # Hidden rule is fixed across splits. Distractors and noise are independent.
        # Development and eval use a different cue amplitude: transfer test.
        strength = {'train': 1.0, 'dev': 0.7, 'eval': 0.5}[split]
        features = (sign * strength, *(rng.choice((-1.0, 1.0)) for _ in range(21)),
                    rng.uniform(-1, 1), rng.uniform(-1, 1))
        out.append(Trial(tuple(features), 0 if sign > 0 else 1,
                         split, f'{split}:{seed}:{idx}'))
    return tuple(out)