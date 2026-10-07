# Detection method and limitations

The pipeline resizes each frame, applies HSV masking, converts to grayscale, performs erosion/dilation and optional Gaussian blur, then uses Canny edges, a binary threshold and external contours.

For each nondegenerate contour:

```text
A = contour area
r = minimum enclosing circle radius
difference (%) = 100 × (πr² − A) / A
accept if A > min_area and difference ≤ max_area_difference
```

The default difference limit is 100%, inherited from the original prototype. This is a permissive geometry heuristic: it can accept noncircular objects and does not identify steel or other materials. Lowering the limit makes the geometry check stricter, without establishing recognition accuracy.

Annotations show the accepted contour, minimum enclosing circle, centroid, radius, area and area difference. Measurements use resized-image pixels, not physical units. The fixed width and height can change the input aspect ratio.

## Changes from the historical script

- The original variable called grayscale actually extracted the red channel of a masked BGR image. The default now uses a real BGR-to-grayscale conversion.
- Set `grayscale_mode` to `"legacy-red"` in JSON to reproduce that earlier preprocessing choice.
- HSV hue bounds now use OpenCV's 0–179 range.
- Unused shape classification, queues, variables and the imutils dependency were removed.
- Parameters are explicit configuration instead of global variables.
- Processing can run without a desktop or camera.

The historical screenshots precede these changes and are retained as prior examples, not output from the new default settings.

## Evidence and validation

The repository has historical screenshots and a reproducible synthetic example. Tests check contour filtering, color masking, preprocessing behavior, configuration, annotated video export and resource cleanup.

No annotated industrial dataset, precision/recall measurements, physical calibration or production deployment validation is included.
