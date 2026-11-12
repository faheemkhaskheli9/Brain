"""Deterministic audio I/O, auditory routing and malformed-data tests."""

import io
import math
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

from audio_io import AudioClip, HOP, MAX_SECONDS, MAX_WAV_BYTES, audio_packets, read_wav, write_wav
from multimodal_io import MultimodalBridge
from sparse_connectivity import make_sparse_schematic


class AudioIOTests(unittest.TestCase):
    def setUp(self):
        self.brain = MultimodalBridge()
        self.rate = 16_000
        self.seconds = 0.12
        self.t = np.arange(int(self.rate * self.seconds)) / self.rate

    def sine(self, hz: float, amplitude: float = 0.6) -> np.ndarray:
        return (amplitude * np.sin(2 * math.pi * hz * self.t)).astype(np.float32)

    def test_pcm16_roundtrip_preserves_mono_and_sample_rate(self):
        signal = self.sine(440)[:, None]
        encoded = self.brain.audio_output(signal, sample_rate=self.rate)
        decoded = read_wav(encoded)
        self.assertEqual(decoded.sample_rate, self.rate)
        self.assertEqual(decoded.samples.shape, signal.shape)
        np.testing.assert_allclose(decoded.samples, signal, atol=1 / 32768)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'sample.wav'
            path.write_bytes(encoded)
            from_disk = read_wav(path)
            np.testing.assert_array_equal(from_disk.samples, decoded.samples)

    def test_stereo_routes_separate_hemispheres_and_distinguishes_spectral_peaks(self):
        signal = np.stack((self.sine(250), self.sine(3400)), axis=1)
        packets = self.brain.audio_input(AudioClip(self.rate, signal))
        self.assertGreater(len(packets), 1)
        first = { (packet.modality, packet.hemisphere): packet for packet in packets[0][1] }
        self.assertEqual(len(first), 4)
        self.assertEqual(first['audio_spectrum', 'L'].cortical_target, 'L_a1')
        self.assertEqual(first['audio_spectrum', 'R'].entry_region, 'R_mgb')
        self.assertEqual(first['audio_change', 'L'].cortical_target, 'L_auditory_assoc')
        low = first['audio_spectrum', 'L'].values[:8]
        high = first['audio_spectrum', 'R'].values[:8]
        self.assertLess(np.argmax(low), np.argmax(high))
        self.assertNotEqual(low, high)

    def test_mono_audio_duplicates_signal_to_both_cortices(self):
        waveform = self.sine(440)[:, None]
        sequence = self.brain.audio_input(write_wav(waveform, self.rate))
        for _, packets in sequence:
            by_side = {p.hemisphere: p.values for p in packets if p.modality == 'audio_spectrum'}
            self.assertEqual(by_side['L'], by_side['R'])

    def test_audio_change_zero_initially_and_timestamps_are_monotonic(self):
        waveform = np.concatenate((np.zeros(1024, dtype=np.float32), np.ones(1024, dtype=np.float32)))[:, None]
        events = self.brain.audio_input(AudioClip(self.rate, waveform))
        self.assertEqual(events[0][0], 0.0)
        self.assertAlmostEqual(events[1][0], HOP / self.rate)
        self.assertTrue(all(events[i][0] < events[i+1][0] for i in range(len(events)-1)))
        self.assertTrue(all(p.values == (0.0,) * 9 for p in events[0][1] if p.modality == 'audio_change'))
        self.assertTrue(any(any(abs(v) > 0.01 for v in p.values) for _, packets in events[3:]
                            for p in packets if p.modality == 'audio_change'))

    def test_silence_routes_zero_feature_packets_but_no_learned_activity(self):
        clip = AudioClip(self.rate, np.zeros((1024, 2), dtype=np.float32))
        outputs = self.brain.audio_input(clip)
        self.assertTrue(all(all(v == 0 for v in p.values) for _, packets in outputs for p in packets))
        brain_graph = make_sparse_schematic()
        activity = brain_graph.input_packets(outputs[0][1])
        self.assertEqual(activity, {'L_a1': 0.0, 'R_a1': 0.0,
                                    'L_auditory_assoc': 0.0, 'R_auditory_assoc': 0.0})
        self.assertEqual(brain_graph.step(activity).stats.weighted_products, 0)

    def test_8bit_pcm_is_decoded_and_16bit_output_is_supported(self):
        with io.BytesIO() as buffer:
            with wave.open(buffer, 'wb') as wav:
                wav.setframerate(self.rate)
                wav.setnchannels(1)
                wav.setsampwidth(1)
                wav.writeframes(bytes([0, 128, 255]))
            decoded = read_wav(buffer.getvalue())
        np.testing.assert_allclose(decoded.samples[:, 0], [-1, 0, 127/128])

    def test_rejects_24bit_audio_and_bad_codec(self):
        with io.BytesIO() as buffer:
            with wave.open(buffer, 'wb') as wav:
                wav.setframerate(self.rate)
                wav.setnchannels(1)
                wav.setsampwidth(3)
                wav.writeframes(b'\x00\x00\x00')
            with self.assertRaises(ValueError):
                read_wav(buffer.getvalue())
        for bad in (b'abc', b'', b'x'*(MAX_WAV_BYTES+1)):
            with self.subTest(size=len(bad)), self.assertRaises(ValueError):
                read_wav(bad)

    def test_rejects_oversized_duration_bad_channels_and_nonfinite_samples(self):
        for sample in (np.zeros((3, 3), dtype=np.float32),
                       np.zeros((3, 1), dtype=np.float64),
                       np.array([[math.nan]], dtype=np.float32),
                       np.array([[1.1]], dtype=np.float32),
                       np.empty((0, 1), dtype=np.float32)):
            with self.subTest(shape=sample.shape), self.assertRaises(ValueError):
                self.brain.audio_output(sample)
        with self.assertRaises(ValueError):
            self.brain.audio_output(np.zeros((self.rate*(MAX_SECONDS+1), 1), dtype=np.float32))
        with self.assertRaises(ValueError):
            self.brain.audio_output(np.ones((512, 1), dtype=np.float32), sample_rate=100)
        with self.assertRaises(ValueError):
            self.brain.audio_output(np.ones((512, 1), dtype=np.float32), sample_rate=True)

    def test_validation_against_corrupt_rate_and_truncated_wav(self):
        good = self.brain.audio_output(self.sine(440)[:, None], sample_rate=self.rate)
        with self.assertRaises(ValueError):
            read_wav(good[:-4])
        with self.assertRaises(ValueError):
            read_wav(good[:4])

    def test_rejects_invalid_audio_sources(self):
        with self.assertRaises(TypeError):
            self.brain.audio_input(123)
        with self.assertRaises(ValueError):
            self.brain.audio_input(b'not audio')
        with self.assertRaises(ValueError):
            AudioClip(self.rate, np.full((1024, 2), np.inf, dtype=np.float32))

    def test_deterministic_clips_and_no_fake_speech_understanding(self):
        wave_data = self.sine(250)[:, None]
        clip = AudioClip(self.rate, wave_data)
        a = audio_packets(clip, self.brain.sensorimotor.sensors)
        b = audio_packets(clip, self.brain.sensorimotor.sensors)
        self.assertEqual(a, b)
        self.assertFalse(hasattr(self.brain, 'transcribe'))
        self.assertFalse(hasattr(self.brain, 'text_to_speech'))
        self.assertTrue(hasattr(self.brain, 'audio_output'))


if __name__ == '__main__':
    unittest.main()
