"""Image, video and Unicode text I/O for the *untrained* structural brain.

Media codecs are not neural encoders, learned representations or creative outputs.
The file/image/video content is supplied by the caller; the graph remains unchanged.
Pillow (images) and OpenCV (videos) are optional and loaded only when used.
"""

from __future__ import annotations

import io
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np

from sensorimotor_bridge import SensoryPacket, SensorimotorLoop

GRID = 8
TEXT_CHUNK = 32
MAX_PIXELS = 8_000_000
MAX_BYTES = 20_000_000
MAX_VIDEO_FRAMES = 300
MAX_VIDEO_RGB_BYTES = 96_000_000
MAX_TEXT_BYTES = 262_144


def _pillow():
    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError as exc:
        raise RuntimeError('Image I/O requires: pip install ".[media]"') from exc
    return Image, UnidentifiedImageError


def _cv2():
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError('Video I/O requires: pip install ".[media]"') from exc
    return cv2


def validate_frame(pixels: np.ndarray) -> np.ndarray:
    """Accept exact HxWx3 uint8 RGB arrays, enforcing small bounded media."""
    if not isinstance(pixels, np.ndarray) or pixels.ndim != 3 or pixels.shape[-1] != 3:
        raise ValueError('RGB frame must be a numpy HxWx3 array')
    h, w, _ = pixels.shape
    if h < 1 or w < 2 or h * w > MAX_PIXELS or pixels.dtype != np.uint8:
        raise ValueError('RGB frame must be uint8, >=2 pixels wide and <=MAX_PIXELS')
    return pixels


def read_image(source: bytes | Path) -> np.ndarray:
    """Decode RGB PNG/JPEG with optional Pillow; reject large/decompression-bomb files."""
    Image, UnidentifiedImageError = _pillow()
    if isinstance(source, Path):
        if source.stat().st_size > MAX_BYTES:
            raise ValueError('Image file exceeds byte budget')
        raw = source.read_bytes()
    elif isinstance(source, bytes):
        raw = source
    else:
        raise TypeError('Image source must be bytes or Path')
    if len(raw) > MAX_BYTES:
        raise ValueError('Image file exceeds byte budget')
    try:
        with Image.open(io.BytesIO(raw)) as im:
            if im.format not in {'PNG', 'JPEG'} or im.width < 2 or im.height < 1 or im.width * im.height > MAX_PIXELS:
                raise ValueError('Only bounded PNG/JPEG images are supported')
            return np.asarray(im.convert('RGB'), dtype=np.uint8).copy()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError('Invalid image encoding') from exc


def write_image(frame: np.ndarray, *, fmt: str = 'PNG') -> bytes:
    """Render *supplied* RGB pixels as PNG or JPEG bytes."""
    Image, _ = _pillow()
    validate_frame(frame)
    if fmt not in {'PNG', 'JPEG'}:
        raise ValueError('Image output format must be PNG or JPEG')
    out = io.BytesIO()
    Image.fromarray(frame, 'RGB').save(out, format=fmt)
    result = out.getvalue()
    if len(result) > MAX_BYTES:
        raise ValueError('Encoded image exceeds byte budget')
    return result


def _visual_features(frame: np.ndarray) -> dict[str, list[float]]:
    """Downsample independent half-fields; no object/meaning recognition.

    Left image hemifield goes to right visual cortex and vice versa.
    """
    Image, _ = _pillow()
    h, w, _ = validate_frame(frame).shape
    half = w // 2
    fields = {'R': frame[:, :half], 'L': frame[:, half:]}
    return {
        hemisphere: (np.asarray(Image.fromarray(array).resize((GRID, GRID), resample=Image.Resampling.BILINEAR),
                                dtype=np.float32).reshape(-1) / 255.0).tolist()
        for hemisphere, array in fields.items()
    }


@dataclass(frozen=True)
class VideoFrame:
    time_s: float
    pixels: np.ndarray


