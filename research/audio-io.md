# Audio input/output for the untrained Brain scaffold

**Implemented:** bounded mono/stereo uncompressed PCM WAV decoding, lossy
frequency/loudness feature extraction, temporal changes, and PCM16 WAV
serialization of caller-supplied audio. The existing 78-region/142-connection
schematic already has the medial geniculate body (MGB), primary auditory
cortex (A1) and auditory association cortex. **No new anatomical regions or
connections are necessary.**

## Run

```bash
python research/audio_io.py
python -m unittest discover -s research -p 'test_audio_io.py' -v
```

Example for a self-contained generated waveform (a manually specified
440 Hz test signal, **not neural audio generation**):

```python
# not run here: execute with the repository research directory on Python path.
import numpy as np
from pathlib import Path
from multimodal_io import MultimodalBridge

io = MultimodalBridge()
fs = 16_000
t = np.arange(fs // 4) / fs
sound = (0.25 * np.sin(2 * np.pi * 440 * t)).astype("float32")[:, None]
wav_bytes = io.audio_output(sound, sample_rate=fs)
Path("/tmp/example.wav").write_bytes(wav_bytes)

events = io.audio_input(wav_bytes)  # (time_seconds, tuple[SensoryPacket, ...])
print(len(events), events[0][0], len(events[0][1]))  # 16, 0.0, 4
```

## Input and output contracts

| Direction | API | Data |
|---|---|---|
| Audio input | `MultimodalBridge.audio_input(bytes or Path)` | PCM8 unsigned or PCM16 signed WAV |
| Waveform input | `MultimodalBridge.audio_input(AudioClip(...))` | `float32` array, `[samples, 1 or 2 channels]` |
| Audio output | `MultimodalBridge.audio_output(samples, sample_rate=...)` | Serialized PCM16 WAV `bytes` |
| Spectral cortex input | `audio_spectrum` port | 8 log-spaced FFT bands + RMS; MGB → A1 |
| Temporal cortex input | `audio_change` port | 9 component-wise frame differences; MGB entry → auditory association cortex software port |

A 512-sample Hann-window FFT is computed every 256 samples.
The first change packet is all zeros; subsequent packets compare consecutive
feature windows. Time stamps are the start sample divided by sample rate.
Stereo left/right channels map to corresponding cortical hemisphere ports
as a **software convention**, not biological auditory laterality; mono
features are copied to both. The input/output values are normalized.

This is a *toy acoustic encoder*, not a cochlear model, a learned
representation or tonotopically correct simulation. It drops waveform
phase, fine timing, speech identity and other features. Routing its packets
through `research/sparse_connectivity.py` still requires **assigned**
connection weights; by default every connection weight is `None` and
there is no propagation.

### Safety and resource limits

- WAV PCM only: no MP3, FLAC, Opus, AAC or compressed WAV decoding.
- 8,000–48,000 samples/second; 1–2 channels; up to 30 s.
- Maximum input and encoded output: 12 MB.
- Reject nonfinite/unbounded waveforms, invalid channel/sample-rate values,
  oversized files, truncated PCM and unsupported bit depth.
- PCM16 output is quantized, so audio values are approximately, not exactly,
  preserved. No microphone access or audio playback device integration.
- Videos currently carry only visual frames. Audio extraction, synchronization
  and audiovisual multiplexing are separate future tasks.
- No ASR, TTS, sound generation, music understanding or speech grounding.
  Do not count WAV round-trips as evidence of learned skills.

## Adversarial review and next experiments

The fixed 8-band spectral representation is highly lossy: two spoken words
can have similar average band energy and be indistinguishable after regional
pooling. Current stereo mapping is also not a correct model of auditory
projections, which are bilateral. Frequency bands are relative to the
Nyquist interval rather than a calibrated human cochlear frequency map.

Before claiming learning, compare equal-budget, multi-seed downstream
models on held-out tones, environments, spoken symbols and localization.
Ablate temporal-change features and compare against randomized spectral
bins. Track false classifications, repeated errors and forgetting.
Separate genuine learned audio generation from pre-recorded/caller-supplied
waveforms.

Background: the MGB-to-A1 thalamocortical projection is an established
auditory sensory pathway (see the existing structural anatomy notes and
https://doi.org/10.1016/j.bandl.2012.05.004). Its use here is an
illustrative routing hypothesis, not detailed physiological validation.
