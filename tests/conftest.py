import atexit
import os
from pathlib import Path
import tempfile

_SAVE_DIR = tempfile.TemporaryDirectory(prefix="meridian-tests-")
atexit.register(_SAVE_DIR.cleanup)
os.environ["MERIDIAN_SAVE_PATH"] = str(Path(_SAVE_DIR.name) / "save.json")

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
