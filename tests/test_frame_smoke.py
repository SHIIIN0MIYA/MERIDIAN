"""Headless frame-smoke coverage for every registered game state.

``Game`` drives its frame through three dispatch tables (``_EVENT_DISPATCH``,
``_UPDATE_DISPATCH``, ``_DRAW_DISPATCH`` in ``meridian/app.py``) — 46 states in
total.  This module walks *all* of them, runs a few ``update()`` + ``draw()``
frames each with the dummy SDL drivers, and fails with the offending state name
if any frame raises.

Why the entry functions matter
------------------------------
Assigning ``game.state = "air_playing"`` and drawing is **not** a valid smoke
test: ``_draw_air_raid`` reads ``self.air_player["x"]``, and only
``_begin_air_combat()`` creates that dict.  Assigning the state directly
produces ``KeyError: 'x'`` — a bug in the *test*, not in the product.  The same
holds for every arcade game: ``snake``/``breakout``/``2048``/``mines``/
``tetris``/``tank`` need their own ``_start_*_game()`` entry first, and gomoku's
``_start_new_game()`` deliberately does not switch state (the entry transition
does that at its midpoint), which is why ``_gomoku_playing`` below sets the
state itself, exactly like ``tests/_game_fixture.py:start_gomoku``.

So every state is split into one of two groups:

* **directly assignable** — shell/UI screens whose mixin ``_init_*`` already
  populated everything they draw (``boot``, ``desktop``, ``menu``, the arcade
  menus/settings pages, the profile/achievement/lore screens, ``shutdown``).
  ``setup`` is ``None`` for these.
* **entry-driven** — the state is reached by calling the game's own entry
  function, optionally followed by the production state transition into the
  "end" screen.  ``setup`` performs all of it and must leave
  ``game.state == <target>``; the per-state test asserts that before drawing,
  so a silently-broken entry cannot make the smoke test vacuously pass.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from meridian import Game
from meridian.common import pygame

REPO_ROOT = Path(__file__).resolve().parents[1]

# Frames per state: enough for one-shot intro effects (the air menu plays its
# prologue card on the first frame, then draws the menu) and a couple of
# animation ticks, without making the suite slow.
FRAMES = 4


# ── entry functions ─────────────────────────────────────────────────────────
# Each takes the live ``Game`` and leaves it in the state named by its key.

def _gomoku_playing(game: Game) -> None:
    """Gomoku's entry prepares the board but never switches state (R-11)."""
    game._start_new_game()
    game.state = game.PLAYING


def _gomoku_end(game: Game) -> None:
    """Reach the end page through the production transition, not by assignment."""
    game._start_new_game()
    game.board.winner = 1
    game.end_page_delay = 1
    game._update_delayed_end_page()  # the real END transition; sets game.state


def _snake_end(game: Game) -> None:
    """``_end_snake_game`` is the production death entry (it sets SNAKE_END)."""
    game._start_snake_game()
    game._end_snake_game()


def _breakout_end(game: Game) -> None:
    # No dedicated finish helper: BREAKOUT_END is set inline by the two loss
    # paths in `_update_breakout`.  The end screen reads only fields that
    # `_start_breakout_game` has already populated, so the state is assigned
    # after the real game entry.
    game._start_breakout_game()
    game.state = game.BREAKOUT_END


def _g2048_end(game: Game) -> None:
    # Same as breakout: the win/game-over transitions live inline in
    # `_apply_2048_move`, so the state is assigned after the real game entry.
    game._start_2048_game()
    game.state = game.G2048_END


def _mines_end(game: Game) -> None:
    """Reach the win screen through ``_check_mines_win``.

    The helper is what every reveal calls; it leaves MINES_END only once the
    revealed count reaches the board's non-mine total, so that count is seeded
    to the finishing value first.
    """
    game._start_mines_game()
    game.mines_revealed_count = game.mines_size * game.mines_size - game.mines_count
    game._check_mines_win()


def _tetris_end(game: Game) -> None:
    """``_finish_tetris_game`` is the production top-out entry."""
    game._start_tetris_game()
    game._finish_tetris_game()


def _tank_end(game: Game) -> None:
    # TANK_END is set inline when a match ends; no standalone helper exists.
    game._start_tank_battle()
    game.state = game.TANK_END


def _air_playing(game: Game) -> None:
    """Only ``_begin_air_combat`` creates ``air_player`` (with its ``x``/``y``)."""
    game._begin_air_combat()


def _air_end(game: Game) -> None:
    """Combat must exist before the end screen can draw the wrecked HUD."""
    game._begin_air_combat()
    game._finish_air(False)  # production entry; sets AIR_END itself


def _air_brief(game: Game) -> None:
    """``_prepare_air_level`` is what the campaign/level-select entries call."""
    game._prepare_air_level(0)  # sets AIR_BRIEF itself


def _air_story(game: Game) -> None:
    """A story screen always has a source; ``_draw_air_story`` parses it.

    Assigning the state alone leaves ``air_story_source == ""`` and the draw
    path raises ``ValueError`` on ``int("")`` — so use the archive entry.
    """
    game._open_air_story_archive()  # sets AIR_STORY itself


