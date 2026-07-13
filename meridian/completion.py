"""Pure, backward-safe cross-world completion calculations."""

from __future__ import annotations

from dataclasses import dataclass

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


def _stat(data, game, key, default=0):
    return data.get("statistics", {}).get(game, {}).get(key, default)


def _wins(data, game):
    if game == "gomoku":
        return _stat(data, game, "black_wins") + _stat(data, game, "white_wins")
    return _stat(data, game, "wins")


def _item_variety(data):
    stats = data.get("statistics", {}).get("tank", {})
    return sum(stats.get(f"{item}_uses", 0) > 0 for item in
               ("repair", "shield", "speed", "mine", "emp", "piercing", "smoke", "warp"))


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
    achievement_ids = [key for key in save_data.get("achievements", {}) if key.startswith(f"{game_id}_")]
    # Fixed denominators keep deleted/unknown old fields from inflating progress.
    from .system import ACHIEVEMENTS
    definitions = [definition[0] for definition in ACHIEVEMENTS if definition[3] == game_id]
    achievement = int(len(set(achievement_ids) & set(definitions)) * 100 / max(1, len(definitions)))
    checks = OBJECTIVES[game_id]
    objectives = int(sum(bool(check(save_data)) for check in checks) * 100 / len(checks))
    entries = [
        entry for entry in (lore.get_world(game_id)["lore_entries"] if lore.get_world(game_id) else [])
        if entry.get("unlock") != "always"
    ]
    unlocked = set(save_data.get("lore", {}).get("unlocked_entries", []))
    lore_percent = int(sum(entry["id"] in unlocked for entry in entries) * 100 / max(1, len(entries)))
    return WorldCompletion(achievement, objectives, lore_percent,
                           combine_completion(achievement, objectives, lore_percent))


def global_completion(save_data: dict) -> int:
    return sum(world_completion(game, save_data).total for game in WORLD_IDS) // len(WORLD_IDS)


__all__ = ["OBJECTIVES", "WORLD_IDS", "WorldCompletion", "combine_completion", "global_completion", "world_completion"]
