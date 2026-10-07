# Maintenance and structure

The original root script `steel_balls_detection_v3.py` has been split into an installable package. Use `steel-ball-detect` or `python -m steel_ball_detection` after installation.

| Location | Responsibility |
| --- | --- |
| `src/steel_ball_detection/pipeline.py` | Image processing and geometry |
| `src/steel_ball_detection/config.py` | JSON load/save |
| `src/steel_ball_detection/gui.py` | Desktop sliders and windows |
| `src/steel_ball_detection/video.py` | Input, output and cleanup |
| `src/steel_ball_detection/cli.py` | Arguments and user-facing errors |
| `configs/` | Repeatable detector parameters |
| `examples/` | Runnable synthetic demonstration |
| `tests/` | Processing and video regression checks |
| `docs/assets/` | Historical screenshots and synthetic preview |

The old screenshots have descriptive names under `docs/assets/`. Their image bytes are unchanged. Original code and paths remain in Git history.

Installation metadata and dependencies now live in `pyproject.toml`; `requirements.txt` is no longer needed.
