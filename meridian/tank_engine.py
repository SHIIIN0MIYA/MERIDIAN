"""Deterministic, rendering-independent logic for Tank Duel."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Mapping


ARENA_COLS = 24
ARENA_ROWS = 12


class Terrain(str, Enum):
    EMPTY = "."
    BRICK = "B"
    STEEL = "S"
    GRASS = "G"


class ItemType(str, Enum):
    REPAIR = "repair"
    SHIELD = "shield"
    SPEED = "speed"


@dataclass(frozen=True)
class PlayerCommand:
    move_x: int = 0
    move_y: int = 0
    use_item: bool = False


@dataclass
class TankState:
    player_id: str
    x: float
    y: float
    facing_x: int
    facing_y: int
    hp: int = 3

    @property
    def position(self) -> tuple[float, float]:
        return self.x, self.y


@dataclass(frozen=True)
class EngineEvent:
    kind: str
    player_id: str | None = None
    data: Mapping[str, object] = field(default_factory=dict)


@dataclass
class Arena:
    rows: list[str]

    def __post_init__(self) -> None:
        if len(self.rows) != ARENA_ROWS or any(
            len(row) != ARENA_COLS for row in self.rows
        ):
            raise ValueError(f"arena must be {ARENA_COLS}x{ARENA_ROWS}")

    def is_walkable(self, x: int | float, y: int | float) -> bool:
        tile_x = math.floor(x)
        tile_y = math.floor(y)
        if not (0 <= tile_x < ARENA_COLS and 0 <= tile_y < ARENA_ROWS):
            return False
        return self.rows[tile_y][tile_x] in {
            Terrain.EMPTY.value,
            Terrain.GRASS.value,
        }


_ARENA_ROWS = [
    "SSSSSSSSSSSSSSSSSSSSSSSS",
    "S......................S",
    "S....BB..........BB....S",
    "S......G........G......S",
    "S..S................S..S",
    "S..........BB..........S",
    "S..........SS..........S",
    "S..S................S..S",
    "S......G........G......S",
    "S....BB..........BB....S",
    "S......................S",
    "SSSSSSSSSSSSSSSSSSSSSSSS",
]


class TankBattleEngine:
    STEP_MS = 16
    MOVE_SPEED = 0.004
    TANK_HALF_SIZE = 0.35

    def __init__(self, seed: int = 0) -> None:
        self.seed = seed
        self.arena = Arena(list(_ARENA_ROWS))
        self.spawn_candidates = [(1, 1), (22, 10)]
        self.tanks = {
            "red": TankState("red", 1.5, 1.5, 1, 0),
            "blue": TankState("blue", 22.5, 10.5, -1, 0),
        }
        self._accumulator_ms = 0

    def update(
        self,
        dt_ms: int,
        commands: Mapping[str, PlayerCommand],
    ) -> list[EngineEvent]:
        self._accumulator_ms += max(0, dt_ms)
        events: list[EngineEvent] = []
        while self._accumulator_ms >= self.STEP_MS:
            events.extend(self._step(self.STEP_MS, commands))
            self._accumulator_ms -= self.STEP_MS
        return events

    def _step(
        self,
        dt_ms: int,
        commands: Mapping[str, PlayerCommand],
    ) -> list[EngineEvent]:
        self._move_tanks_simultaneously(dt_ms, commands)
        return []

    @staticmethod
    def _normalized_move(command: PlayerCommand) -> tuple[float, float]:
        length = math.hypot(command.move_x, command.move_y)
        if length == 0:
            return 0.0, 0.0
        return command.move_x / length, command.move_y / length

    def _move_tanks_simultaneously(
        self,
        dt_ms: int,
        commands: Mapping[str, PlayerCommand],
    ) -> None:
        candidates: dict[str, tuple[float, float]] = {}
        for player_id, tank in self.tanks.items():
            command = commands.get(player_id, PlayerCommand())
            move_x, move_y = self._normalized_move(command)
            if move_x or move_y:
                tank.facing_x = _direction(move_x)
                tank.facing_y = _direction(move_y)
            distance = self.MOVE_SPEED * dt_ms
            candidate = (tank.x + move_x * distance, tank.y + move_y * distance)
            candidates[player_id] = (
                candidate if self._position_is_walkable(candidate) else tank.position
            )

        rejected: set[str] = set()
        player_ids = tuple(self.tanks)
        for index, first_id in enumerate(player_ids):
            for second_id in player_ids[index + 1 :]:
                if self._tanks_overlap(candidates[first_id], candidates[second_id]):
                    rejected.update((first_id, second_id))

        for player_id, tank in self.tanks.items():
            if player_id not in rejected:
                tank.x, tank.y = candidates[player_id]

    def _position_is_walkable(self, position: tuple[float, float]) -> bool:
        x, y = position
        epsilon = 1e-9
        left = math.floor(x - self.TANK_HALF_SIZE)
        right = math.floor(x + self.TANK_HALF_SIZE - epsilon)
        top = math.floor(y - self.TANK_HALF_SIZE)
        bottom = math.floor(y + self.TANK_HALF_SIZE - epsilon)
        return all(
            self.arena.is_walkable(tile_x, tile_y)
            for tile_y in range(top, bottom + 1)
            for tile_x in range(left, right + 1)
        )

    def _tanks_overlap(
        self,
        first: tuple[float, float],
        second: tuple[float, float],
    ) -> bool:
        diameter = self.TANK_HALF_SIZE * 2
        return abs(first[0] - second[0]) < diameter and abs(first[1] - second[1]) < diameter


def _direction(component: float) -> int:
    if component > 0:
        return 1
    if component < 0:
        return -1
    return 0


__all__ = [
    "ARENA_COLS",
    "ARENA_ROWS",
    "Arena",
    "EngineEvent",
    "ItemType",
    "PlayerCommand",
    "TankBattleEngine",
    "TankState",
    "Terrain",
]
