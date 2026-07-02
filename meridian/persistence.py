"""Versioned, crash-resistant persistence for MERIDIAN."""

from copy import deepcopy
from datetime import datetime
import json
import os
from pathlib import Path
import shutil


SCHEMA_VERSION = 4


def default_settings():
    return {
        "language": "en",
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


def default_records():
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


def default_statistics():
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
    }


def default_progress():
    return {
        "gomoku": {"run_active": False, "run_state": None},
        "snake": {"run_active": False, "run_state": None},
        "breakout": {"run_active": False, "run_state": None},
        "2048": {"run_active": False, "run_state": None},
        "mines": {"run_active": False, "run_state": None},
        "tetris": {"run_active": False, "run_state": None},
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


def default_lore():
    return {
        "prologues_seen": [],
        "unlocked_entries": [],
        "read_entries": [],
    }


def default_data():
    return {
        "schema_version": SCHEMA_VERSION,
        "settings": default_settings(),
        "records": default_records(),
        "statistics": default_statistics(),
        "achievements": {},
        "progress": default_progress(),
        "lore": default_lore(),
    }


def _deep_merge(default, incoming):
    if not isinstance(default, dict) or not isinstance(incoming, dict):
        return deepcopy(incoming)
    result = deepcopy(default)
    for key, value in incoming.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


class SaveManager:
    def __init__(self, path=None):
        if path is None:
            path = os.environ.get("MERIDIAN_SAVE_PATH")
        if path is None:
            root = Path(os.environ.get("APPDATA", Path.home()))
            path = root / "MERIDIAN" / "save.json"
        self.path = Path(path)
        self.backup_path = self.path.with_suffix(".json.bak")

    def migrate(self, data):
        version = int(data.get("schema_version", 0)) if isinstance(data, dict) else 0
        if version > SCHEMA_VERSION:
            return _deep_merge(default_data(), data)
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
        migrated = _deep_merge(default_data(), source)
        migrated["schema_version"] = SCHEMA_VERSION
        return migrated

    def _read(self, path):
        with path.open("r", encoding="utf-8") as handle:
            return self.migrate(json.load(handle))

    def load(self):
        if not self.path.exists():
            return default_data()
        try:
            return self._read(self.path)
        except (OSError, ValueError, TypeError):
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            corrupt = self.path.with_name(f"save.corrupt-{stamp}.json")
            try:
                self.path.replace(corrupt)
            except OSError:
                pass
            if self.backup_path.exists():
                try:
                    return self._read(self.backup_path)
                except (OSError, ValueError, TypeError):
                    pass
            return default_data()

    def save(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_suffix(".json.tmp")
        payload = self.migrate(data)
        with temp_path.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=True, sort_keys=True)
            handle.flush()
            os.fsync(handle.fileno())
        if self.path.exists():
            shutil.copy2(self.path, self.backup_path)
        os.replace(temp_path, self.path)

    def reset_settings(self, data):
        result = self.migrate(data)
        result["settings"] = default_settings()
        return result

    def erase_progress(self, data):
        result = self.migrate(data)
        result["records"] = default_records()
        result["statistics"] = default_statistics()
        result["achievements"] = {}
        result["progress"] = default_progress()
        return result
