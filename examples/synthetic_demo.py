"""Generate a reproducible synthetic video and processing preview."""

from pathlib import Path

import cv2
import numpy as np

from steel_ball_detection.pipeline import DetectorConfig, analyze_frame


def main():
    root = Path(__file__).resolve().parents[1]
    generated = root / "examples" / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    assets = root / "docs" / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    video = generated / "synthetic-input.avi"
    writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*"MJPG"), 12, (320, 240))
    if not writer.isOpened():
        raise RuntimeError("Cannot create synthetic video")
    try:
        for index in range(36):
            frame = np.zeros((240, 320, 3), dtype=np.uint8)
            cv2.circle(frame, (75 + index, 110), 30, (220, 220, 220), -1)
            cv2.rectangle(frame, (180, 100), (300, 110), (220, 220, 220), -1)
            writer.write(frame)
    finally:
        writer.release()
    result = analyze_frame(frame, DetectorConfig(width=320, height=240))
    panels = []
    for label, image in (("Synthetic input", frame), ("HSV mask", result.masked),
                         ("Canny edges", result.edges), ("Candidate detection", result.annotated)):
        if image.ndim == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        panel = np.zeros((270, 320, 3), dtype=np.uint8)
        panel[30:] = image
        cv2.putText(panel, label, (10, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
        panels.append(panel)
    preview = np.vstack((np.hstack(panels[:2]), np.hstack(panels[2:])))
    if not cv2.imwrite(str(assets / "synthetic-pipeline.png"), preview):
        raise RuntimeError("Cannot create preview")
    print(f"Synthetic input: {video}")
    print(f"Preview: {assets / 'synthetic-pipeline.png'}")


if __name__ == "__main__":
    main()
