"""Portable JSON configuration for repeatable processing."""

from dataclasses import asdict
import json
from pathlib import Path

from .pipeline import DetectorConfig


def load_config(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Configuration must be a JSON object")
        return DetectorConfig(**data)
    except (OSError, TypeError, ValueError) as error:
        raise ValueError(f"Cannot load configuration {path}: {error}") from error


def save_config(config, path):
    Path(path).write_text(json.dumps(asdict(config), indent=2) + "\n", encoding="utf-8")