def read_video(path: Path, *, max_frames: int = MAX_VIDEO_FRAMES) -> tuple[VideoFrame, ...]:
    """Bounded MP4/AVI decoder; returns frames and timestamps, no audio decoding."""
    cv2 = _cv2()
    if not isinstance(path, Path) or path.suffix.lower() not in {'.mp4', '.avi'}:
        raise ValueError('Video input needs a .mp4 or .avi Path')
    if not path.is_file():
        raise ValueError('Video file does not exist')
    if not isinstance(max_frames, int) or isinstance(max_frames, bool) or not 1 <= max_frames <= MAX_VIDEO_FRAMES:
        raise ValueError('Invalid frame budget')
    if path.stat().st_size > MAX_BYTES:
        raise ValueError('Video file exceeds byte budget')
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        cap.release()
        raise ValueError('Cannot decode video')
    result = []
    try:
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        if not math.isfinite(fps) or fps <= 0:
            raise ValueError('Video FPS is missing or invalid')
        n = float(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if not math.isfinite(n) or n <= 0 or n > max_frames:
            raise ValueError('Video frame count exceeds budget or cannot be verified')
        width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if width < 2 or height < 1 or width * height > MAX_PIXELS or width * height * 3 * math.ceil(n) > MAX_VIDEO_RGB_BYTES:
            raise ValueError('Video frame dimensions or decoded memory exceed budget')
        for index in range(int(n)):
            ok, bgr = cap.read()
            if not ok or bgr is None:
                raise ValueError('Truncated video')
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            validate_frame(rgb)
            result.append(VideoFrame(index / fps, rgb.copy()))
        # Reject truncated metadata: do not silently ignore extra frames.
        if cap.read()[0]:
            raise ValueError('Video contains additional frames beyond declared frame count')
        if not result:
            raise ValueError('Empty video')
        return tuple(result)
    finally:
        cap.release()


def write_video(frames: Iterable[np.ndarray], path: Path, *, fps: float = 10.0) -> None:
    """Stream caller-supplied RGB frames to MP4, with a bounded total budget."""
    cv2 = _cv2()
    if not isinstance(path, Path) or path.suffix.lower() != '.mp4':
        raise ValueError('Video output must be an .mp4 Path')
    if not isinstance(fps, (int, float)) or isinstance(fps, bool) or not math.isfinite(fps) or not 0 < fps <= 60:
        raise ValueError('FPS must be finite in (0, 60]')
    it = iter(frames)
    try:
        first = validate_frame(next(it))
    except StopIteration as exc:
        raise ValueError('Video needs at least one frame') from exc
    h, w, _ = first.shape
    if h % 2 or w % 2:
        raise ValueError('MP4 output requires even width and height')
    if first.nbytes > MAX_VIDEO_RGB_BYTES:
        raise ValueError('Video exceeds decoded memory budget')
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*'mp4v'), float(fps), (w, h))
    if not writer.isOpened():
        writer.release()
        raise RuntimeError('MP4 encoder unavailable in this OpenCV build')
    try:
        writer.write(cv2.cvtColor(first, cv2.COLOR_RGB2BGR))
        frame_count = 1
        for frame in it:
            validate_frame(frame)
            if frame.shape != first.shape or frame_count >= MAX_VIDEO_FRAMES:
                raise ValueError('Video exceeds frame budget or has inconsistent dimensions')
            if (frame_count + 1) * first.nbytes > MAX_VIDEO_RGB_BYTES:
                raise ValueError('Video exceeds decoded memory budget')
            writer.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            frame_count += 1
    except BaseException:
        writer.release()
        path.unlink(missing_ok=True)
        raise
    finally:
        writer.release()
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        path.unlink(missing_ok=True)
        raise ValueError('Encoded video missing or exceeds byte budget')


