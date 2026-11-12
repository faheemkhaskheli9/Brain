"""Explicit sensory entry ports and bounded toy-body motor output.

Interface only: NO learning, neural dynamics, or biological weight assumptions.
The motor activity argument must come from a separate, future neural model.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from numbers import Real
from typing import Mapping, Sequence

from structural_connectome import StructuralGraph, make_schematic_graph


@dataclass(frozen=True)
class SensoryPort:
    name: str
    relay: str
    cortex: str
    channels: int | None  # None = body-dependent proprioception width


# Channel counts and normalized features are software contracts, NOT measurements.
PORTS = (
    SensoryPort("vision", "lgn", "v1", 3),
    SensoryPort("vision_pixels", "lgn", "v1", 8 * 8 * 3),
    SensoryPort("visual_change", "lgn", "visual_assoc", 8 * 8 * 3),
    SensoryPort("text_symbols", "orthography", "language_temporal", 33),
    SensoryPort("hearing", "mgb", "a1", 3),
    SensoryPort("touch", "thalamus", "s1", 2),
    SensoryPort("proprioception", "thalamus", "s1", None),
    SensoryPort("smell", "olfactory_bulb", "piriform", 2),
    SensoryPort("taste", "gustatory_thalamus", "gustatory_cortex", 5),
    SensoryPort("balance", "vestibular_nuclei", "vestibular_cortex", 3),
    SensoryPort("interoception", "posterior_insula", "posterior_insula", 2),
)


def _unit_vector(values: Sequence[float], width: int, label: str) -> tuple[float, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, (list, tuple)) or len(values) != width:
        raise ValueError(f"{label}: expected {width} normalized numeric channels")
    if any(isinstance(v, bool) or not isinstance(v, Real) or not math.isfinite(v) or abs(v) > 1 for v in values):
        raise ValueError(f"{label}: all channels must be finite numbers in [-1, 1]")
    return tuple(float(v) for v in values)


@dataclass(frozen=True)
class SensoryPacket:
    modality: str
    hemisphere: str
    entry_region: str
    cortical_target: str
    values: tuple[float, ...]


class SensoryRouter:
    """Validates observations and exposes relay/cortical targets; propagates NOTHING."""

    def __init__(self, graph: StructuralGraph, joints: tuple[str, ...]):
        ids = {region.id for region in graph.regions}
        self.ports = {port.name: port for port in PORTS}
        if not joints or len(set(joints)) != len(joints):
            raise ValueError("At least one unique joint per side is required")
        self.proprioception_width = len(joints) * 2
        for port in PORTS:
            for side in ("L", "R"):
                if f"{side}_{port.relay}" not in ids or f"{side}_{port.cortex}" not in ids:
                    raise ValueError(f"Graph missing sensory pathway for {port.name}, {side}")

    def route(self, observations: Mapping[str, Mapping[str, Sequence[float]]]) -> tuple[SensoryPacket, ...]:
        if not isinstance(observations, Mapping):
            raise ValueError("Observations must map modalities to hemisphere-specific values")
        packets = []
        for name, per_side in observations.items():
            if name not in self.ports or not isinstance(per_side, Mapping):
                raise ValueError(f"Unknown modality or invalid hemisphere mapping: {name}")
            port = self.ports[name]
            for side, values in per_side.items():
                if side not in ("L", "R"):
                    raise ValueError(f"Unknown hemisphere {side!r}")
                width = self.proprioception_width if port.channels is None else port.channels
                packed = _unit_vector(values, width, f"{name}/{side}")
                packets.append(SensoryPacket(name, side, f"{side}_{port.relay}", f"{side}_{port.cortex}", packed))
        return tuple(packets)


@dataclass(frozen=True)
class MotorCommand:
    name: str
    drive: float


class MotorDecoder:
    """Fixed actuator mapping from neural motor-pool activity, not learned weights."""

    def __init__(self, graph: StructuralGraph, joints: tuple[str, ...]):
        ids = {region.id for region in graph.regions}
        if not joints or len(set(joints)) != len(joints) or any(not j or "_" in j for j in joints):
            raise ValueError("Joints must have distinct nonempty names without underscores")
        if not {"L_motor_pool", "R_motor_pool"}.issubset(ids):
            raise ValueError("Structural graph needs left/right spinal motor pools")
        self.joints = joints

    def decode(self, motor_activity: Mapping[str, Sequence[float]] | None = None) -> tuple[MotorCommand, ...]:
        """Missing signals -> zero output. Unexpected/unbounded signals fail closed."""
        if motor_activity is None:
            motor_activity = {}
        if not isinstance(motor_activity, Mapping) or any(k not in ("L_motor_pool", "R_motor_pool") for k in motor_activity):
            raise ValueError("Motor activity must target known spinal motor pools")
        out = []
        for side in ("L", "R"):
            source = f"{side}_motor_pool"
            values = _unit_vector(motor_activity.get(source, [0.0] * len(self.joints)), len(self.joints), source)
            out.extend(MotorCommand(f"{side}_{joint}", value) for joint, value in zip(self.joints, values))
        return tuple(out)


class SimpleJointBody:
    """Abstract bounded joint positions and velocities, not a biomechanics simulator."""

    def __init__(self, joints: tuple[str, ...] = ("hip", "knee")):
        if not joints or len(set(joints)) != len(joints) or any(not j or "_" in j for j in joints):
            raise ValueError("Invalid joint names")
        self.joints = joints
        self.positions = {f"{s}_{j}": 0.0 for s in ("L", "R") for j in joints}
        self.velocities = self.positions.copy()

    def apply(self, commands: tuple[MotorCommand, ...], *, dt: float = 0.05) -> None:
        if not isinstance(dt, Real) or isinstance(dt, bool) or not math.isfinite(dt) or not 0 < dt <= 0.1:
            raise ValueError("dt must be in (0, 0.1] for this toy integrator")
        expected = set(self.positions)
        if {cmd.name for cmd in commands} != expected or len(commands) != len(expected):
            raise ValueError("Body requires exactly one command per joint")
        for cmd in commands:
            _unit_vector([cmd.drive], 1, cmd.name)
        # Validate everything BEFORE mutating any joint.
        for cmd in commands:
            velocity = max(-1.0, min(1.0, 0.85 * self.velocities[cmd.name] + dt * cmd.drive))
            position = max(-1.0, min(1.0, self.positions[cmd.name] + dt * velocity))
            self.velocities[cmd.name], self.positions[cmd.name] = velocity, position

    def proprioception(self) -> dict[str, list[float]]:
        return {
            side: [self.positions[f"{side}_{joint}"] for joint in self.joints]
            + [self.velocities[f"{side}_{joint}"] for joint in self.joints]
            for side in ("L", "R")
        }


class SensorimotorLoop:
    """Sensory -> optional future brain -> motor -> body -> proprioception.

    Does not invent the future brain's forward pass or infer motor activity from
    sensory features. The supplied activity is explicitly an external injection.
    """

    def __init__(self, graph: StructuralGraph | None = None, body: SimpleJointBody | None = None):
        self.graph = graph if graph is not None else make_schematic_graph()
        self.body = body if body is not None else SimpleJointBody()
        self.sensors = SensoryRouter(self.graph, self.body.joints)
        self.motors = MotorDecoder(self.graph, self.body.joints)

    def step(self, observations: Mapping[str, Mapping[str, Sequence[float]]],
             motor_activity: Mapping[str, Sequence[float]] | None = None, *, dt: float = 0.05) -> dict:
        incoming = self.sensors.route(observations)
        commands = self.motors.decode(motor_activity)
        self.body.apply(commands, dt=dt)
        feedback = self.sensors.route({"proprioception": self.body.proprioception()})
        return {
            "sensory": incoming,
            "motor": commands,
            "proprioceptive_feedback": feedback,
            "motor_source": "external activity" if motor_activity is not None else "no neural motor model: zero drive",
        }


if __name__ == "__main__":
    loop = SensorimotorLoop()
    stopped = loop.step({"vision": {"L": [0.3, 0.1, 0.4]}})
    injected = loop.step({"touch": {"R": [0.4, 0.2]}}, {"L_motor_pool": [0.8, 0.0]})
    print({"zero_motor_drive": [command.drive for command in stopped["motor"]],
           "externally_injected_motor_drive": [command.drive for command in injected["motor"]],
           "body_position": loop.body.positions})
