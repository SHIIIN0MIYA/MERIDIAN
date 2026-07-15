"""Pure, backward-safe cross-world completion calculations."""

from __future__ import annotations

from dataclasses import dataclass
import math

from . import lore


WORLD_IDS = ("gomoku", "snake", "breakout", "2048", "mines", "tetris", "air", "tank")


@dataclass(frozen=True)
class WorldCompletion:
    achievement: int
    objectives: int
    lore: int
    total: int


def combine_completion(achievement, objectives, lore_percent) -> int:
    values = [max(0, min(100, int(value))) for value in (achievement, objectives, lore_percent)]
    return int(values[0] * .40 + values[1] * .35 + values[2] * .25)


def _mapping(value):
    return value if isinstance(value, dict) else {}


def _stat(data, game, key, default=0):
    statistics = _mapping(_mapping(data).get("statistics"))
    game_stats = _mapping(statistics.get(game))
    value = game_stats.get(key, default)
    if isinstance(default, dict):
        return _mapping(value)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return default
    return value


def _wins(data, game):
    if game == "gomoku":
        return _stat(data, game, "black_wins") + _stat(data, game, "white_wins")
    return _stat(data, game, "wins")


def _item_variety(data):
    return sum(_stat(data, "tank", f"{item}_uses") > 0 for item in
               ("repair", "shield", "speed", "mine", "emp", "piercing", "smoke", "warp"))


def _is_world_lore_condition(unlock) -> bool:
    """Only valid stat/achievement facts contribute to a world's denominator."""
    if not isinstance(unlock, str):
        return False
    if unlock.startswith("achievement:"):
        return bool(unlock.partition(":")[2])
    if not unlock.startswith("stat:"):
        return False
    parts = unlock.split(":")
    if len(parts) != 4 or not all(parts[1:3]):
        return False
    try:
        return math.isfinite(float(parts[3]))
    except (TypeError, ValueError):
        return False


def lore_condition_met(entry_or_unlock, save_data: dict, *, completion_percent=None) -> bool:
    """Return whether a Lore unlock condition is satisfied by saved facts.

    The evaluator is deliberately read-only and defensive: third-party or old
    saves may contain malformed values, and an unknown condition must never
    grant progress or prevent the archive from opening.
    """
    if isinstance(entry_or_unlock, dict):
        unlock = entry_or_unlock.get("unlock", "always")
    else:
        unlock = entry_or_unlock
    if not isinstance(unlock, str):
        return False
    if unlock == "always":
        return True

    if unlock.startswith("achievement:"):
        achievement_id = unlock.partition(":")[2]
        achievements = save_data.get("achievements", {}) if isinstance(save_data, dict) else {}
        if not isinstance(achievements, (dict, list, tuple, set)):
            return False
        return bool(achievement_id) and achievement_id in achievements

    if unlock.startswith("stat:"):
        parts = unlock.split(":")
        if len(parts) != 4:
            return False
        _, game_id, key, raw_threshold = parts
        try:
            threshold = float(raw_threshold)
        except (TypeError, ValueError):
            return False
        statistics = save_data.get("statistics", {}) if isinstance(save_data, dict) else {}
        if not isinstance(statistics, dict):
            return False
        game_stats = statistics.get(game_id, {})
        if not isinstance(game_stats, dict):
            return False
        try:
            if game_id == "gomoku" and key == "wins":
                value = float(game_stats.get("black_wins", 0)) + float(game_stats.get("white_wins", 0))
            else:
                value = game_stats.get(key, 0)
            return float(value) >= threshold
        except (AttributeError, KeyError, TypeError, ValueError, ZeroDivisionError):
            return False

    if unlock.startswith("completion:"):
        try:
            threshold = float(unlock.partition(":")[2])
            percent = global_completion(save_data) if completion_percent is None else completion_percent
            return float(percent) >= threshold
        except (AttributeError, KeyError, TypeError, ValueError, ZeroDivisionError):
            return False

    return False


