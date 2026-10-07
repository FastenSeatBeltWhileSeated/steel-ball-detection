"""Image processing independent of camera access and desktop windows."""

from dataclasses import dataclass
from math import isfinite, pi
from numbers import Integral

import cv2
import numpy as np


@dataclass(frozen=True)
class DetectorConfig:
    width: int = 720
    height: int = 480
    hsv_lower: tuple[int, int, int] = (0, 0, 0)
    hsv_upper: tuple[int, int, int] = (179, 255, 255)
    blur_amount: int = 0
    canny_low: int = 0
    canny_high: int = 255
    aperture_size: int = 3
    binary_threshold: int = 0
    binary_max: int = 255
    max_area_difference: float = 100.0
    min_area: float = 0.0
    grayscale_mode: str = "grayscale"

    def __post_init__(self):
        for name in ("hsv_lower", "hsv_upper"):
            values = getattr(self, name)
            if not isinstance(values, (tuple, list)) or len(values) != 3:
                raise ValueError("HSV bounds must contain three values")
            object.__setattr__(self, name, tuple(values))
        limits = {"width": (1, 8192), "height": (1, 8192),
                  "blur_amount": (0, 20), "canny_low": (0, 255),
                  "canny_high": (0, 255), "binary_threshold": (0, 255),
                  "binary_max": (0, 255)}
        for name, (low, high) in limits.items():
            value = getattr(self, name)
            if not isinstance(value, Integral) or not low <= value <= high:
                raise ValueError(f"{name} must be an integer from {low} to {high}")
        if self.aperture_size not in (3, 5, 7):
            raise ValueError("aperture_size must be 3, 5 or 7")
        for lower, upper, maximum in zip(self.hsv_lower, self.hsv_upper, (179, 255, 255)):
            if not isinstance(lower, Integral) or not isinstance(upper, Integral):
                raise ValueError("HSV bounds must contain integers")
            if not 0 <= lower <= upper <= maximum:
                raise ValueError("HSV lower bounds must not exceed upper bounds or channel limits")
        for name in ("max_area_difference", "min_area"):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or not isfinite(value) or value < 0:
                raise ValueError(f"{name} must be a finite nonnegative number")
        if self.grayscale_mode not in ("grayscale", "legacy-red"):
            raise ValueError("grayscale_mode must be grayscale or legacy-red")


@dataclass(frozen=True)
class Detection:
    centroid: tuple[int, int]
    circle_center: tuple[float, float]
    radius: float
    area: float
    circle_area: float
    area_difference: float


@dataclass
class FrameAnalysis:
    annotated: np.ndarray
    masked: np.ndarray
    blurred: np.ndarray
    edges: np.ndarray
    thresholded: np.ndarray
    detections: list[Detection]


def measure_contour(contour, config):
    """Return accepted geometry or None; this does not identify material."""
    area = cv2.contourArea(contour)
    moments = cv2.moments(contour)
    if area <= config.min_area or moments["m00"] == 0:
        return None
    (x, y), radius = cv2.minEnclosingCircle(contour)
    circle_area = pi * radius ** 2
    difference = (circle_area - area) * 100.0 / area
    if difference > config.max_area_difference:
        return None
    return Detection(
        centroid=(int(moments["m10"] / moments["m00"]),
                  int(moments["m01"] / moments["m00"])),
        circle_center=(x, y), radius=radius, area=area,
        circle_area=circle_area, area_difference=difference,
    )


def analyze_frame(frame, config=None):
    """Process a uint8 BGR frame without modifying the caller's array."""
    config = config or DetectorConfig()
    if (not isinstance(frame, np.ndarray) or frame.dtype != np.uint8
            or frame.ndim != 3 or frame.shape[2] != 3 or frame.size == 0):
        raise ValueError("frame must be a nonempty uint8 BGR image")
    resized = cv2.resize(frame, (config.width, config.height))
    hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array(config.hsv_lower, dtype=np.uint8),
                      np.array(config.hsv_upper, dtype=np.uint8))
    masked = cv2.bitwise_and(resized, resized, mask=mask)
    gray = (masked[:, :, 2].copy() if config.grayscale_mode == "legacy-red"
            else cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY))
    gray = cv2.dilate(cv2.erode(gray, None, iterations=1), None, iterations=1)
    kernel = 2 * config.blur_amount + 1
    blurred = cv2.GaussianBlur(gray, (kernel, kernel), 0) if kernel > 1 else gray.copy()
    edges = cv2.Canny(blurred, config.canny_low, config.canny_high,
                      apertureSize=config.aperture_size)
    _, thresholded = cv2.threshold(edges, config.binary_threshold,
                                   config.binary_max, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    annotated = resized.copy()
    detections = []
    for contour in contours:
        detection = measure_contour(contour, config)
        if detection is None:
            continue
        detections.append(detection)
        x, y = detection.circle_center
        cv2.drawContours(annotated, [contour], -1, (0, 255, 0), 2)
        cv2.circle(annotated, (round(x), round(y)), round(detection.radius), (0, 255, 255), 2)
        cv2.circle(annotated, detection.centroid, 4, (0, 0, 255), -1)
        label = f"r={detection.radius:.1f}px A={detection.area:.0f}px2 d={detection.area_difference:.1f}%"
        c_x, c_y = detection.centroid
        cv2.putText(annotated, label, (max(0, c_x - 20), max(15, c_y - 25)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    return FrameAnalysis(annotated, masked, blurred, edges, thresholded, detections)