def encode_text(text: str) -> tuple[list[float], ...]:
    """Reversible UTF-8 byte packets, fixed 32-byte chunks + length marker.

    There is no tokenizer, semantic model or learned linguistic understanding.
    """
    if not isinstance(text, str):
        raise TypeError('Text must be a Unicode string')
    data = text.encode('utf-8')
    if len(data) > MAX_TEXT_BYTES:
        raise ValueError('Text exceeds byte budget')
    if not data:
        return ()
    return tuple([byte / 255 for byte in data[i:i + TEXT_CHUNK]]
                 + [0.0] * (TEXT_CHUNK - len(data[i:i + TEXT_CHUNK]))
                 + [len(data[i:i + TEXT_CHUNK]) / TEXT_CHUNK]
                 for i in range(0, len(data), TEXT_CHUNK))


def decode_text(packets: Iterable[list[float]]) -> str:
    """Only reconstruct explicitly supplied text-byte packets, not generated language."""
    output = bytearray()
    for packet in packets:
        if len(packet) != TEXT_CHUNK + 1:
            raise ValueError('Invalid text packet width')
        length = round(packet[-1] * TEXT_CHUNK)
        if not 1 <= length <= TEXT_CHUNK or abs(packet[-1] * TEXT_CHUNK - length) > 1e-6:
            raise ValueError('Invalid text packet length')
        if any(not isinstance(value, (int, float)) or not math.isfinite(value) or abs(value) > 1e-8
               for value in packet[length:TEXT_CHUNK]):
            raise ValueError('Text packet contains nonzero padding')
        for value in packet[:length]:
            if not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError('Invalid text-byte encoding')
            byte = round(value * 255)
            if not 0 <= byte <= 255 or abs(value * 255 - byte) > 1e-5:
                raise ValueError('Text packet contains non-byte representation')
            output.append(byte)
        if len(output) > MAX_TEXT_BYTES:
            raise ValueError('Text exceeds byte budget')
    return output.decode('utf-8', errors='strict')


class MultimodalBridge:
    """Codec + anatomical input routing + explicit output rendering, untrained."""

    def __init__(self, sensorimotor: SensorimotorLoop | None = None):
        self.sensorimotor = sensorimotor if sensorimotor is not None else SensorimotorLoop()

    def image_input(self, source: bytes | Path | np.ndarray) -> tuple[SensoryPacket, ...]:
        frame = validate_frame(source) if isinstance(source, np.ndarray) else read_image(source)
        return self.sensorimotor.sensors.route({'vision_pixels': _visual_features(frame)})

    def video_input(self, path: Path) -> tuple[tuple[float, tuple[SensoryPacket, ...]], ...]:
        result = []
        previous = None
        for frame in read_video(path):
            visual = _visual_features(frame.pixels)
            # Distinct static and change features; reset at each clip boundary.
            motion = {side: [current - old for current, old in zip(visual[side], previous[side])]
                      if previous is not None else [0.0] * (GRID * GRID * 3)
                      for side in ('L', 'R')}
            sensory = self.sensorimotor.sensors.route({'vision_pixels': visual, 'visual_change': motion})
            result.append((frame.time_s, sensory))
            previous = visual
        return tuple(result)

    def text_input(self, text: str) -> tuple[SensoryPacket, ...]:
        # Software symbolic injection: not visual OCR nor brain-level reading.
        return tuple(self.sensorimotor.sensors.route({'text_symbols': {'L': packet}})[0]
                     for packet in encode_text(text))

    @staticmethod
    def text_output(text: str) -> bytes:
        if not isinstance(text, str) or len(text.encode('utf-8')) > MAX_TEXT_BYTES:
            raise ValueError('Text output must be bounded Unicode')
        return text.encode('utf-8')

    @staticmethod
    def image_output(pixels: np.ndarray) -> bytes:
        return write_image(pixels)

    @staticmethod
    def video_output(frames: Iterable[np.ndarray], path: Path, *, fps: float = 10.0) -> None:
        write_video(frames, path, fps=fps)


if __name__ == '__main__':
    bridge = MultimodalBridge()
    print('Unicode text input packets:', len(bridge.text_input('Hello سنڌي اردو')))
    print('Image input packets:', len(bridge.image_input(np.zeros((16, 16, 3), dtype=np.uint8))))
    print('Output formats: UTF-8 bytes, PNG bytes, MP4 file (caller supplies content)')
