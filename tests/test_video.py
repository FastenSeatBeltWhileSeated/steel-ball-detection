from unittest.mock import patch

import cv2
import numpy as np
import pytest

from steel_ball_detection.config import load_config
from steel_ball_detection.pipeline import DetectorConfig
from steel_ball_detection.video import process_video


@pytest.fixture
def input_video(tmp_path):
    path = tmp_path / "input.avi"
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 12, (160, 120))
    assert writer.isOpened()
    for _ in range(6):
        frame = np.zeros((120, 160, 3), dtype=np.uint8)
        cv2.circle(frame, (80, 60), 25, (255, 255, 255), -1)
        writer.write(frame)
    writer.release()
    return path


def test_headless_export_and_config_save(input_video, tmp_path):
    output, settings = tmp_path / "output.avi", tmp_path / "settings.json"
    config = DetectorConfig(width=160, height=120)
    with patch.object(cv2, "namedWindow") as window:
        assert process_video(input_video, config, headless=True, output=output, save_settings=settings) == 6
    window.assert_not_called()
    capture = cv2.VideoCapture(str(output))
    try:
        assert int(capture.get(cv2.CAP_PROP_FRAME_COUNT)) == 6
        assert capture.get(cv2.CAP_PROP_FPS) == pytest.approx(12)
        success, frame = capture.read()
        assert success and frame.shape == (120, 160, 3)
        # Yellow outline demonstrates that annotation reached the exported video.
        assert ((frame[:, :, 1] > 150) & (frame[:, :, 2] > 150) & (frame[:, :, 0] < 100)).any()
    finally:
        capture.release()
    assert load_config(settings).width == 160


def test_source_is_not_overwritten(input_video):
    with pytest.raises(ValueError, match="differ"):
        process_video(input_video, headless=True, output=input_video)


def test_invalid_input_rejected(tmp_path):
    with pytest.raises(ValueError, match="Cannot open"):
        process_video(tmp_path / "missing.avi", headless=True)


def test_output_extension_rejected(input_video, tmp_path):
    with pytest.raises(ValueError, match="extension"):
        process_video(input_video, headless=True, output=tmp_path / "wrong.mp4")


def test_odd_export_dimensions_rejected(input_video, tmp_path):
    with pytest.raises(ValueError, match="even"):
        process_video(input_video, DetectorConfig(width=161), headless=True, output=tmp_path / "out.avi")


def test_logo_export(input_video, tmp_path):
    logo, output = tmp_path / "logo.png", tmp_path / "output.avi"
    cv2.imwrite(str(logo), np.full((20,40,4), (240,0,0,255), dtype=np.uint8))
    assert process_video(input_video, headless=True, logo=logo, output=output) == 6
    capture = cv2.VideoCapture(str(output))
    try:
        success, frame = capture.read()
        assert success
        # The fixed-size logo occupies the upper-right area of the 720px frame.
        assert frame[40,600,0] > 200 and frame[40,600,2] < 30
    finally:
        capture.release()


def test_desktop_escape_releases_resources(input_video):
    factory = cv2.VideoCapture
    captures = []
    def open_capture(source):
        cap = factory(source)
        captures.append(cap)
        return cap
    positions = {}
    def create_slider(name, window, value, maximum, callback):
        positions[name] = value
    with patch.object(cv2, "VideoCapture", side_effect=open_capture), \
         patch.object(cv2, "namedWindow"), \
         patch.object(cv2, "createTrackbar", side_effect=create_slider), \
         patch.object(cv2, "getTrackbarPos", side_effect=lambda name, window: positions[name]), \
         patch.object(cv2, "imshow"), patch.object(cv2, "waitKey", return_value=27), \
         patch.object(cv2, "destroyAllWindows") as cleanup:
        assert process_video(input_video) == 1
    assert not captures[0].isOpened()
    cleanup.assert_called_once()
