"""Bounded PCM WAV input/output and temporal auditory features for the Brain scaffold.

Engineering I/O only: no neural signal simulation, speech recognition, or audio
synthesis. Returned waveforms are externally supplied; cortical feature packets
are fixed, lossy summaries rather than learned representations.
"""

from __future__ import annotations

import io
import math
import wave
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from sensorimotor_bridge import SensoryPacket, SensoryRouter

MIN_SAMPLE_RATE = 8_000
MAX_SAMPLE_RATE = 48_000
MAX_SECONDS = 30
MAX_WAV_BYTES = 12_000_000
WINDOW = 512
HOP = 256
BANDS = 8
FEATURE_CHANNELS = BANDS + 1  # 8 log-spaced spectral energies, plus RMS loudness


@dataclass(frozen=True)
class AudioClip:
    """Normalized float32 samples shaped (time, channels), 1 or 2 channels."""

    sample_rate: int
    samples: np.ndarray

    def __post_init__(self) -> None:
        _validate_samples(self.samples, self.sample_rate)

    @property
    def duration_s(self) -> float:
        return len(self.samples) / self.sample_rate


def _validate_samples(samples: np.ndarray, sample_rate: int) -> None:
    if (type(sample_rate) is not int or not MIN_SAMPLE_RATE <= sample_rate <= MAX_SAMPLE_RATE):
        raise ValueError(f"Sample rate must be an integer between {MIN_SAMPLE_RATE} and {MAX_SAMPLE_RATE}")
    if not isinstance(samples, np.ndarray) or samples.dtype != np.float32 or samples.ndim != 2:
        raise ValueError("Samples must be a float32 array shaped (time, channels)")
    n, channels = samples.shape
    if channels not in (1, 2) or n == 0 or n > sample_rate * MAX_SECONDS:
        raise ValueError("Expected 1-2 channels, and between 1 sample and 30 seconds of audio")
    if not np.all(np.isfinite(samples)) or np.any(np.abs(samples) > 1):
        raise ValueError("Samples must be finite and normalized within [-1, 1]")


def read_wav(source: bytes | Path) -> AudioClip:
    """Decode uncompressed PCM WAV 8-bit unsigned or 16-bit signed, mono/stereo."""
    if isinstance(source, Path):
        if source.stat().st_size > MAX_WAV_BYTES:
            raise ValueError("WAV exceeds encoded byte budget")
        raw = source.read_bytes()
    elif isinstance(source, bytes):
        raw = source
    else:
        raise TypeError("WAV input must be bytes or pathlib.Path")
    if not raw or len(raw) > MAX_WAV_BYTES:
        raise ValueError("Empty or oversized WAV")
    try:
        with wave.open(io.BytesIO(raw), "rb") as wav:
            rate, channels, n, width = (
                wav.getframerate(), wav.getnchannels(), wav.getnframes(), wav.getsampwidth()
            )
            if wav.getcomptype() != "NONE" or width not in (1, 2):
                raise ValueError("Only uncompressed 8-bit or 16-bit PCM WAV is supported")
            if (type(rate) is not int or not MIN_SAMPLE_RATE <= rate <= MAX_SAMPLE_RATE or channels not in (1, 2)
                    or n == 0 or n > rate * MAX_SECONDS):
                raise ValueError("Unsupported sample rate, channel count or audio duration")
            if n * channels * width > MAX_WAV_BYTES:
                raise ValueError("Decoded audio exceeds budget")
            pcm = wav.readframes(n)
            if len(pcm) != n * channels * width:
                raise ValueError("Truncated PCM data")
            # Reject unexpected additional samples beyond the header's declared frame count.
            if wav.readframes(1):
                raise ValueError("WAV contains more data than declared")
    except (EOFError, wave.Error, OSError) as exc:
        raise ValueError("Malformed or unsupported WAV container") from exc
    if width == 1:
        samples = (np.frombuffer(pcm, dtype=np.uint8).astype(np.float32) - 128) / 128
    else:
        samples = np.frombuffer(pcm, dtype="<i2").astype(np.float32) / 32768.0
    return AudioClip(rate, samples.reshape(n, channels).copy())


def write_wav(samples: np.ndarray, sample_rate: int = 16_000) -> bytes:
    """Encode caller-supplied normalized float32 samples as PCM16 WAV bytes."""
    _validate_samples(samples, sample_rate)
    pcm = np.clip(np.rint(samples.astype(np.float64) * 32768), -32768, 32767).astype("<i2")
    with io.BytesIO() as handle:
        with wave.open(handle, "wb") as wav:
            wav.setnchannels(samples.shape[1])
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(pcm.tobytes())
        result = handle.getvalue()
    if len(result) > MAX_WAV_BYTES:
        raise ValueError("Encoded WAV exceeds byte budget")
    return result


def _spectrum(chunk: np.ndarray) -> tuple[float, ...]:
    """Eight log-spaced FFT magnitudes and RMS amplitude; fixed non-learned features."""
    if len(chunk) != WINDOW:
        raise ValueError("Internal audio window size mismatch")
    window = np.hanning(WINDOW).astype(np.float32)
    spectrum = np.abs(np.fft.rfft(chunk * window)) * 2 / float(window.sum())
    # FFT bins are distributed logarithmically to allocate more resolution to
    # low frequencies; these are not calibrated auditory filters or cochlear bands.
    cuts = np.geomspace(1, len(spectrum), BANDS + 1)
    out = []
    for start, stop in zip(cuts[:-1], cuts[1:]):
        low = max(1, int(math.floor(start)))
        high = max(low + 1, int(math.ceil(stop)))
        out.append(min(1.0, float(np.max(spectrum[low:high]))))
    out.append(min(1.0, float(np.sqrt(np.mean(chunk.astype(np.float64) ** 2)))))
    return tuple(out)


def audio_packets(clip: AudioClip, router: SensoryRouter) -> tuple[tuple[float, tuple[SensoryPacket, ...]], ...]:
    """Time-ordered stereo/mono features targeting A1 and auditory association.

    Stereo channel L feeds L auditory cortex, R feeds R; mono is duplicated.
    This is a SOFTWARE convention, NOT physiological ear-to-cortex laterality.
    """
    _validate_samples(clip.samples, clip.sample_rate)
    result = []
    previous = None
    n, channels = clip.samples.shape
    for start in range(0, n, HOP):
        window = np.zeros((WINDOW, channels), dtype=np.float32)
        take = min(WINDOW, n - start)
        window[:take] = clip.samples[start:start + take]
        features = [_spectrum(window[:, channel]) for channel in range(channels)]
        current = {"L": features[0], "R": features[1] if channels == 2 else features[0]}
        changes = {
            side: tuple(current[side][k] - previous[side][k] for k in range(FEATURE_CHANNELS))
            if previous is not None else (0.0,) * FEATURE_CHANNELS
            for side in ("L", "R")
        }
        packets = router.route({"audio_spectrum": current, "audio_change": changes})
        result.append((start / clip.sample_rate, packets))
        previous = current
    return tuple(result)


if __name__ == "__main__":
    from sensorimotor_bridge import SensorimotorLoop

    fs = 16_000
    t = np.arange(fs // 4) / fs
    sample = (0.25 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)[:, None]
    clip = read_wav(write_wav(sample, fs))
    windows = audio_packets(clip, SensorimotorLoop().sensors)
    print(f"Audio I/O: {len(windows)} windows, {len(windows[0][1])} auditory packets/window")
