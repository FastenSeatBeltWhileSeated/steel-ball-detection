"""Command-line entry point for desktop and headless processing."""

import argparse

import cv2

from .config import load_config
from .pipeline import DetectorConfig
from .video import process_video


def main(argv=None):
    parser = argparse.ArgumentParser(description="Interactive contour-based steel ball detection prototype")
    parser.add_argument("-i", "--input", default="0", help="Video path or camera index (default: 0)")
    parser.add_argument("--config", help="Detector configuration JSON")
    parser.add_argument("--headless", action="store_true", help="Process without desktop windows")
    parser.add_argument("-o", "--output", help="Annotated output AVI (MJPG; no audio)")
    parser.add_argument("--logo", help="Optional transparent PNG overlay")
    parser.add_argument("--save-config", help="Save final settings; press s during desktop processing")
    parser.add_argument("--delay-ms", type=int, default=1, help="Desktop keyboard polling delay")
    args = parser.parse_args(argv)
    if args.delay_ms < 1:
        parser.error("--delay-ms must be positive")
    source = int(args.input) if args.input.isdecimal() else args.input
    try:
        config = load_config(args.config) if args.config else DetectorConfig()
        count = process_video(source, config, headless=args.headless, output=args.output,
                              logo=args.logo, save_settings=args.save_config, delay_ms=args.delay_ms)
    except (ValueError, OSError, cv2.error) as error:
        parser.error(str(error))
    print(f"Processed {count} frames")
