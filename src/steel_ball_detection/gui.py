"""Desktop controls isolated from the reusable processing pipeline."""

from dataclasses import replace

import cv2


class Controls:
    window = "Configuration"
    sliders = (
        ("LH", 179), ("LS", 255), ("LV", 255),
        ("UH", 179), ("US", 255), ("UV", 255),
        ("Blur", 20), ("Canny low", 255), ("Canny high", 255),
        ("Aperture index", 2), ("Binary threshold", 255), ("Binary max", 255),
    )

    def __init__(self, config):
        self.base = config
        values = dict(zip(("LH", "LS", "LV"), config.hsv_lower))
        values.update(zip(("UH", "US", "UV"), config.hsv_upper))
        values.update({"Blur": config.blur_amount, "Canny low": config.canny_low,
                       "Canny high": config.canny_high,
                       "Aperture index": (3, 5, 7).index(config.aperture_size),
                       "Binary threshold": config.binary_threshold, "Binary max": config.binary_max})
        cv2.namedWindow(self.window, cv2.WINDOW_AUTOSIZE)
        for name, maximum in self.sliders:
            cv2.createTrackbar(name, self.window, values[name], maximum, lambda value: None)

    def read(self):
        values = {name: cv2.getTrackbarPos(name, self.window) for name, _ in self.sliders}
        # Normalize crossed sliders so each channel still has ordered bounds.
        lower = tuple(min(values[lo], values[hi]) for lo, hi in (("LH", "UH"), ("LS", "US"), ("LV", "UV")))
        upper = tuple(max(values[lo], values[hi]) for lo, hi in (("LH", "UH"), ("LS", "US"), ("LV", "UV")))
        return replace(self.base, hsv_lower=lower, hsv_upper=upper,
                       blur_amount=values["Blur"], canny_low=values["Canny low"],
                       canny_high=values["Canny high"],
                       aperture_size=(3, 5, 7)[values["Aperture index"]],
                       binary_threshold=values["Binary threshold"],
                       binary_max=values["Binary max"])

    @staticmethod
    def show(result):
        for name, image in (("HSV mask", result.masked), ("Blur", result.blurred),
                            ("Canny", result.edges), ("Threshold", result.thresholded),
                            ("Detections", result.annotated)):
            cv2.imshow(name, image)