OBJECTIVES = {
    "gomoku": (lambda d: _stat(d,"gomoku","games_completed") >= 1,
               lambda d: _stat(d,"gomoku","black_wins") >= 1,
               lambda d: _stat(d,"gomoku","white_wins") >= 1,
               lambda d: _wins(d,"gomoku") >= 10),
    "snake": (lambda d: _stat(d,"snake","best_score") >= 10,
              lambda d: _stat(d,"snake","best_score") >= 30,
              lambda d: _stat(d,"snake","food_eaten") >= 100),
    "breakout": (lambda d: _stat(d,"breakout","levels_cleared") >= 1,
                 lambda d: _stat(d,"breakout","levels_cleared") >= 5,
                 lambda d: _stat(d,"breakout","highest_level") >= 10,
                 lambda d: _stat(d,"breakout","hard_levels_cleared") >= 1),
    "2048": (lambda d: _stat(d,"2048","highest_tile") >= 512,
             lambda d: _stat(d,"2048","highest_tile") >= 1024,
             lambda d: _stat(d,"2048","highest_tile") >= 2048),
    "mines": (lambda d: _stat(d,"mines","wins") >= 1,
              lambda d: _stat(d,"mines","wins_by_mode",{}).get("9x10",0) >= 1,
              lambda d: _stat(d,"mines","wins_by_mode",{}).get("16x40",0) >= 1),
    "tetris": (lambda d: _stat(d,"tetris","highest_level") >= 5,
                lambda d: _stat(d,"tetris","highest_level") >= 10,
                lambda d: _stat(d,"tetris","lines_cleared") >= 100,
                lambda d: _stat(d,"tetris","tetrises") >= 10),
    "air": (lambda d: _stat(d,"air","campaigns_completed") >= 1,
            lambda d: _stat(d,"air","challenge_campaigns_completed") >= 1,
            lambda d: _stat(d,"air","boss_rush_clears") >= 1),
    "tank": (lambda d: _stat(d,"tank","matches_completed") >= 1,
             lambda d: _wins(d,"tank") >= 1,
             lambda d: _item_variety(d) >= 8,
             lambda d: _stat(d,"tank","sudden_wins") >= 1),
}


def world_completion(game_id: str, save_data: dict) -> WorldCompletion:
    source = _mapping(save_data)
    achievements = _mapping(source.get("achievements"))
    achievement_ids = [
        key for key in achievements
        if isinstance(key, str) and key.startswith(f"{game_id}_")
    ]
    # Fixed denominators keep deleted/unknown old fields from inflating progress.
    from .system import ACHIEVEMENTS
    definitions = [definition[0] for definition in ACHIEVEMENTS if definition[3] == game_id]
    achievement = int(len(set(achievement_ids) & set(definitions)) * 100 / max(1, len(definitions)))
    checks = OBJECTIVES[game_id]
    objectives = int(sum(bool(check(source)) for check in checks) * 100 / len(checks))
    world = lore.get_world(game_id)
    entries = [
        entry for entry in (world["lore_entries"] if world else [])
        if _is_world_lore_condition(entry.get("unlock"))
    ]
    lore_data = _mapping(source.get("lore"))
    raw_unlocked = lore_data.get("unlocked_entries", [])
    if not isinstance(raw_unlocked, (list, tuple, set)):
        raw_unlocked = []
    unlocked = {entry_id for entry_id in raw_unlocked if isinstance(entry_id, str)}
    lore_percent = int(sum(entry["id"] in unlocked for entry in entries) * 100 / max(1, len(entries)))
    return WorldCompletion(achievement, objectives, lore_percent,
                           combine_completion(achievement, objectives, lore_percent))


def global_completion(save_data: dict) -> int:
    return sum(world_completion(game, save_data).total for game in WORLD_IDS) // len(WORLD_IDS)


__all__ = [
    "OBJECTIVES", "WORLD_IDS", "WorldCompletion", "combine_completion",
    "global_completion", "lore_condition_met", "world_completion",
]
