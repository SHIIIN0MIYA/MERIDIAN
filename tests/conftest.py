import atexit
import os
from pathlib import Path
import random

import pytest

_SAVE_PATH = Path(__file__).resolve().parents[1] / "save.json"


def _cleanup_save_file():
    for path in (
        _SAVE_PATH,
        _SAVE_PATH.with_suffix(".json.tmp"),
        _SAVE_PATH.with_suffix(".json.bak"),
    ):
        path.unlink(missing_ok=True)


atexit.register(_cleanup_save_file)
os.environ["MERIDIAN_SAVE_PATH"] = str(_SAVE_PATH)

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


@pytest.fixture(autouse=True)
def _freeze_visual_environment(monkeypatch):
    """Keep screenshot inputs stable without consulting the host clock."""
    from meridian.shell_desktop import DesktopMixin

    random.seed(330)
    monkeypatch.setattr(DesktopMixin, "_get_desktop_time_text", lambda self: "12:34")
    monkeypatch.setattr(DesktopMixin, "_get_battery_text", lambda self: "BAT 88%")
