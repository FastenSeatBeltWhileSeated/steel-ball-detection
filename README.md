# Steel Ball Detection

Interactive computer vision prototype for detecting candidate steel balls in video using Python and OpenCV.

This project explores **classical image processing and contour geometry**. It includes adjustable processing controls and screenshots from an earlier run.

## Recorded examples

![Detection prototype, recorded screenshot 1](Captura%20de%20pantalla%20de%202020-09-29%2017-02-50.png)

![Detection prototype, recorded screenshot 2](Captura%20de%20pantalla%20de%202020-09-29%2017-02-56.png)

These are historical screenshots included in the repository, rather than results from a newly benchmarked dataset.

## Processing pipeline

1. Resize each video frame to 720 × 480 pixels.
2. Apply an adjustable HSV color mask.
3. Extract the red channel of the masked BGR image as a single-channel processing input.
4. Apply erosion, dilation and optional Gaussian blur.
5. Detect edges with Canny and apply a binary threshold.
6. Extract external contours.
7. Compare contour area with the area of its minimum enclosing circle.
8. Draw accepted contours, enclosing circles, centroids and pixel measurements.

For contour area `A` and enclosing-circle radius `r`, the implemented criterion is:

```text
difference (%) = 100 × (πr² − A) / A
accept candidate when difference ≤ 100
```

This is a permissive geometric heuristic. It can accept objects other than steel balls and does not identify material.

## Installation

Use Python 3 in a desktop environment with OpenCV GUI support.

```bash
git clone https://github.com/FastenSeatBeltWhileSeated/Steel-ball-detection.git
cd Steel-ball-detection
python -m venv .venv
```

Activate the environment:

```bash
# Linux / macOS
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Then install the dependencies:

```bash
python -m pip install -r requirements.txt
```

## Usage

Process a video supplied by you:

```bash
python steel_balls_detection_v3.py --input /path/to/video.avi
```

Or use a camera:

```bash
python steel_balls_detection_v3.py --input 0
```

Optionally include a transparent PNG overlay:

```bash
python steel_balls_detection_v3.py --input /path/to/video.avi --logo /path/to/logo.png
```

The source video and original logo are **not included**. A logo is optional; provide a four-channel PNG when using `--logo`.

Tune the HSV, blur, Canny and threshold trackbars while inspecting the intermediate windows. OpenCV hue values normally span 0–179, although this historical interface exposes a wider slider range. Press **Escape** with an OpenCV window focused to exit.

## Repository contents

| File | Purpose |
| --- | --- |
| `steel_balls_detection_v3.py` | Interactive detection prototype |
| `requirements.txt` | Python runtime dependencies |
| Two PNG screenshots | Historical examples of the interface and detections |

## Scope and limitations

- Uses image processing and geometry; no trained ML model is included.
- Detection settings require manual adjustment for lighting, background and video conditions.
- The single-channel processing input is the masked red BGR channel, not HSV value or standard grayscale.
- Measurements are in resized-image pixels; there is no camera calibration or physical size conversion.
- No annotated dataset, precision/recall metrics, throughput benchmark or deployment validation is included.
- Requires a graphical desktop; the interactive interface cannot run directly in a headless environment.

The current maintenance update makes the input configurable, makes the logo optional, handles end-of-video and releases resources. It retains the original detection pipeline.

## Validation

The maintenance update was checked with a generated video and mocked window controls to exercise the processing loop, optional overlay and end-of-video cleanup. This checks execution behavior; it does not establish detection accuracy or validate the GUI on a physical desktop.

