import json
import os
from pathlib import Path
import tempfile

import pygame
import pytest
import tests.visual_scenes as visual_scenes

from meridian import Game
from meridian.localization import set_language


@pytest.fixture
def game():
    pygame.init()
    test_root = Path.cwd() / "tests" / ".tmp"
    test_root.mkdir(exist_ok=True)
    temp = tempfile.TemporaryDirectory(dir=test_root)
    path = Path(temp.name) / "desktop-volume.json"
    previous = os.environ.get("MERIDIAN_SAVE_PATH")
    os.environ["MERIDIAN_SAVE_PATH"] = str(path)
    instance = Game()
    instance.state = instance.DESKTOP
    instance.animation_level = "off"
    yield instance
    if previous is None:
        os.environ.pop("MERIDIAN_SAVE_PATH", None)
    else:
        os.environ["MERIDIAN_SAVE_PATH"] = previous
    temp.cleanup()


def click(game, rect):
    pos = rect.center
    game._handle_desktop_volume_event(
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": pos})
    )
    game._handle_desktop_volume_event(
        pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": pos})
    )


def open_panel(game):
    click(game, game._get_desktop_volume_tab_rect())
    game._update_desktop_volume_panel(0)


def drag_to(game, track, ratio):
    x = track.left + round(track.width * ratio)
    pos = (x, track.centery)
    game._handle_desktop_volume_event(
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": pos})
    )
    game._handle_desktop_volume_event(
        pygame.event.Event(pygame.MOUSEMOTION, {"pos": pos})
    )
    game._handle_desktop_volume_event(
        pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": pos})
    )


def test_three_desktop_sliders_update_correct_audio_values_and_persist(game):
    open_panel(game)
    rows = game._desktop_volume_rows()

    assert [row["key"] for row in rows] == ["master", "music", "sfx"]
    drag_to(game, rows[0]["track"], 0.25)
    drag_to(game, rows[1]["track"], 0.4)
    drag_to(game, rows[2]["track"], 0.7)

    assert game.audio.master_volume == pytest.approx(0.25, abs=0.02)
    assert game.audio.music_volume == pytest.approx(0.4, abs=0.02)
    assert game.audio.sfx_volume == pytest.approx(0.7, abs=0.02)
    assert game.master_volume == game.audio.master_volume
    with game.save_manager.path.open("r", encoding="utf-8") as handle:
        saved = json.load(handle)["settings"]
    assert saved["master_volume"] == game.audio.master_volume
    assert saved["music_volume"] == game.audio.music_volume
    assert saved["sfx_volume"] == game.audio.sfx_volume


def test_speaker_opens_and_right_side_left_arrow_starts_closing(game):
    open_panel(game)
    assert game.desktop_volume_state.phase == "open"
    assert game.desktop_volume_geometry.width_ratio == 1.0

    close_rect = game._get_desktop_volume_close_rect()
    click(game, close_rect)

    assert close_rect.centerx > game._get_desktop_volume_panel_rect().centerx
    assert game.desktop_volume_state.phase == "closing_content"
    assert game.desktop_volume_geometry.width_ratio == 1.0


def test_animation_geometry_controls_actual_hit_regions(game):
    game.animation_level = "full"
    click(game, game._get_desktop_volume_tab_rect())
    game._update_desktop_volume_panel(120)
    opening_panel = game._get_desktop_volume_panel_rect()
    opening_track = game._desktop_volume_rows()[0]["track"]
    before = game.audio.master_volume

    drag_to(game, opening_track, 0.1)

    assert game.audio.master_volume == before
    assert opening_panel.width == round(
        game._get_desktop_volume_panel_base_rect().width
        * game.desktop_volume_geometry.width_ratio
    )

    game._update_desktop_volume_panel(300)
    settled_track = game._desktop_volume_rows()[0]["track"]
    drag_to(game, settled_track, 0.1)
    assert game.audio.master_volume == pytest.approx(0.1, abs=0.02)


def test_page_change_and_close_cancel_drag(game):
    open_panel(game)
    track = game._desktop_volume_rows()[1]["track"]
    game._handle_desktop_volume_event(
        pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"button": 1, "pos": track.center},
        )
    )
    assert game.desktop_volume_state.drag_target == "music"

    game._start_desktop_page_slide(1)

    assert game.desktop_volume_state.drag_target is None
    assert game.desktop_volume_dragging is False

    game.desktop_slide_active = False
    game.desktop_page = 0
    open_panel(game)
    track = game._desktop_volume_rows()[2]["track"]
    game._handle_desktop_volume_event(
        pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"button": 1, "pos": track.center},
        )
    )
    click(game, game._get_desktop_volume_close_rect())
    assert game.desktop_volume_state.drag_target is None


def test_volume_row_labels_are_bilingual(game):
    set_language("en")
    assert [row["label"] for row in game._desktop_volume_rows()] == [
        "MASTER", "MUSIC", "SFX",
    ]

    set_language("zh_hans")
    assert [row["label"] for row in game._desktop_volume_rows()] == [
        "主音量", "音乐音量", "音效音量",
    ]


@pytest.mark.parametrize(
    ("keyframe", "phase"),
    [
        ("collapsed", "closed"),
        ("overshoot", "opening"),
        ("settled", "open"),
        ("closing", "closing_content"),
    ],
)
def test_visual_keyframes_inject_state_without_new_scenes(game, keyframe, phase):
    geometry = visual_scenes.inject_volume_panel_keyframe(game, keyframe)
    game._draw_desktop_volume_control()

    assert game.desktop_volume_state.phase == phase
    assert geometry is game.desktop_volume_geometry
    if keyframe == "overshoot":
        assert 1.0 < geometry.width_ratio <= 1.08


def test_overshoot_panel_stays_inside_desktop_safe_boundary(game):
    visual_scenes.inject_volume_panel_keyframe(game, "overshoot")
    panel = game._get_desktop_volume_panel_rect()

    assert panel.left >= game._get_desktop_volume_tab_rect().right
    assert panel.right <= 1280
    assert panel.bottom <= 720
