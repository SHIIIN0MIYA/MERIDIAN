import os
from pathlib import Path

import pytest

import tools.update_visual_baselines as baseline_tool
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


def test_write_baselines_isolates_and_cleans_save_environment(tmp_path, monkeypatch):
    baseline_root = tmp_path / "baselines"
    user_save = tmp_path / "real-user-save.json"
    sentinel = b"do not replace the real user save"
    user_save.write_bytes(sentinel)
    monkeypatch.setenv("MERIDIAN_SAVE_PATH", str(user_save))
    isolated_paths = []
    real_render_scene = baseline_tool.render_scene

    def capture_isolated_path(scene, language):
        isolated_paths.append(Path(os.environ["MERIDIAN_SAVE_PATH"]))
        return real_render_scene(scene, language)

    monkeypatch.setattr(baseline_tool, "render_scene", capture_isolated_path)

    paths = write_baselines(baseline_root)

    assert len(paths) == 24
    assert os.environ["MERIDIAN_SAVE_PATH"] == str(user_save)
    assert user_save.read_bytes() == sentinel
    assert isolated_paths
    assert all(path != user_save for path in isolated_paths)
    assert len({path.parent for path in isolated_paths}) == 1
    assert not isolated_paths[0].parent.exists()


def test_write_baselines_restores_environment_and_cleans_temp_dir_on_error(
    tmp_path, monkeypatch
):
    original_save = tmp_path / "original-save.json"
    monkeypatch.setenv("MERIDIAN_SAVE_PATH", str(original_save))
    isolated_paths = []

    def fail_render(_scene, _language):
        isolated_paths.append(Path(os.environ["MERIDIAN_SAVE_PATH"]))
        raise RuntimeError("render failed")

    monkeypatch.setattr(baseline_tool, "render_scene", fail_render)

    with pytest.raises(RuntimeError, match="render failed"):
        write_baselines(tmp_path / "baselines")

    assert os.environ["MERIDIAN_SAVE_PATH"] == str(original_save)
    assert isolated_paths
    assert not isolated_paths[0].parent.exists()
