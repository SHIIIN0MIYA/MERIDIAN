import os

from tools.update_visual_baselines import main, write_baselines
from tests.visual_scenes import SCENE_NAMES


def test_update_tool_writes_exactly_twenty_four_pngs(tmp_path):
    paths = write_baselines(tmp_path)

    expected = {
        tmp_path / language / f"{scene}.png"
        for language in ("en", "zh_hans")
        for scene in SCENE_NAMES
    }
    assert len(paths) == 24
    assert set(paths) == expected
    assert all(path.is_file() for path in paths)
    assert all(path.suffix == ".png" for path in paths)


def test_cli_prints_target_and_refuses_without_explicit_yes(tmp_path, capsys):
    baseline_root = tmp_path / "baselines"

    exit_code = main([], baseline_root=baseline_root)

    assert exit_code == 2
    assert str(baseline_root.resolve()) in capsys.readouterr().out
    assert not baseline_root.exists()


def test_cli_writes_baselines_with_explicit_yes(tmp_path, capsys):
    baseline_root = tmp_path / "baselines"

    exit_code = main(["--yes"], baseline_root=baseline_root)

    assert exit_code == 0
    assert len(list(baseline_root.rglob("*.png"))) == 24
    assert str(baseline_root.resolve()) in capsys.readouterr().out


def test_cli_isolates_visual_rendering_from_the_user_save(tmp_path, monkeypatch):
    baseline_root = tmp_path / "baselines"
    unusable_appdata = tmp_path / "not-a-directory"
    unusable_appdata.write_text("block user-save fallback", encoding="utf-8")
    monkeypatch.delenv("MERIDIAN_SAVE_PATH", raising=False)
    monkeypatch.setenv("APPDATA", str(unusable_appdata))

    exit_code = main(["--yes"], baseline_root=baseline_root)

    assert exit_code == 0
    assert "MERIDIAN_SAVE_PATH" not in os.environ
    assert len(list(baseline_root.rglob("*.png"))) == 24
