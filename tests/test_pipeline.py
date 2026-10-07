from dataclasses import replace

import cv2
import numpy as np
import pytest

from steel_ball_detection.config import load_config, save_config
from steel_ball_detection.pipeline import DetectorConfig, analyze_frame, measure_contour


def test_circular_candidate_detected_without_mutating_input():
    frame = np.zeros((120, 160, 3), dtype=np.uint8)
    cv2.circle(frame, (80, 60), 25, (255, 255, 255), -1)
    original = frame.copy()
    result = analyze_frame(frame, DetectorConfig(width=160, height=120))
    np.testing.assert_array_equal(frame, original)
    assert len(result.detections) == 1
    candidate = result.detections[0]
    assert abs(candidate.centroid[0] - 80) <= 1
    assert abs(candidate.centroid[1] - 60) <= 1
    assert 24 < candidate.radius < 27


def test_blank_frame_has_no_detections():
    result = analyze_frame(np.zeros((100, 100, 3), dtype=np.uint8))
    assert not result.detections
    assert result.annotated.shape == (480, 720, 3)


def test_degenerate_and_elongated_contours_are_rejected():
    config = DetectorConfig()
    degenerate = np.array([[[0, 0]], [[5, 0]]], dtype=np.int32)
    elongated = np.array([[[0, 0]], [[100, 0]], [[100, 5]], [[0, 5]]], dtype=np.int32)
    assert measure_contour(degenerate, config) is None
    assert measure_contour(elongated, config) is None


def test_hsv_mask_can_exclude_the_object():
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.circle(frame, (50, 50), 20, (255, 255, 255), -1)
    config = DetectorConfig(hsv_lower=(0, 200, 200), hsv_upper=(10, 255, 255))
    assert not analyze_frame(frame, config).detections


def test_grayscale_and_legacy_red_are_distinct():
    frame = np.full((30, 30, 3), (255, 0, 0), dtype=np.uint8)
    config = DetectorConfig(width=30, height=30)
    corrected = analyze_frame(frame, config)
    legacy = analyze_frame(frame, replace(config, grayscale_mode="legacy-red"))
    assert corrected.blurred.mean() > 0
    assert legacy.blurred.mean() == 0


@pytest.mark.parametrize("values", [
    {"width": 0}, {"blur_amount": -1}, {"aperture_size": 4},
    {"hsv_upper": (255, 255, 255)}, {"hsv_lower": (0, 0)}, {"hsv_lower": None},
    {"hsv_lower": (100, 0, 0), "hsv_upper": (50, 255, 255)},
    {"max_area_difference": float("nan")}, {"grayscale_mode": "unknown"},
])
def test_invalid_configuration_rejected(values):
    with pytest.raises(ValueError):
        DetectorConfig(**values)


def test_configuration_round_trip(tmp_path):
    config = DetectorConfig(blur_amount=2, max_area_difference=45, grayscale_mode="legacy-red")
    path = tmp_path / "settings.json"
    save_config(config, path)
    loaded = load_config(path)
    assert loaded.blur_amount == config.blur_amount
    assert tuple(loaded.hsv_upper) == config.hsv_upper
    assert loaded.max_area_difference == 45
    assert loaded.grayscale_mode == "legacy-red"
    assert loaded == config


@pytest.mark.parametrize("text", ["[]", "{", '{"unknown": 1}'])
def test_invalid_config_file_rejected(tmp_path, text):
    path = tmp_path / "invalid.json"
    path.write_text(text)
    with pytest.raises(ValueError):
        load_config(path)


def test_invalid_frame_rejected():
    with pytest.raises(ValueError):
        analyze_frame(np.zeros((20, 20), dtype=np.uint8))
