"""Versioned, crash-resistant persistence for MERIDIAN."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
from typing import Any

SCHEMA_VERSION: int = 5

# The top-level containers a real profile always has, each of which must be a
# dict.  A file that parses as JSON but does not carry all of them is not a
# profile: it is a half-written / cloud-synced / hand-edited file that must be
# quarantined rather than merged into the defaults.  Merging it would report a
# brand-new profile to the player and then overwrite the good ``.bak``.
CORE_CONTAINERS: tuple[str, ...] = (
    "settings", "records", "statistics", "progress", "achievements", "lore",
)

# A profile is small (a few KB).  Anything far larger is rejected before
# parsing, so a deeply nested document cannot raise RecursionError out of
# ``load()`` and past the quarantine path.
MAX_SAVE_BYTES: int = 8 * 1024 * 1024


def default_settings() -> dict[str, Any]:
    return {
        "language": "en",
        "master_volume": 1.0,
        "music_volume": 0.55,
        "sfx_volume": 1.0,
        "muted": False,
        "fullscreen": False,
        "animation_level": "full",
        "screen_shake": True,
        "gomoku_board_size": 15,
        "snake_speed": "normal",
        "snake_skin": "green",
        "breakout_control": "keyboard",
        "breakout_difficulty": "normal",
        "breakout_ball_skin": "yellow",
        "breakout_brick_skin": "purple",
        "breakout_paddle_skin": "orange",
        "air_skin": "default",
        "mines_size": 9,
        "mines_count": 10,
    }


def default_records() -> dict[str, Any]:
    return {
        "gomoku": {"black_wins": 0, "white_wins": 0, "draws": 0},
        "snake": {"best_score": 0},
        "breakout": {"best_score": 0},
        "2048": {"best_score": 0},
        "mines": {"best_times": {}},
        "tetris": {"best_score": 0, "best_level": 1},
        "air": {
            "best_score": 0, "highest_level": 1,
            "boss_rush_score": 0, "boss_rush_health": 0,
        },
    }


def default_statistics() -> dict[str, Any]:
    base = {"play_time_ms": 0, "games_started": 0, "games_completed": 0}
    return {
        "global": {
            "launches": 0,
            "play_time_ms": 0,
            "games_started": 0,
            "games_completed": 0,
        },
        "gomoku": {
            **base, "black_wins": 0, "white_wins": 0, "draws": 0, "undos": 0,
            "wins_on_19": 0,
        },
        "snake": {
            **base, "deaths": 0, "food_eaten": 0, "best_score": 0,
            "best_fast_score": 0,
        },
        "breakout": {
            **base, "best_score": 0, "highest_level": 1, "bricks_broken": 0,
            "levels_cleared": 0, "lives_lost": 0, "hard_levels_cleared": 0,
            "perfect_levels": 0,
        },
        "2048": {
            **base, "moves": 0, "merges": 0, "wins": 0, "highest_tile": 0,
            "best_score": 0,
        },
        "mines": {
            **base, "wins": 0, "losses": 0, "cells_revealed": 0, "flags_placed": 0,
            "wins_by_mode": {},
        },
        "tetris": {
            **base, "best_score": 0, "highest_level": 1, "lines_cleared": 0,
            "tetrises": 0, "pieces_locked": 0, "best_lines": 0,
        },
        "air": {
            **base, "best_score": 0, "highest_level": 1, "levels_cleared": 0,
            "enemies_destroyed": 0, "bosses_encountered": 0, "bosses_defeated": 0,
            "powerups": 0, "deaths": 0, "damage_taken": 0, "repairs": 0,
            "grazes": 0, "cannon_level": 0, "spread_level": 0, "laser_level": 0,
            "best_missile_kills": 0, "s_ranks": 0, "campaigns_completed": 0,
            "challenge_clears": 0, "challenge_campaigns_completed": 0,
            "boss_rush_clears": 0,
        },
        "tank": {
            **base, "matches_completed": 0, "wins": 0,
            "red_wins": 0, "blue_wins": 0, "kills": 0,
            "hits": 0, "shots_fired": 0, "bricks_destroyed": 0,
            "items_picked_up": 0, "items_used": 0, "repair_uses": 0,
            "shield_uses": 0, "speed_uses": 0, "mine_uses": 0,
            "emp_uses": 0, "piercing_uses": 0, "smoke_uses": 0, "warp_uses": 0,
            "mine_hits": 0, "shield_blocks": 0, "overdrive_kills": 0,
            "sudden_death_wins": 0, "sudden_wins": 0,
            "largest_comeback": 0, "comeback_wins": 0,
            "accurate_matches": 0, "iron_will_kills": 0,
            "overdrive_double_kills": 0,
        },
    }


def default_progress() -> dict[str, Any]:
    return {
        "gomoku": {"run_active": False, "run_state": None},
        "snake": {"run_active": False, "run_state": None},
        "breakout": {"run_active": False, "run_state": None},
        "2048": {"run_active": False, "run_state": None},
        "mines": {"run_active": False, "run_state": None},
        "tetris": {"run_active": False, "run_state": None},
        "tank": {"run_active": False, "run_state": None},
        "air": {
            "unlocked": 1,
            "completed": 0,
            "skins_unlocked": ["default"],
            "prologue_seen": False,
            "stories_read": [],
            "challenge_unlocked": False,
            "campaign_complete": False,
            "challenge_complete": False,
            "boss_rush_complete": False,
            "archive_unlocked": 1,
            "ratings": {"standard": {}, "challenge": {}},
            "boss_rush_best": {"score": 0, "health": 0},
            "run_active": False,
            "run_mode": "standard",
            "run_level": 0,
            "run_loadout": {
                "cannon": 1, "spread": 0, "laser": 0, "active": "cannon",
            },
            "run_state": None,
        },
    }


def default_lore() -> dict[str, Any]:
    return {
        "prologues_seen": [],
        "unlocked_entries": [],
        "read_entries": [],
    }


def default_data() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "settings": default_settings(),
        "records": default_records(),
        "statistics": default_statistics(),
        "achievements": {},
        "progress": default_progress(),
        "lore": default_lore(),
    }


def _is_profile_shaped(data: object) -> bool:
    """True when ``data`` is a profile (possibly an old/partial one) rather than junk.

    Deliberately tolerant about *missing* containers: a v0 save may legitimately
    carry only some of them, and ``tests/test_persistence.py`` pins that a
    settings-only file still migrates (e.g. a language choice must survive).
    It is strict about *wrong types*: a container that is present but is not a
    dict is damage, and merging it would carry the bad shape into
    ``_apply_loaded_data`` and crash the game for good.

    An empty ``{}`` is rejected: real v0 saves always carried game containers,
    while ``{}`` is what a partial write or a sync conflict leaves behind.
    """
    if not isinstance(data, dict):
        return False
    if not data:
        return False
    return all(
        isinstance(value, dict)
        for key, value in data.items()
        if key in CORE_CONTAINERS
    )


def _deep_merge(default: dict, incoming: dict) -> dict:
    if not isinstance(default, dict) or not isinstance(incoming, dict):
        return deepcopy(incoming)
    result = deepcopy(default)
    for key, value in incoming.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        elif key in result and isinstance(result[key], dict):
            # A wrong-typed inbound value must not replace a trustworthy default
            # structure: keeping the default is what lets a damaged save start
            # the game instead of crashing in _apply_loaded_data (R-21).
            continue
        else:
            result[key] = deepcopy(value)
    return result


def _backfill_tank_statistics(data: dict) -> None:
    """Derive renamed Tank counters only when an old save lacks them."""
    statistics = data.get("statistics")
    if not isinstance(statistics, dict):
        return
    tank = statistics.get("tank")
    if not isinstance(tank, dict):
        return

    def count(key: str) -> int:
        value = tank.get(key, 0)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return 0
        return max(0, int(value))

    if "matches_completed" not in tank:
        tank["matches_completed"] = count("games_completed")
    if "wins" not in tank:
        tank["wins"] = count("red_wins") + count("blue_wins")
    if "sudden_wins" not in tank:
        tank["sudden_wins"] = count("sudden_death_wins")


class SaveManager:
    def __init__(self, path: Path | str | None = None) -> None:
        if path is None:
            path = os.environ.get("MERIDIAN_SAVE_PATH")
        if path is None:
            root = Path(os.environ.get("APPDATA", Path.home()))
            path = root / "MERIDIAN" / "save.json"
        self.path = Path(path)
        self.backup_path = self.path.with_suffix(".json.bak")
        # A second generation so one bad rotation cannot take the last good copy
        # with it.
        self.backup_path_2 = self.path.with_suffix(".json.bak2")

    def migrate(self, data: dict) -> dict[str, Any]:
        version = int(data.get("schema_version", 0)) if isinstance(data, dict) else 0
        if version > SCHEMA_VERSION:
            source = deepcopy(data)
            _backfill_tank_statistics(source)
            return _deep_merge(default_data(), source)
        source = deepcopy(data) if isinstance(data, dict) else {}
        if version < 3:
            source.setdefault("records", {})["air"] = default_records()["air"]
            source.setdefault("statistics", {})["air"] = default_statistics()["air"]
            source.setdefault("progress", {})["air"] = default_progress()["air"]
            achievements = source.setdefault("achievements", {})
            source["achievements"] = {
                key: value for key, value in achievements.items()
                if not key.startswith("air_")
            }
        if version < 4:
            for game_id in ("gomoku", "snake", "breakout", "2048", "mines", "tetris"):
                source.setdefault("progress", {}).setdefault(game_id, default_progress()[game_id])
            source.setdefault("progress", {}).setdefault("air", {})["run_state"] = None
        if version < 5:
            source.setdefault("statistics", {}).setdefault("tank", default_statistics()["tank"])
            source.setdefault("progress", {}).setdefault("tank", default_progress()["tank"])
        _backfill_tank_statistics(source)
        migrated = _deep_merge(default_data(), source)
        migrated["schema_version"] = SCHEMA_VERSION
        return migrated

    def _read(self, path: Path) -> dict[str, Any]:
        # Size guard first: a huge (e.g. deeply nested) document would raise
        # RecursionError out of json.load, which the quarantine path must still
        # catch, but refusing it up front keeps the failure cheap and clear.
        if path.stat().st_size > MAX_SAVE_BYTES:
            raise ValueError(f"save file is implausibly large: {path}")
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not _is_profile_shaped(data):
            raise ValueError("file is valid JSON but not a MERIDIAN profile")
        return self.migrate(data)

    def _quarantine(self, path: Path) -> None:
        """Move an unusable save aside so it is not read or overwritten again."""
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        try:
            path.replace(path.with_name(f"save.corrupt-{stamp}.json"))
        except OSError:
            pass

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return default_data()
        try:
            return self._read(self.path)
        except Exception:  # noqa: BLE001 - any failure here means "unusable save"
            # Widened deliberately: a shape-corrupt save raises AttributeError /
            # KeyError / ZeroDivisionError from migrate() or from the caller's
            # _apply_loaded_data(), and none of those may end the process.
            self._quarantine(self.path)

        # Only a file that still passes the full shape check is worth adopting.
        for candidate in (self.backup_path, self.backup_path_2):
            if not candidate.exists():
                continue
            try:
                return self._read(candidate)
            except Exception:  # noqa: BLE001
                self._quarantine(candidate)
        return default_data()

    def save(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_suffix(".json.tmp")
        payload = self.migrate(data)
        with temp_path.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=True, sort_keys=True)
            handle.flush()
            os.fsync(handle.fileno())
        # Rotate the backup only from a file that is itself a usable profile.
        # Rotating unconditionally is what let a junk primary destroy the last
        # good copy: the junk was copied over .bak moments before being written.
        if self.path.exists() and self._is_usable_file(self.path):
            if self.backup_path.exists():
                try:
                    shutil.copy2(self.backup_path, self.backup_path_2)
                except OSError:
                    pass
            shutil.copy2(self.path, self.backup_path)
        os.replace(temp_path, self.path)

    def _is_usable_file(self, path: Path) -> bool:
        """True when ``path`` is a readable, profile-shaped save."""
        try:
            if path.stat().st_size > MAX_SAVE_BYTES:
                return False
            with path.open("r", encoding="utf-8") as handle:
                return _is_profile_shaped(json.load(handle))
        except (OSError, ValueError, TypeError):
            return False

    def reset_settings(self, data: dict) -> dict[str, Any]:
        result = self.migrate(data)
        result["settings"] = default_settings()
        return result

    def erase_progress(self, data: dict) -> dict[str, Any]:
        result = self.migrate(data)
        result["records"] = default_records()
        result["statistics"] = default_statistics()
        result["achievements"] = {}
        result["progress"] = default_progress()
        result["lore"] = default_lore()
        return result
