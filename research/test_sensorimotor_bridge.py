"""Tests for distinct sensory cortices and an externally driven toy body."""

import math
import unittest

from sensorimotor_bridge import MotorDecoder, PORTS, SensorimotorLoop, SensoryRouter, SimpleJointBody
from structural_connectome import LearningWeights, make_schematic_graph


class SensorimotorTests(unittest.TestCase):
    def setUp(self):
        self.graph = make_schematic_graph()
        self.body = SimpleJointBody()
        self.loop = SensorimotorLoop(self.graph, self.body)

    def test_all_senses_have_anatomical_entry_and_cortex(self):
        ids = {r.id for r in self.graph.regions}
        for port in PORTS:
            for side in ("L", "R"):
                self.assertIn(f"{side}_{port.relay}", ids)
                self.assertIn(f"{side}_{port.cortex}", ids)
        self.assertEqual(len(self.graph.regions), 78)

    def test_visual_auditory_and_smell_target_distinct_relays(self):
        data = self.loop.sensors.route({"vision": {"L": [0, 0, 1]},
                                        "hearing": {"R": [0.1, -0.2, 0.3]},
                                        "smell": {"L": [0.1, 0.8]}})
        self.assertEqual([(p.entry_region, p.cortical_target) for p in data],
                         [("L_lgn", "L_v1"), ("R_mgb", "R_a1"), ("L_olfactory_bulb", "L_piriform")])

    def test_all_senses_are_independently_addressable(self):
        sensory = {port.name: {"L": [0] * (port.channels or 4)} for port in PORTS}
        packets = self.loop.sensors.route(sensory)
        self.assertEqual(len(packets), len(PORTS))
        self.assertEqual({p.modality for p in packets}, set(sensory))

    def test_sensor_input_validation(self):
        for bad in ({"unknown": {"L": [1]}}, {"vision": {"Q": [0, 0, 0]}},
                    {"vision": {"L": [0, 0]}}, {"vision": {"L": [math.nan, 0, 0]}},
                    {"taste": {"R": [False] * 5}}, {"touch": {"L": [3, 0]}}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.loop.sensors.route(bad)

    def test_corticospinal_crossing_and_spinal_motor_output(self):
        names = {(edge.source, edge.target, edge.pathway) for edge in self.graph.connections}
        self.assertIn(("L_m1", "R_spinal_cord", "crossed_corticospinal_schematic"), names)
        self.assertIn(("R_m1", "L_spinal_cord", "crossed_corticospinal_schematic"), names)
        self.assertIn(("L_spinal_cord", "L_motor_pool", "spinal_motor_pool"), names)

    def test_no_learning_weights_no_spontaneous_movement(self):
        self.assertTrue(all(v is None for v in LearningWeights(self.graph).values.values()))
        before = self.body.positions.copy()
        result = self.loop.step({"vision": {"L": [0.5, 0.2, 0.1]}})
        self.assertEqual(before, self.body.positions)
        self.assertTrue(all(command.drive == 0.0 for command in result["motor"]))
        self.assertEqual(result["motor_source"], "no neural motor model: zero drive")

    def test_external_motor_activity_moves_one_joint_and_returns_feedback(self):
        output = self.loop.step({"touch": {"R": [0.5, 0.2]}}, {"L_motor_pool": [0.8, 0]})
        self.assertGreater(self.body.positions["L_hip"], 0)
        self.assertEqual(self.body.positions["R_hip"], 0)
        feedback = {packet.hemisphere: packet.values for packet in output["proprioceptive_feedback"]}
        self.assertEqual(len(feedback["L"]), 4)
        self.assertGreater(feedback["L"][0], 0)
        self.assertEqual(feedback["R"], (0.0, 0.0, 0.0, 0.0))

    def test_invalid_motor_inputs_and_timestep_do_not_mutate_body(self):
        original = self.body.positions.copy()
        for bad in ({"X_motor_pool": [1, 0]}, {"L_motor_pool": [2, 0]},
                    {"L_motor_pool": [0]}, {"L_motor_pool": [float("inf"), 0]}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.loop.step({}, bad)
            self.assertEqual(self.body.positions, original)
        for dt in (0, -0.1, math.nan, 1.0):
            with self.subTest(dt=dt), self.assertRaises(ValueError):
                self.loop.step({}, {"L_motor_pool": [1, 1]}, dt=dt)
            self.assertEqual(self.body.positions, original)

    def test_sensors_failure_before_actuation(self):
        with self.assertRaises(ValueError):
            self.loop.step({"vision": {"L": [999, 0, 0]}}, {"L_motor_pool": [1, 1]})
        self.assertEqual(sum(self.body.positions.values()), 0)

    def test_configurable_body_joint_interface(self):
        body = SimpleJointBody(("shoulder", "elbow", "wrist"))
        loop = SensorimotorLoop(self.graph, body)
        loop.step({}, {"R_motor_pool": [0, 0, 0.4]})
        self.assertGreater(body.positions["R_wrist"], 0)
        self.assertEqual(len(loop.sensors.route({"proprioception": body.proprioception()})[0].values), 6)
        with self.assertRaises(ValueError):
            MotorDecoder(self.graph, ("hip", "hip"))
        with self.assertRaises(ValueError):
            SensoryRouter(self.graph, ())


if __name__ == "__main__":
    unittest.main()
