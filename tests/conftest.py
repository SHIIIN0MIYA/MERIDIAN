import atexit
import os
from pathlib import Path
import shutil
import tempfile
import uuid

_SAVE_DIRECTORY = Path(tempfile.mkdtemp(prefix="meridian-tests-"))
_SAVE_PATH = _SAVE_DIRECTORY / f"test-state-{uuid.uuid4().hex}.json"


def _cleanup_save_directory():
    shutil.rmtree(_SAVE_DIRECTORY, ignore_errors=True)


atexit.register(_cleanup_save_directory)
os.environ["MERIDIAN_SAVE_PATH"] = str(_SAVE_PATH)

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
