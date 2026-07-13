from pathlib import Path
import os


def test_suite_uses_unique_disposable_save_path():
    save_path = Path(os.environ["MERIDIAN_SAVE_PATH"])
    repository_root = Path(__file__).resolve().parents[1]

    assert save_path.name != "save.json"
    assert repository_root not in save_path.parents
    assert save_path.parent.name.startswith("meridian-tests-")


def test_visual_freezing_is_not_an_autouse_fixture(request):
    assert "_freeze_visual_environment" not in request.fixturenames
