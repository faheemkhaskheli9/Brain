# Multimodal image, video and text I/O (untrained scaffold)

**Status:** runnable research adapter. **Not** a model that recognizes images, understands text, generates original media or learns to control the body. It does not alter Brain World's backprop-free learner or its default behavior. The structural connectivity graph and future learned weights remain separate.

## Install and run

```bash
pip install '.[media]'  # numpy baseline plus optional Pillow and OpenCV-headless
python research/multimodal_io.py
python -m unittest discover -s research -p 'test_multimodal_io.py' -v
```

From repository root:

```python
# not run here (optional Pillow / OpenCV codecs required)
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, "research")
from multimodal_io import MultimodalBridge

brain_io = MultimodalBridge()
rgb = np.zeros((32, 32, 3), dtype=np.uint8)
image_packets = brain_io.image_input(rgb)  # V1 in two hemispheres
text_packets = brain_io.text_input("Hello سنڌي اردو")
image_png = brain_io.image_output(rgb)    # supplied pixels, not generated
text_utf8 = brain_io.text_output("response supplied by caller")
Path("/tmp/image.png").write_bytes(image_png)
print(len(image_packets), len(text_packets), text_utf8.decode("utf-8"))

# Input MP4 frames are timestamped, bounded, and yield V1 and visual-change packets.
brain_io.video_output([rgb, rgb.copy()], Path("/tmp/movie.mp4"), fps=10)
timestamped_packets = brain_io.video_input(Path("/tmp/movie.mp4"))
print(len(timestamped_packets))
```

Media interface contract:

| Media | Input | Cortical interface | Output |
|---|---|---|---|
| Image | PNG/JPEG bytes or Path, or uint8 RGB ndarray | RGB 8x8 features per contralateral visual half-field → L/R V1 | PNG bytes (JPEG also supported by `write_image`) |
| Video | MP4/AVI Path, no sound track processed | Every frame: V1 spatial features + adjacent-frame visual changes routed to `visual_assoc`, timestamped | MP4 video assembled from caller-supplied RGB frames |
| Text | Python Unicode string; UTF-8 byte chunks + length | Symbolic injection into left orthography/temporal-language areas (software representation, **not** biological text senses) | UTF-8 bytes from caller-supplied string |

### Anatomical interpretation

The schematic now has **78 nodes and 142 connections** (previously 70/122).
It adds four abstract left/right populations: orthographic ventral temporal region,
temporal language network, frontal language network and writing premotor.
Nodes and directional edges are **illustrative priors**, not recorded neuron connections.
`vision_pixels` and `visual_change` are mathematical preprocessed inputs,
not spikes or measured human receptive fields. For images, left visual field
routes to the right-hemisphere V1 port and vice versa. This is a simplified
hemifield convention, not a simulation of eyes, optics or optic-chiasm anatomy.
Text bytes are handed to an interface without simulated literacy acquisition;
actual human written-language comprehension depends on visual and language
circuits developed through experience. Output text/images/video are **external
rendering actions**, not biological cortex-generated content or learned skills.

### Bounded resources and failure behavior

- Image: decoded RGB up to 8 million pixels, compressed input/output up to 20 MB.
- Video: input ≤20 MB; ≤300 frames, ≤96 MB decoded RGB; finite FPS required.
  Output MP4 requires even dimensions, FPS (0,60] and matching uint8 RGB sizes.
  OpenCV `mp4v` encoder/decoder support depends on build and system codecs.
- Text: UTF-8 byte budget 256 KiB, fixed 32-byte + length packets; supports
  Unicode scripts without changing meaning or translating them.
- Reject malformed image and video data, invalid text packet sizes/padding,
  nonfinite values, oversized arrays, and unknown sensory channels.
- This version loads a **bounded** video clip into memory, not arbitrary
  streaming/live-video input. MP4 is lossy; video pixel-exact round-trip is
  not promised. Audio tracks, OCR, speech recognition and speech synthesis
  are **not** implemented.
- No decoder is a generative model: callers explicitly supply the output
  string, output pixels or output frames.

## Optional sparse event routing downstream

The [event-driven sparse router](sparse-connectivity.md) accepts these
sensory packets through `network.input_packets(packets)` and routes
nonzero activity only along explicitly present, enabled structural arcs
whose weights have been assigned. For now, this adapter applies fixed,
lossy mean-absolute pooling to each packet; no trained multimodal
representation or understanding is implemented. The original media
input/output codecs remain independent of routing.

## Adversarial evaluation

1. **Interface correctness:** different images and text scripts route to
   distinct ports; verify image hemifield inversion, UTF-8 round-trip,
   video time order and frame-reset behavior.
2. **No fake capability:** output/echo tests must not be reported as learned
   image/video generation, comprehension, reading, writing or agency.
3. **Missing modalities:** audio within videos is ignored. No tactile/retinal
   simulator or object detection/OCR exists.
4. **Resource exhaustion:** enforce bounded frames, dimensions, bytes, and
   explicitly reject malformed inputs. Treat untrusted media codecs as
   optional native dependencies requiring standard security updates.
5. **Future falsifiable learning:** pre-register control task, matched
   topology/rewired alternatives, no-feedback and shuffled-packet baselines,
   several seeds, frozen held-out tasks, error correction, retention and
   compute budgets before attaching any plasticity model.

## Literature context (not implementation validation)

- Fedorenko, Ivanova & Regev (2024), *Nature Reviews Neuroscience*: the
  core human language network is distinct from low-level perceptual/motor
  interfaces: https://doi.org/10.1038/s41583-024-00802-4
- Turker et al. (2025), adult reading meta-analysis: left visual/motor regions
  show relative selectivity for letters/text:
  https://doi.org/10.1016/j.neubiorev.2025.106166
- The VWFA changes with reading experience, rather than representing a native
  text sensor: https://pmc.ncbi.nlm.nih.gov/articles/PMC5856411/

See [structural connectome](structural-connectome.md) for the broader
untrained anatomy, spinal motor interface and measured-vs-schematic caveats.
