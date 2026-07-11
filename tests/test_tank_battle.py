import pygame
import pytest

from meridian.common import WINDOW_H, WINDOW_W
from meridian.localization import set_language
from meridian.tank_battle import TankBattleMixin
from meridian.tank_engine import EngineEvent, PlayerCommand


def keydown(key):
    return pygame.event.Event(pygame.KEYDOWN, {"key": key})


def keyup(key):
    return pygame.event.Event(pygame.KEYUP, {"key": key})


def press(game, *keys):
    for key in keys:
        game._handle_tank_playing_event(keydown(key))


class RecordingAudio:
    def __init__(self):
        self.names = []

    def play(self, name, *_args, **_kwargs):
        self.names.append(name)


@pytest.fixture
def game():
    pygame.init()
    set_language("en")
    harness = type("TankHarness", (TankBattleMixin,), {})()
    harness.screen = pygame.Surface((WINDOW_W, WINDOW_H))
    harness.font_menu_title = pygame.font.Font(None, 32)
    harness.font_status = pygame.font.Font(None, 18)
    harness.font_btn = pygame.font.Font(None, 20)
    harness.font_small = pygame.font.Font(None, 14)
    harness.audio = RecordingAudio()
    harness.anim_tick = 0
    harness.state = "tank_menu"
    harness._logical_mouse_pos = lambda: (-1, -1)
    harness._go_desktop = lambda: None
    harness._start_transition = lambda state, *_args: setattr(harness, "state", state)
    harness._init_tank_battle()
    return harness


def test_red_opposite_keys_use_latest_then_fall_back(game):
    game._handle_tank_playing_event(keydown(pygame.K_a))
    game._handle_tank_playing_event(keydown(pygame.K_d))
    assert game._tank_command("red").move_x == 1
    game._handle_tank_playing_event(keyup(pygame.K_d))
    assert game._tank_command("red").move_x == -1


def test_red_and_blue_can_move_diagonally(game):
    press(game, pygame.K_w, pygame.K_d, pygame.K_UP, pygame.K_LEFT)
    assert game._tank_command("red") == PlayerCommand(1, -1)
    assert game._tank_command("blue") == PlayerCommand(-1, -1)


def test_each_players_item_key_is_a_single_frame_pulse(game):
    press(game, pygame.K_f, pygame.K_RETURN)
    assert game._tank_command("red").use_item is True
    assert game._tank_command("blue").use_item is True
    assert game._tank_command("red").use_item is False
    assert game._tank_command("blue").use_item is False


@pytest.mark.parametrize(
    ("kind", "sound"),
    [
        ("shot", "tank_shot"),
        ("bullet_clash", "tank_clash"),
        ("brick_hit", "tank_brick"),
        ("tank_hit", "tank_hit"),
        ("tank_destroyed", "tank_explosion"),
        ("pickup", "tank_pickup"),
        ("item_used", "tank_item"),
        ("sudden_death", "tank_alarm"),
    ],
)
def test_engine_events_use_fixed_sound_names(game, kind, sound):
    game._handle_tank_engine_events([EngineEvent(kind, "red")])
    assert game.audio.names == [sound]


def test_capture_and_restore_round_trip_uses_engine_snapshot(game):
    game.tank_engine.score["red"] = 4
    snapshot = game._capture_tank_run_state()
    game.tank_engine.score["red"] = 0
    game._restore_tank_run_state(snapshot)
    assert game.tank_engine.score["red"] == 4
    assert game._capture_tank_run_state() == snapshot


@pytest.mark.parametrize("state", ["menu", "controls", "playing", "end"])
def test_tank_pages_draw_without_error(game, state):
    getattr(game, f"_draw_tank_{state}")()
