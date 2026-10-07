"""Video processing with optional desktop controls and AVI export."""

from pathlib import Path

import cv2
import numpy as np

from .config import save_config
from .gui import Controls
from .pipeline import DetectorConfig, analyze_frame


def _load_logo(path):
    if path is None:
        return None
    image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if image is None or image.ndim != 3 or image.shape[2] != 4:
        raise ValueError("Logo must be a readable four-channel PNG")
    return cv2.resize(image, (201, 67))


def _add_logo(frame, logo):
    height, width = frame.shape[:2]
    x, y = width - logo.shape[1] - 20, 20
    if x < 0 or y + logo.shape[0] > height:
        raise ValueError("Processed frame is too small for the logo")
    region = frame[y:y + logo.shape[0], x:x + logo.shape[1]]
    alpha = logo[:, :, 3:4].astype(np.float32) / 255.0
    region[:] = np.rint(region * (1 - alpha) + logo[:, :, :3] * alpha).astype(np.uint8)


def process_video(source, config=None, *, headless=False, output=None, logo=None,
                  save_settings=None, delay_ms=1):
    config = config or DetectorConfig()
    if output:
        if Path(output).suffix.lower() != ".avi":
            raise ValueError("Output must use the .avi extension (MJPG codec)")
        if config.width % 2 or config.height % 2:
            raise ValueError("AVI export requires even width and height")
        if isinstance(source, (str, Path)) and Path(source).resolve() == Path(output).resolve():
            raise ValueError("Input and output paths must differ")
    overlay = _load_logo(logo)
    capture = cv2.VideoCapture(str(source) if isinstance(source, Path) else source)
    writer = None
    controls = None
    frame_count = 0
    try:
        if not capture.isOpened():
            raise ValueError(f"Cannot open video or camera: {source}")
        fps = capture.get(cv2.CAP_PROP_FPS)
        if not np.isfinite(fps) or fps <= 0:
            fps = 30.0
        if not headless:
            controls = Controls(config)
        while True:
            success, frame = capture.read()
            if not success:
                break
            if controls:
                config = controls.read()
            result = analyze_frame(frame, config)
            if overlay is not None:
                _add_logo(result.annotated, overlay)
            if output:
                if writer is None:
                    writer = cv2.VideoWriter(str(output), cv2.VideoWriter_fourcc(*"MJPG"),
                                             fps, (config.width, config.height))
                    if not writer.isOpened():
                        raise ValueError(f"Cannot write output: {output}")
                writer.write(result.annotated)
            frame_count += 1
            if controls:
                controls.show(result)
                key = cv2.waitKey(max(1, delay_ms)) & 0xFF
                if key == 27:
                    break
                if key == ord("s") and save_settings:
                    save_config(config, save_settings)
        if frame_count == 0:
            raise ValueError("Input contains no readable frames")
        if save_settings:
            save_config(config, save_settings)
        return frame_count
    finally:
        capture.release()
        if writer is not None:
            writer.release()
        if not headless:
            cv2.destroyAllWindows()
