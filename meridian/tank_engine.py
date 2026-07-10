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


@dataclass
class BulletState:
    owner: str
    x: float
    y: float
    dx: float
    dy: float

    @property
    def direction(self) -> tuple[float, float]:
        return self.dx, self.dy


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
    BULLET_SPEED = 0.006
    FIRE_INTERVAL_MS = 650
    MAX_BULLETS_PER_PLAYER = 2
    TANK_HALF_SIZE = 0.35
    BULLET_CLASH_DISTANCE = 0.2

    def __init__(self, seed: int = 0) -> None:
        self.seed = seed
        self.arena = Arena(list(_ARENA_ROWS))
        self.spawn_candidates = [(1, 1), (22, 10)]
        self.tanks = {
            "red": TankState("red", 1.5, 1.5, 1, 0),
            "blue": TankState("blue", 22.5, 10.5, -1, 0),
        }
        self.bullets: list[BulletState] = []
        self.score = {"red": 0, "blue": 0}
        self._fire_elapsed_ms = {"red": 0, "blue": 0}
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
        events = self._spawn_due_bullets(dt_ms)
        self._move_bullets(dt_ms)

        removed: set[int] = set()
        hits: list[tuple[str, int, str]] = []
        events.extend(self._collect_bullet_clashes(removed))
        events.extend(self._collect_bullet_impacts(removed, hits))
        self.bullets = [
            bullet for index, bullet in enumerate(self.bullets) if index not in removed
        ]
        events.extend(self._resolve_damage_batch(hits))
        return events

    def _spawn_due_bullets(self, dt_ms: int) -> list[EngineEvent]:
        events: list[EngineEvent] = []
        for player_id, tank in self.tanks.items():
            if tank.hp <= 0:
                continue
            self._fire_elapsed_ms[player_id] += dt_ms
            if self._fire_elapsed_ms[player_id] < self.FIRE_INTERVAL_MS:
                continue
            self._fire_elapsed_ms[player_id] -= self.FIRE_INTERVAL_MS
            owned = sum(bullet.owner == player_id for bullet in self.bullets)
            if owned >= self.MAX_BULLETS_PER_PLAYER:
                continue
            length = math.hypot(tank.facing_x, tank.facing_y)
            dx = tank.facing_x / length
            dy = tank.facing_y / length
            self.bullets.append(BulletState(player_id, tank.x, tank.y, dx, dy))
            events.append(EngineEvent("shot", player_id))
        return events

    def _move_bullets(self, dt_ms: int) -> None:
        distance = self.BULLET_SPEED * dt_ms
        for bullet in self.bullets:
            bullet.x += bullet.dx * distance
            bullet.y += bullet.dy * distance

    def _collect_bullet_clashes(self, removed: set[int]) -> list[EngineEvent]:
        events: list[EngineEvent] = []
        participants: set[int] = set()
        for first_index, first in enumerate(self.bullets):
            for second_index in range(first_index + 1, len(self.bullets)):
                second = self.bullets[second_index]
                if first.owner != second.owner and math.dist(
                    (first.x, first.y), (second.x, second.y)
                ) <= (
                    self.BULLET_CLASH_DISTANCE
                ):
                    participants.update((first_index, second_index))
                    events.append(EngineEvent("bullet_clash"))
        removed.update(participants)
        return events

    def _collect_bullet_impacts(
        self,
        removed: set[int],
        hits: list[tuple[str, int, str]],
    ) -> list[EngineEvent]:
        events: list[EngineEvent] = []
        bricks_hit: set[tuple[int, int]] = set()
        for index, bullet in enumerate(self.bullets):
            if index in removed:
                continue
            tile_x, tile_y = math.floor(bullet.x), math.floor(bullet.y)
            if not (0 <= tile_x < ARENA_COLS and 0 <= tile_y < ARENA_ROWS):
                removed.add(index)
                continue
            terrain = self.arena.rows[tile_y][tile_x]
            if terrain == Terrain.BRICK.value:
                bricks_hit.add((tile_x, tile_y))
                removed.add(index)
                events.append(EngineEvent("brick_hit", bullet.owner))
                continue
            if terrain == Terrain.STEEL.value:
                removed.add(index)
                continue
            for target, tank in self.tanks.items():
                if target == bullet.owner or tank.hp <= 0:
                    continue
                if (
                    abs(bullet.x - tank.x) <= self.TANK_HALF_SIZE
                    and abs(bullet.y - tank.y) <= self.TANK_HALF_SIZE
                ):
                    removed.add(index)
                    hits.append((target, 1, bullet.owner))
                    events.append(
                        EngineEvent("tank_hit", target, {"attacker": bullet.owner})
                    )
                    break
        for tile_x, tile_y in bricks_hit:
            self._replace_tile(tile_x, tile_y, Terrain.EMPTY.value)
        return events

    def _replace_tile(self, x: int, y: int, value: str) -> None:
        row = self.arena.rows[y]
        if isinstance(row, str):
            self.arena.rows[y] = row[:x] + value + row[x + 1 :]
        else:
            row[x] = value

    def _resolve_damage_batch(
        self, hits: list[tuple[str, int, str]]
    ) -> list[EngineEvent]:
        damage = {"red": 0, "blue": 0}
        attackers: dict[str, list[str]] = {"red": [], "blue": []}
        for target, amount, attacker in hits:
            damage[target] += amount
            attackers[target].append(attacker)

        events: list[EngineEvent] = []
        destroyed: list[str] = []
        for target in ("red", "blue"):
            if not damage[target]:
                continue
            tank = self.tanks[target]
            was_alive = tank.hp > 0
            tank.hp = max(0, tank.hp - damage[target])
            if was_alive and tank.hp == 0:
                destroyed.append(target)

        for target in destroyed:
            attacker = attackers[target][0]
            self.score[attacker] += 1
            events.append(
                EngineEvent("tank_destroyed", target, {"attacker": attacker})
            )
        return events

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
    "BulletState",
    "EngineEvent",
    "ItemType",
    "PlayerCommand",
    "TankBattleEngine",
    "TankState",
    "Terrain",
]
