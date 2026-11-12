"""Deterministic multimodal bridge tests: no learned content claims."""

import tempfile
import unittest
from pathlib import Path

import numpy as np

from multimodal_io import (
    MAX_BYTES, MAX_TEXT_BYTES, MultimodalBridge, decode_text, encode_text,
    read_image, read_video, write_image, write_video,
)
from structural_connectome import LearningWeights, make_schematic_graph


class MultimodalTests(unittest.TestCase):
    def setUp(self):
        self.bridge = MultimodalBridge()
        self.image = np.zeros((16, 20, 3), dtype=np.uint8)
        self.image[:, :10, 0] = 255  # left visual field is red
        self.image[:, 10:, 1] = 255  # right visual field is green

    def test_image_png_roundtrip_has_distinct_visual_hemifields(self):
        png = self.bridge.image_output(self.image)
        np.testing.assert_array_equal(read_image(png), self.image)
        packets = self.bridge.image_input(png)
        self.assertEqual({p.cortical_target for p in packets}, {'L_v1', 'R_v1'})
        by_side = {p.hemisphere: p.values for p in packets}
        self.assertEqual(len(by_side['L']), 8 * 8 * 3)
        self.assertEqual(len(by_side['R']), 8 * 8 * 3)
        self.assertEqual(by_side['R'][0:3], (1., 0., 0.))
        self.assertEqual(by_side['L'][0:3], (0., 1., 0.))
        self.assertEqual(len(self.bridge.image_input(self.image)), 2)

    def test_jpeg_decode(self):
        jpeg = write_image(self.image, fmt='JPEG')
        decoded = read_image(jpeg)
        self.assertEqual(decoded.shape, self.image.shape)
        self.assertEqual(decoded.dtype, np.uint8)

    def test_image_invalid_format_size_and_shape(self):
        for bad in (np.zeros((2, 3, 4), dtype=np.uint8), np.zeros((1, 1, 3), dtype=np.uint8),
                    np.zeros((8, 8, 3), dtype=np.float32)):
            with self.subTest(shape=bad.shape), self.assertRaises(ValueError):
                self.bridge.image_output(bad)
        with self.assertRaises(ValueError):
            read_image(b'not-an-image')
        with self.assertRaises(ValueError):
            read_image(b'x' * (MAX_BYTES + 1))
        with self.assertRaises(ValueError):
            write_image(self.image, fmt='TIFF')

    def test_unicode_text_roundtrip_across_packet_boundaries(self):
        message = 'Hello, سنڌي اردو 你好! ' * 8
        packets = encode_text(message)
        self.assertGreater(len(packets), 1)
        self.assertEqual(decode_text(packets), message)
        inputs = self.bridge.text_input(message)
        self.assertEqual(len(inputs), len(packets))
        self.assertTrue(all(p.entry_region == 'L_orthography' and p.cortical_target == 'L_language_temporal'
                            for p in inputs))
        self.assertEqual(self.bridge.text_output(message).decode('utf-8'), message)
        self.assertEqual(self.bridge.text_input(''), ())

    def test_unicode_malformed_and_oversized_packets_rejected(self):
        with self.assertRaises(ValueError):
            encode_text('x' * (MAX_TEXT_BYTES + 1))
        with self.assertRaises(ValueError):
            self.bridge.text_output('x' * (MAX_TEXT_BYTES + 1))
        with self.assertRaises(ValueError):
            decode_text([[0.] * 32 + [3.]])
        with self.assertRaises(ValueError):
            decode_text([[0., 1.] + [0.] * 30 + [1 / 32]])
        with self.assertRaises(UnicodeDecodeError):
            decode_text([[255 / 255] + [0.] * 31 + [1 / 32]])

    def test_mp4_write_decode_motion_and_time(self):
        frames = [np.full((16, 20, 3), n * 30, dtype=np.uint8) for n in (0, 1, 2, 3)]
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'clip.mp4'
            self.bridge.video_output(frames, path, fps=10)
            decoded = read_video(path)
            self.assertEqual(len(decoded), 4)
            self.assertAlmostEqual(decoded[-1].time_s, 0.3, places=3)
            events = self.bridge.video_input(path)
            self.assertEqual(len(events), 4)
            self.assertEqual([t for t, _ in events], [f.time_s for f in decoded])
            self.assertTrue(all(len(packets) == 4 for _, packets in events))
            motion_first = [p for p in events[0][1] if p.modality == 'visual_change']
            self.assertTrue(all(all(v == 0 for v in p.values) for p in motion_first))
            motion_second = [p for p in events[1][1] if p.modality == 'visual_change']
            self.assertTrue(any(any(v != 0 for v in p.values) for p in motion_second))
            repeat = self.bridge.video_input(path)
            self.assertTrue(all(all(v == 0 for v in p.values) for p in repeat[0][1]
                                if p.modality == 'visual_change'))

    def test_bad_video_budgets_shapes_and_filename(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            with self.assertRaises(ValueError):
                write_video([self.image], root / 'clip.txt')
            with self.assertRaises(ValueError):
                write_video([self.image, np.zeros((10, 10, 3), dtype=np.uint8)], root / 'clip.mp4')
            with self.assertRaises(ValueError):
                write_video([self.image], root / 'clip.mp4', fps=0)
            with self.assertRaises(ValueError):
                read_video(root / 'missing.mp4')

    def test_no_learned_generation_or_weight_updates(self):
        self.assertTrue(all(w is None for w in LearningWeights(make_schematic_graph()).values.values()))
        self.assertFalse(hasattr(self.bridge, 'generate'))
        self.assertFalse(hasattr(self.bridge, 'predict'))


if __name__ == '__main__':
    unittest.main()
