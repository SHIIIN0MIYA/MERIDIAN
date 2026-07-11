import pygame
import pytest
from unittest.mock import patch

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


def test_item_edges_during_pause_are_discarded_before_resume(game):
    recorded = []
    original_update = game.tank_engine.update

    def record_update(dt_ms, commands):
        recorded.append(commands["red"].use_item)
        return original_update(dt_ms, commands)

    game.tank_engine.update = record_update
    game.tank_paused = True
    game.tank_engine.paused = True
    game._handle_tank_playing_event(keydown(pygame.K_f))
    game._update_tank_battle()

    assert game._tank_item_pulses == {"red": False, "blue": False}

    game.tank_paused = False
    game.tank_engine.paused = False
    game._update_tank_battle()

    assert recorded == [False]
    assert game._tank_item_pulses == {"red": False, "blue": False}


def test_item_edge_reaches_exactly_one_normal_update(game):
    recorded = []
    original_update = game.tank_engine.update

    def record_update(dt_ms, commands):
        recorded.append(commands["red"].use_item)
        return original_update(dt_ms, commands)

    game.tank_engine.update = record_update
    game._handle_tank_playing_event(keydown(pygame.K_f))
    game._update_tank_battle()
    game._update_tank_battle()

    assert recorded == [True, False]
    assert game._tank_item_pulses == {"red": False, "blue": False}


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


def test_restore_accepts_legacy_raw_engine_snapshot(game):
    legacy = game.tank_engine.to_dict()
    legacy["score"]["red"] = 3

    game._restore_tank_run_state(legacy)

    assert game.tank_engine.score["red"] == 3
    assert game._tank_match_shots == 0
    assert game._tank_match_stats_recorded is False


def test_tracking_survives_restore_and_match_end_is_idempotent(game):
    recorded = []
    game._record_stat = lambda game_id, key, amount=1, mode="add": recorded.append((key, amount))
    game._tank_match_shots = 10
    game._tank_match_hits = 5
    game._tank_was_behind = {"red": True, "blue": False}
    game._tank_overdrive_kills = {"red": 1, "blue": 0}
    game._tank_in_sudden_death = True
    game.tank_engine.tanks["red"].speed_until_ms = 10_000
    snapshot = game._capture_tank_run_state()

    restored = type(game)()
    restored.audio = RecordingAudio()
    restored._init_tank_battle()
    restored._record_stat = game._record_stat
    restored._restore_tank_run_state(snapshot)
    restored._handle_tank_engine_events([
        EngineEvent("tank_destroyed", "blue", {"attacker": "red"}),
        EngineEvent("match_ended", "red"),
        EngineEvent("match_ended", "red"),
    ])

    keys = [key for key, _ in recorded]
    assert keys.count("overdrive_double_kills") == 1
    assert keys.count("accurate_matches") == 1
    assert keys.count("comeback_wins") == 1
    assert keys.count("sudden_wins") == 1
    assert keys.count("matches_completed") == 1


def test_only_shield_blocked_event_records_a_shield_block(game):
    recorded = []
    game._record_stat = lambda game_id, key, amount=1, mode="add": recorded.append(key)

    game._handle_tank_engine_events([
        EngineEvent("tank_hit", "red", {"attacker": "blue"}),
        EngineEvent("shield_blocked", "red", {"attacker": "blue", "source": "bullet"}),
    ])

    assert recorded.count("shield_blocks") == 1


def test_pending_snapshot_changes_menu_to_continue_and_new_match(game):
    game._pending_run_states = {"tank": game._capture_tank_run_state()}

    buttons = game._tank_buttons("menu")

    assert [(button["label"], button["action"]) for button in buttons[:2]] == [
        ("CONTINUE", "continue"),
        ("NEW MATCH", "start"),
    ]


def test_new_match_discards_pending_snapshot_and_resets_engine(game):
    snapshot = game._capture_tank_run_state()
    snapshot["engine"]["score"]["red"] = 4
    game._pending_run_states = {"tank": snapshot}

    game._start_tank_battle()

    assert "tank" not in game._pending_run_states
    assert game.tank_engine.score == {"red": 0, "blue": 0}


def test_tank_menu_draws_restore_failure_notice(game):
    game.tank_restore_notice = "TANK SAVE COULD NOT BE RESTORED"

    with patch("meridian.tank_battle.render_pixel_text", wraps=__import__(
        "meridian.tank_battle", fromlist=["render_pixel_text"]
    ).render_pixel_text) as render:
        game._draw_tank_menu()

    assert any(call.args[1] == game.tank_restore_notice for call in render.call_args_list)


@pytest.mark.parametrize("state", ["menu", "controls", "playing", "end"])
def test_tank_pages_draw_without_error(game, state):
    getattr(game, f"_draw_tank_{state}")()
