from pathlib import Path
import os


def test_suite_uses_disposable_save_path():
    save_path = Path(os.environ["MERIDIAN_SAVE_PATH"])
    assert save_path.name == "save.json"
    assert "MERIDIAN" not in {part.upper() for part in save_path.parts}
