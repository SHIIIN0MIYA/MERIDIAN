import pygame
import pytest
from unittest.mock import patch

from meridian import Game
from meridian.common import C, WINDOW_H, WINDOW_W
from meridian.localization import set_language, translate
from meridian.persistence import default_data
from meridian.tank_battle import TankBattleMixin
from meridian.tank_engine import (
    EngineEvent,
    ItemType,
    MatchPhase,
    PickupState,
    PlayerCommand,
)


def keydown(key):
    return pygame.event.Event(pygame.KEYDOWN, {"key": key})


def keyup(key):
    return pygame.event.Event(pygame.KEYUP, {"key": key})


def press(game, *keys):
    for key in keys:
        game._handle_tank_playing_event(keydown(key))


def click(handler, position):
    attributes = {"button": 1, "pos": position}
    handler(pygame.event.Event(pygame.MOUSEBUTTONDOWN, attributes))
    handler(pygame.event.Event(pygame.MOUSEBUTTONUP, attributes))


class RecordingAudio:
    def __init__(self):
        self.names = []
        self.tank_phase = None
        self.scene_volume = None

    def play(self, name, *_args, **_kwargs):
        self.names.append(name)

    def set_tank_phase(self, phase):
        self.tank_phase = phase

    def set_scene_volume_scale(self, scale, fade_ms=0):
        self.scene_volume = (scale, fade_ms)


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
        ("brick_impact", "tank_brick"),
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
    game._tank_max_deficit = {"red": 3, "blue": 0}
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


def test_comeback_requires_three_point_deficit_and_survives_restore(game):
    recorded = []
    game._record_stat = lambda game_id, key, amount=1, mode="add": recorded.append(key)
    game.tank_engine.score = {"red": 0, "blue": 2}
    game._handle_tank_engine_events([EngineEvent("tank_destroyed", "red", {"attacker": "blue"})])
    game.tank_engine.score = {"red": 0, "blue": 3}
    game._handle_tank_engine_events([EngineEvent("tank_destroyed", "red", {"attacker": "blue"})])
    snapshot = game._capture_tank_run_state()

    restored = type(game)()
    restored.audio = RecordingAudio()
    restored._init_tank_battle()
    restored._record_stat = game._record_stat
    restored._restore_tank_run_state(snapshot)
    restored._handle_tank_engine_events([EngineEvent("match_ended", "red")])

    assert restored._tank_max_deficit == {"red": 3, "blue": 0}
    assert recorded.count("comeback_wins") == 1


def test_legacy_boolean_comeback_tracking_does_not_award_three_point_comeback(game):
    snapshot = game._capture_tank_run_state()
    snapshot["tracking"].pop("max_deficit", None)
    snapshot["tracking"]["was_behind"] = {"red": True, "blue": False}
    game._restore_tank_run_state(snapshot)
    recorded = []
    game._record_stat = lambda game_id, key, amount=1, mode="add": recorded.append(key)
    game._handle_tank_engine_events([EngineEvent("match_ended", "red")])
    assert "comeback_wins" not in recorded


def test_match_end_records_generic_completion_and_per_player_summary(game):
    recorded = []
    game._record_stat = lambda game_id, key, amount=1, mode="add": recorded.append(key)
    game._handle_tank_engine_events([
        EngineEvent("shot", "red"), EngineEvent("shot", "red"),
        EngineEvent("shot", "blue"), EngineEvent("tank_hit", "blue", {"attacker": "red"}),
        EngineEvent("item_used", "blue", {"item": "shield"}), EngineEvent("match_ended", "red"),
    ])
    assert recorded.count("games_completed") == 1
    assert game._tank_player_shots == {"red": 2, "blue": 1}
    assert game._tank_player_hits == {"red": 1, "blue": 0}
    assert game._tank_player_items_used == {"red": 0, "blue": 1}


def test_per_player_summary_survives_restore(game):
    game._tank_player_shots = {"red": 7, "blue": 5}
    game._tank_player_hits = {"red": 3, "blue": 2}
    game._tank_player_items_used = {"red": 1, "blue": 4}
    snapshot = game._capture_tank_run_state()
    game._reset_tank_tracking()
    game._restore_tank_run_state(snapshot)
    assert game._tank_player_shots == {"red": 7, "blue": 5}
    assert game._tank_player_hits == {"red": 3, "blue": 2}
    assert game._tank_player_items_used == {"red": 1, "blue": 4}


def test_end_page_draws_localized_winner_accuracy_and_item_counts(game):
    game.tank_engine.winner = "red"
    game._tank_player_shots = {"red": 4, "blue": 0}
    game._tank_player_hits = {"red": 3, "blue": 0}
    game._tank_player_items_used = {"red": 2, "blue": 1}
    with patch("meridian.tank_battle.render_pixel_text", wraps=__import__(
        "meridian.tank_battle", fromlist=["render_pixel_text"]
    ).render_pixel_text) as render:
        game._draw_tank_end()
    texts = [call.args[1] for call in render.call_args_list]
    assert "RED WINS" in texts
    assert any("RED" in text and "75%" in text and "2" in text for text in texts)
    assert any("BLUE" in text and "0%" in text and "1" in text for text in texts)