# state -> setup callable, or None when the state is safe to assign directly.
STATE_ENTRY = {
    # ── shell / UI, directly assignable ─────────────────────────────────────
    "boot": None,
    "system_ready": None,
    "password": None,
    "desktop": None,
    "menu": None,
    "settings": None,
    "system_settings": None,
    "profile": None,
    "achievement_wall": None,
    "lore_reader": None,
    "lore_story": None,
    "shutdown": None,
    # ── gomoku ──────────────────────────────────────────────────────────────
    "playing": _gomoku_playing,
    "end": _gomoku_end,
    # ── snake ───────────────────────────────────────────────────────────────
    "snake_menu": None,
    "snake_playing": lambda game: game._start_snake_game(),
    "snake_end": _snake_end,
    "snake_settings": None,
    # ── breakout ────────────────────────────────────────────────────────────
    "breakout_menu": None,
    "breakout_playing": lambda game: game._start_breakout_game(),
    "breakout_end": _breakout_end,
    "breakout_settings": None,
    # ── 2048 ────────────────────────────────────────────────────────────────
    "g2048_menu": None,
    "g2048_playing": lambda game: game._start_2048_game(),
    "g2048_end": _g2048_end,
    # ── minesweeper ─────────────────────────────────────────────────────────
    "mines_menu": None,
    "mines_playing": lambda game: game._start_mines_game(),
    "mines_end": _mines_end,
    "mines_settings": None,
    # ── tetris ──────────────────────────────────────────────────────────────
    "tetris_menu": None,
    "tetris_playing": lambda game: game._start_tetris_game(),
    "tetris_end": _tetris_end,
    # ── air raid ────────────────────────────────────────────────────────────
    "air_menu": None,
    "air_select": None,
    "air_controls": None,
    "air_brief": _air_brief,
    "air_archive": None,
    "air_supply": None,
    "air_playing": _air_playing,
    "air_end": _air_end,
    "air_skins": None,
    "air_story": _air_story,
    # ── tank battle ─────────────────────────────────────────────────────────
    "tank_menu": None,
    "tank_controls": None,
    "tank_playing": lambda game: game._start_tank_battle(),
    "tank_end": _tank_end,
}

# The three dispatch tables are documented as covering 46 states; keeping the
# count explicit means a newly registered state cannot slip past this module.
EXPECTED_STATE_COUNT = 46


@pytest.fixture
def game():
    """A fresh ``Game`` per state, torn down so the next one starts clean."""
    pygame.init()
    instance = Game()
    try:
        yield instance
    finally:
        instance.audio.stop()
        pygame.quit()


def _registered_states(instance: Game) -> set[str]:
    return (
        set(instance._EVENT_DISPATCH)
        | set(instance._UPDATE_DISPATCH)
        | set(instance._DRAW_DISPATCH)
    )


class SmokeCoverageTests:
    """The smoke map must stay in lockstep with the real dispatch tables."""

    def test_dispatch_tables_cover_exactly_the_smoke_map(self, game):
        states = _registered_states(game)
        missing = sorted(states - set(STATE_ENTRY))
        extra = sorted(set(STATE_ENTRY) - states)
        assert not missing, f"states with no smoke coverage: {missing}"
        assert not extra, f"smoke map names unregistered states: {extra}"

    def test_update_and_event_tables_only_name_renderable_states(self, game):
        # Every state must be drawable and event-reachable; the update table is
        # intentionally sparse (a state without update work simply falls
        # through to the shared animation tail), so it only needs to be a
        # subset of the renderable states.
        assert set(game._EVENT_DISPATCH) == set(game._DRAW_DISPATCH)
        assert set(game._UPDATE_DISPATCH) <= set(game._DRAW_DISPATCH)

    def test_state_count_is_the_documented_46(self, game):
        states = _registered_states(game)
        assert len(states) == EXPECTED_STATE_COUNT, sorted(states)


class SaveIsolationTests:
    """Regression guard for the repo-root save pollution (R5.1)."""

    def test_save_variables_point_into_this_tests_tmp_path(self, tmp_path):
        save_path = Path(os.environ["MERIDIAN_SAVE_PATH"])
        save_root = Path(os.environ["MERIDIAN_TEST_SAVE_ROOT"])
        assert save_path.is_relative_to(tmp_path), save_path
        assert save_root.is_relative_to(tmp_path), save_root
        assert not save_path.is_relative_to(REPO_ROOT), save_path


@pytest.mark.parametrize("state", sorted(STATE_ENTRY))
def test_state_renders_frames_headless(state, game):
    """update() + draw() must not raise for ``state`` across several frames."""
    setup = STATE_ENTRY[state]
    if setup is not None:
        setup(game)
        assert game.state == state, (
            f"entry for {state!r} left the game in {game.state!r}"
        )

    # Record every dispatch handler that actually runs, so a state that is
    # registered but never reached cannot make this test pass vacuously.
    dispatched: list[str] = []
    real_invoke = game._invoke_dispatch_handler

    def recording_invoke(handler, *args):
        dispatched.append(
            handler if isinstance(handler, str)
            else getattr(handler, "__name__", repr(handler))
        )
        return real_invoke(handler, *args)

    game._invoke_dispatch_handler = recording_invoke

    for _ in range(FRAMES):
        # Re-pin between calls: several handlers legitimately switch state (the
        # boot fade, `_update_delayed_end_page`, the air menu's first-frame
        # prologue card, `_finish_air`), and this test is about rendering
        # *this* state, not about its transitions.
        game.state = state
        game.update()
        game.state = state
        game.draw()

    draw_handler = game._DRAW_DISPATCH[state]
    assert draw_handler in dispatched, (
        f"{state!r} draw handler {draw_handler!r} never ran; dispatched={dispatched}"
    )
    update_entry = game._UPDATE_DISPATCH.get(state)
    for update_handler in update_entry[1] if update_entry else ():
        assert update_handler in dispatched, (
            f"{state!r} update handler {update_handler!r} never ran"
        )