def test_end_page_is_fully_localized_in_chinese(game):
    set_language("zh_hans")
    game.tank_engine.winner = "red"
    game._tank_player_shots = {"red": 4, "blue": 2}
    game._tank_player_hits = {"red": 3, "blue": 1}
    game._tank_player_items_used = {"red": 2, "blue": 1}

    with patch("meridian.tank_battle.render_pixel_text", wraps=__import__(
        "meridian.tank_battle", fromlist=["render_pixel_text"]
    ).render_pixel_text) as render:
        game._draw_tank_end()

    texts = [call.args[1] for call in render.call_args_list]
    assert "红方胜利" in texts
    summaries = [text for text in texts if "%" in text]
    assert any("红方" in text and "命中率" in text and "使用道具" in text for text in summaries)
    assert any("蓝方" in text and "命中率" in text and "使用道具" in text for text in summaries)
    assert all("ACCURACY" not in text and "ITEMS USED" not in text for text in summaries)
    set_language("en")


def test_tank_statistics_labels_are_localized_before_drawing():
    pygame.init()
    set_language("zh_hans")
    game = Game.__new__(Game)
    game.save_data = default_data()
    game.mines_best_times = {}
    game.screen = pygame.Surface((WINDOW_W, WINDOW_H))
    game.font_status = pygame.font.Font(None, 18)
    game.font_small = pygame.font.Font(None, 14)
    game.profile_scroll = 0
    sections = game._profile_statistics_sections()
    game.profile_scroll = next(
        index for index, (title, _values) in enumerate(sections) if "坦克对决" in title
    )

    with patch("meridian.system.render_pixel_text", wraps=__import__(
        "meridian.system", fromlist=["render_pixel_text"]
    ).render_pixel_text) as render:
        game._draw_statistics_list()

    texts = [call.args[1] for call in render.call_args_list]
    english_labels = {"MATCHES", "WINS", "KILLS", "ACCURACY"}
    assert {translate(label) for label in english_labels} <= set(texts)
    assert not english_labels & set(texts)
    set_language("en")


def test_hud_uses_three_filled_or_empty_life_cells_per_player(game):
    game.tank_engine.tanks["red"].hp = 2
    game.tank_engine.tanks["blue"].hp = 1
    with patch("meridian.tank_battle.pygame.draw.rect", wraps=pygame.draw.rect) as draw_rect:
        game._draw_tank_hud()
    life_fills = [
        call.args[1] for call in draw_rect.call_args_list
        if len(call.args) == 3 and pygame.Rect(call.args[2]).size == (14, 14)
    ]
    assert life_fills.count(C.TANK_RED_LIGHT) == 2
    assert life_fills.count(C.TANK_BLUE_LIGHT) == 1
    assert life_fills.count(C.TANK_PANEL_DARK) == 3


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


@pytest.mark.parametrize(
    ("language", "expected", "forbidden"),
    [
        ("en", "RED 0  :  0 BLUE", ("红方", "蓝方")),
        ("zh_hans", "红方 0  :  0 蓝方", ("RED", "BLUE")),
    ],
)
def test_tank_end_score_uses_localized_team_labels(game, language, expected, forbidden):
    set_language(language)
    with patch("meridian.tank_battle.render_pixel_text", wraps=__import__(
        "meridian.tank_battle", fromlist=["render_pixel_text"]
    ).render_pixel_text) as render:
        game._draw_tank_end()

    rendered_text = [call.args[1] for call in render.call_args_list]
    assert expected in rendered_text
    score_text = next(text for text in rendered_text if " : " in text)
    assert all(label not in score_text for label in forbidden)
    set_language("en")


@pytest.mark.parametrize("state", ["menu", "controls", "playing", "end"])
def test_tank_pages_draw_without_error(game, state):
    getattr(game, f"_draw_tank_{state}")()


def test_tank_duel_desktop_to_rematch_acceptance_flow():
    game = Game()
    game.transition_active = False
    game.state = game.DESKTOP
    game.desktop_page = 1
    game._start_transition = lambda state, *_args, **_kwargs: setattr(game, "state", state)
    states = []

    tank_icon = next(
        button
        for button in game._get_desktop_icon_buttons()
        if button["action"] == "open_tank"
    )
    click(game._handle_desktop_event, tank_icon["rect"].center)
    states.append(game.state)

    start = next(
        button
        for button in game._tank_buttons("menu")
        if button["action"] == "start"
    )
    click(game._handle_tank_menu_event, start["rect"].center)
    states.append(game.state)

    red = game.tank_engine.tanks["red"]
    blue = game.tank_engine.tanks["blue"]
    starting_x = red.x
    starting_y = blue.y
    game._handle_tank_playing_event(keydown(pygame.K_d))
    game._handle_tank_playing_event(keydown(pygame.K_UP))
    game._update_tank_battle(32)
    assert red.x > starting_x
    assert blue.y < starting_y
    assert blue.facing_y == -1

    red.hp = 2
    game.tank_engine.pickup = PickupState(ItemType.REPAIR, red.x, red.y)
    game._handle_tank_playing_event(keydown(pygame.K_f))
    game._update_tank_battle(16)
    assert red.hp == 3
    assert red.held_item is None

    game.tank_engine.score = {"red": 1, "blue": 1}
    game.tank_engine.remaining_ms = 1
    game._update_tank_battle(16)
    assert game.tank_engine.phase is MatchPhase.SUDDEN_DEATH

    events = game.tank_engine._resolve_damage_batch([("blue", 3, "red", "bullet")])
    game._handle_tank_engine_events(events)
    game._update_tank_battle(0)
    states.append(game.state)

    rematch = next(
        button
        for button in game._tank_buttons("end")
        if button["action"] == "start"
    )
    click(game._handle_tank_end_event, rematch["rect"].center)
    states.append(game.state)

    assert states == [game.TANK_MENU, game.TANK_PLAYING, game.TANK_END, game.TANK_PLAYING]
