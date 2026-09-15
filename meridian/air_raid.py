"""AIR RAID: a procedural retro-future bullet-hell campaign."""

import copy

from .common import *
from .arcade_common import *
from .arcade_levels import (
    AIR_ARCHIVE, AIR_CHAPTER_STORIES, AIR_ENEMY_TYPES,
    AIR_LEVELS, AIR_PROLOGUE, AIR_STANDARD_LOADOUTS,
)


AIR_PALETTE = {
    "bg": C.AIR_BG, "panel": C.AIR_PANEL, "panel_dark": C.AIR_PANEL_DARK,
    "accent": C.AIR_ACCENT, "accent_light": C.AIR_ACCENT_LIGHT,
    "text": C.AIR_TEXT, "muted": C.AIR_MUTED, "hover": C.AIR_HOVER,
}
# The "challenge unlocked" announcement is a one-shot: it fades on its own
# instead of reappearing on every later end screen (R-07).
AIR_UNLOCK_NOTICE_FRAMES = 300

AIR_WEAPON_COLORS = {
    "cannon": C.AIR_CANNON, "spread": C.AIR_SPREAD, "laser": C.AIR_LASER,
}
AIR_ENEMY_COLORS = {
    "scout": C.AIR_ENEMY_SCOUT, "striker": C.AIR_ENEMY_STRIKER,
    "bomber": C.AIR_ENEMY_BOMBER, "sniper": C.AIR_ENEMY_SNIPER,
    "layer": C.AIR_ENEMY_LAYER, "shield": C.AIR_ENEMY_SHIELD,
    "carrier": C.AIR_ENEMY_CARRIER, "commander": C.AIR_ENEMY_COMMANDER,
}
AIR_RANK_ORDER = {"C": 0, "B": 1, "A": 2, "S": 3}
AIR_PLAY_RECT = pygame.Rect(330, 42, 620, 636)


class AirRaidMixin:
    def _init_air_raid(self):
        self.air_level = 0
        self.air_select_page = 0
        self.air_pressed = None
        self.air_menu_index = 0
        self.air_mode = "standard"
        self.air_campaign_active = False
        self.air_challenge_unlocked_notice = False
        self.air_unlock_notice_frames = 0
        self.air_paused = False
        self.air_result = ""
        self.air_rank = "C"
        self.air_preview_tick = 0
        self.air_archive_index = 0
        self.air_brief_page = 0
        self.air_player = {}
        self.air_enemies = []
        self.air_bullets = []
        self.air_enemy_bullets = []
        self.air_powerups = []
        self.air_particles = []
        self.air_missiles = []
        self.air_warnings = []
        self.air_wave = 0
        self.air_spawn_tick = 0
        self.air_stage_tick = 0
        self.air_score = 0
        self.air_health = 5
        self.air_hits = 0
        self.air_threat = 1.0
        self.air_combo = 0
        self.air_combo_timer = 0
        self.air_multiplier = 1.0
        self.air_grazes = 0
        self.air_destroyed = 0
        self.air_spawned = 0
        self.air_mission_value = 0
        self.air_mission_target = 1
        self.air_missile_charge = 0
        self.air_missile_ready = False
        self.air_best_missile_kills = 0
        self.air_bullet_serial = 0
        self.air_loadout = {"cannon": 1, "spread": 0, "laser": 0, "active": "cannon"}
        self.air_entry_snapshot = None
        self.air_boss_phase = 1
        self.air_boss_phase_flash = 0
        self.air_boss_rush_index = 0
        self.air_boss_rush_health = 5
        self.air_run_score = 0
        self.air_supply_index = 0
        self.air_supply_next_level = 1
        self.air_demo_scene = 0
        self.air_demo_scene_tick = 0
        self.air_story_message = None
        self.air_story_timer = 0
        self.air_ship_color = C.AIR_SKIN_DEFAULT_SHIP
        self.air_engine_color = C.AIR_SKIN_DEFAULT_ENGINE
        self.air_shield_color = C.AIR_SKIN_DEFAULT_SHIELD
        self.air_stage_rng = random.Random(0)
        self.air_story_lines = []
        self.air_story_page = 0
        self.air_story_source = ""
        # Level to launch once the chapter story currently on screen is done.
        self._pending_brief_level = None

    def _air_progress(self):
        return self.save_data["progress"]["air"]

    def _check_air_prologue(self):
        if getattr(self, "dev_mode", False):
            return False
        progress = self._air_progress()
        if not progress.get("prologue_seen", False):
            self.air_story_lines = list(AIR_PROLOGUE)
            self.air_story_page = 0
            self.air_story_source = "prologue"
            progress["prologue_seen"] = True
            # Sync with MERIDIAN lore
            lore_data = self.save_data.setdefault("lore", {})
            seen = lore_data.setdefault("prologues_seen", [])
            if "air" not in seen:
                seen.append("air")
            self._save_now()
            self.state = self.AIR_STORY
            return True
        return False

    def _check_air_chapter_story(self, chapter_index, level):
        """Show the chapter intro if unseen; ``level`` is the level to resume.

        The caller derived ``chapter_index`` from ``level``, but the two are not
        interchangeable: chapter N spans levels 2(N-1) and 2(N-1)+1, so parking
        the chapter index made the story resume at the wrong level (R-06).
        """
        if not getattr(self, "air_campaign_active", False):
            return False
        chapter_num = chapter_index + 1
        progress = self._air_progress()
        stories_read = progress.get("stories_read", [])
        if chapter_num not in stories_read and chapter_num in AIR_CHAPTER_STORIES:
            self.air_story_lines = list(AIR_CHAPTER_STORIES[chapter_num])
            self.air_story_page = 0
            self.air_story_source = f"chapter_{chapter_num}"
            stories_read.append(chapter_num)
            progress["stories_read"] = stories_read
            self._save_now()
            self.state = self.AIR_STORY
            self._pending_brief_level = level
            return True
        return False

    def _open_air_story_archive(self):
        self.air_story_lines = ["STORY ARCHIVE", "Select a chapter to read."]
        self.air_story_page = 0
        self.air_story_source = "archive_index"
        self._pending_brief_level = None
        self.state = self.AIR_STORY

    def _air_menu_items(self):
        progress = self._air_progress()
        items = [
            ("NEW CAMPAIGN", "new_campaign", True),
            ("CONTINUE", "continue", progress.get("run_active", False)),
            ("LEVEL SELECT", "select", True),
            ("CHALLENGE", "challenge", progress.get("challenge_unlocked", False)),
            ("BOSS RUSH", "boss_rush", progress.get("challenge_unlocked", False)),
            ("CAMPAIGN ARCHIVE", "archive", True),
            ("CONTROLS", "controls", True),
            ("SKINS", "skins", True),
            ("STORY ARCHIVE", "story_archive", True),
            ("DESKTOP", "desktop", True),
        ]
        return items

    def _air_menu_buttons(self):
        buttons = []
        for index, (label, action, enabled) in enumerate(self._air_menu_items()):
            col, row = index % 2, index // 2
            buttons.append({
                "rect": pygame.Rect(365 + col * 285, 350 + row * 62, 260, 44),
                "label": label if enabled else f"{label} / LOCKED",
                "action": action, "enabled": enabled,
            })
        return buttons

    def _air_end_buttons(self):
        labels = (
            [("CONTINUE", "continue"), ("MENU", "menu"), ("DESKTOP", "desktop")]
            if self.air_result in ("MISSION CLEAR", "BOSS RUSH CLEAR")
            else [("RETRY", "retry"), ("MENU", "menu"), ("DESKTOP", "desktop")]
        )
        btn_w, btn_h, gap = 240, 44, 22
        total_w = len(labels) * btn_w + (len(labels) - 1) * gap
        start_x = WINDOW_W // 2 - total_w // 2
        y = 548
        return [
            {"rect": pygame.Rect(start_x + index * (btn_w + gap), y, btn_w, btn_h),
             "label": label, "action": action, "enabled": True}
            for index, (label, action) in enumerate(labels)
        ]

    def _start_air_campaign(self, mode="standard"):
        self.air_mode = mode
        self.air_campaign_active = True
        self.air_run_score = 0
        self.air_loadout = {"cannon": 1, "spread": 0, "laser": 0, "active": "cannon"}
        self.air_level = 0
        self.air_boss_rush_index = 0
        progress = self._air_progress()
        progress["run_active"] = True
        progress["run_mode"] = mode
        progress["run_level"] = 0
        progress["run_loadout"] = dict(self.air_loadout)
        self._prepare_air_level(0, preserve_loadout=True)

    def _continue_air_campaign(self):
        progress = self._air_progress()
        self.air_mode = progress.get("run_mode", "standard")
        self.air_campaign_active = True
        self.air_loadout = dict(progress.get("run_loadout", AIR_STANDARD_LOADOUTS[0]))
        self._air_restore_state = progress.get("run_state")
        self._prepare_air_level(progress.get("run_level", 0), preserve_loadout=True)

    def _start_air_boss_rush(self):
        self.air_mode = "boss_rush"
        self.air_campaign_active = True
        self.air_boss_rush_index = 0
        self.air_boss_rush_health = 5
        self.air_run_score = 0
        self.air_loadout = {"cannon": 3, "spread": 3, "laser": 3, "active": "cannon"}
        self._prepare_air_level(1, preserve_loadout=True)

    def _start_air_level(self, level=None, mode="standard"):
        index = self.air_level if level is None else max(0, min(15, int(level)))
        self.air_mode = mode
        self.air_campaign_active = False
        self.air_loadout = dict(AIR_STANDARD_LOADOUTS[index])
        self._prepare_air_level(index, preserve_loadout=True)

    def _prepare_air_level(self, level, preserve_loadout=False):
        chapter_index = AIR_LEVELS[level]["chapter"] - 1
        if self._check_air_chapter_story(chapter_index, level):
            return
        self.air_level = max(0, min(15, int(level)))
        if not preserve_loadout:
            self.air_loadout = dict(AIR_STANDARD_LOADOUTS[self.air_level])
        self.air_brief_page = 0
        self.state = self.AIR_BRIEF
        self.air_story_message = None
        self.air_story_timer = 0

    def _begin_air_combat(self):
        cfg = AIR_LEVELS[self.air_level]
        restore_state = getattr(self, "_air_restore_state", None)
        if restore_state:
            # Copy in: live combat state must never alias the stored snapshot.
            restore_state = copy.deepcopy(restore_state)
            self.air_player = restore_state["player"]
            self.air_enemies = restore_state["enemies"]
            self.air_bullets = restore_state["bullets"]
            self.air_enemy_bullets = restore_state.get("enemy_bullets", [])
            self.air_powerups = restore_state.get("powerups", [])
            self.air_particles = []
            self.air_missiles = restore_state.get("missiles", [])
            self.air_warnings = []
            self.air_wave = restore_state.get("wave", 0)
            self.air_spawn_tick = restore_state.get("spawn_tick", 0)
            self.air_stage_tick = restore_state.get("stage_tick", 0)
            self.air_score = restore_state["score"]
            self.air_health = restore_state["health"]
            self.air_hits = restore_state.get("hits", 0)
            self.air_threat = restore_state.get("threat", 1.0)
            self.air_combo = restore_state.get("combo", 0)
            self.air_combo_timer = restore_state.get("combo_timer", 0)
            self.air_multiplier = restore_state.get("multiplier", 1.0)
            self.air_grazes = restore_state.get("grazes", 0)
            self.air_destroyed = restore_state.get("destroyed", 0)
            self.air_spawned = restore_state.get("spawned", 0)
            self.air_mission_value = restore_state.get("mission_value", 0)
            self.air_mission_target = cfg["target"]
            self.air_missile_charge = restore_state["missile_charge"]
            self.air_missile_ready = restore_state.get("missile_ready", False)
            self.air_best_missile_kills = restore_state.get("best_missile_kills", 0)
            self.air_loadout = restore_state["loadout"]
            self.air_boss_phase = restore_state.get("boss_phase", 1)
            self.air_boss_phase_flash = restore_state.get("boss_phase_flash", 0)
            self.air_bullet_serial = restore_state.get("bullet_serial", 0)
            self.air_paused = False
            self.air_result = ""
            self.air_rank = "C"
            self.air_stage_rng = random.Random(9000 + self.air_level * 101 + (37 if self.air_mode == "challenge" else 0))
            self.air_entry_snapshot = {
                "loadout": dict(self.air_loadout), "missile_charge": self.air_missile_charge,
                "missile_ready": self.air_missile_ready, "health": self.air_health,
            }
            self._air_restore_state = None
            self.state = self.AIR_PLAYING
            return
        self.air_player = {
            "x": float(AIR_PLAY_RECT.centerx), "y": float(AIR_PLAY_RECT.bottom - 60),
            "r": 5, "cool": 0, "shield": 0, "invuln": 90, "hit_flash": 0,
            "vx": 0.0, "vy": 0.0, "muzzle": 0,
        }
        self.air_enemies = []
        self.air_bullets = []
        self.air_enemy_bullets = []
        self.air_powerups = []
        self.air_particles = []
        self.air_missiles = []
        self.air_warnings = []
        self.air_wave = 0
        self.air_spawn_tick = 0
        self.air_stage_tick = 0
        self.air_score = 0
        self.air_health = (
            self.air_boss_rush_health if self.air_mode == "boss_rush" else 5
        )
        self.air_hits = 0
        self.air_threat = 1.0
        self.air_combo = 0
        self.air_combo_timer = 0
        self.air_multiplier = 1.0
        self.air_grazes = 0
        self.air_destroyed = 0
        self.air_spawned = 0
        self.air_mission_value = 0
        self.air_mission_target = cfg["target"]
        self.air_missile_charge = 0
        self.air_missile_ready = False
        self.air_best_missile_kills = 0
        self.air_boss_phase = 1
        self.air_boss_phase_flash = 0
        self.air_paused = False
        self.air_result = ""
        self.air_rank = "C"
        self.air_stage_rng = random.Random(
            9000 + self.air_level * 101 + (37 if self.air_mode == "challenge" else 0))
        self.air_entry_snapshot = {
            "loadout": dict(self.air_loadout), "missile_charge": self.air_missile_charge,
            "missile_ready": self.air_missile_ready, "health": self.air_health,
        }
        if cfg["boss"]:
            self._spawn_air_boss()
        self.state = self.AIR_PLAYING
        self._record_stat("air", "games_started")
        self._show_air_story(cfg["story"][0], 180)

    def _capture_air_run_state(self):
        # Copied so the snapshot is a value, not an alias of live combat
        # state — otherwise playing would mutate save data in place (R-03).
        return copy.deepcopy({
            "player": self.air_player,
            "enemies": self.air_enemies,
            "bullets": self.air_bullets,
            "enemy_bullets": self.air_enemy_bullets,
            "powerups": self.air_powerups,
            "missiles": self.air_missiles,
            "wave": self.air_wave,
            "spawn_tick": self.air_spawn_tick,
            "stage_tick": self.air_stage_tick,
            "score": self.air_score,
            "health": self.air_health,
            "hits": self.air_hits,
            "threat": self.air_threat,
            "combo": self.air_combo,
            "combo_timer": self.air_combo_timer,
            "multiplier": self.air_multiplier,
            "grazes": self.air_grazes,
            "destroyed": self.air_destroyed,
            "spawned": self.air_spawned,
            "mission_value": self.air_mission_value,
            "missile_charge": self.air_missile_charge,
            "missile_ready": self.air_missile_ready,
            "best_missile_kills": self.air_best_missile_kills,
            "loadout": self.air_loadout,
            "boss_phase": self.air_boss_phase,
            "boss_phase_flash": self.air_boss_phase_flash,
            "bullet_serial": self.air_bullet_serial,
        })

    def _retry_air_level(self):
        if self.air_entry_snapshot:
            self.air_loadout = dict(self.air_entry_snapshot["loadout"])
            self.air_missile_charge = self.air_entry_snapshot["missile_charge"]
            self.air_missile_ready = self.air_entry_snapshot["missile_ready"]
            if self.air_mode == "boss_rush":
                self.air_boss_rush_health = self.air_entry_snapshot["health"]
        self._begin_air_combat()

    def _show_air_story(self, text, frames=180):
        self.air_story_message = text
        self.air_story_timer = frames

    def _air_enemy_hp_scale(self):
        return 1.22 if self.air_mode == "challenge" else 1.0

    def _air_enemy_move_scale(self):
        base = 1.0 if self.air_mode == "challenge" else 0.70
        return base * getattr(self, "dev_enemy_speed", 1.0)

    def _air_enemy_bullet_scale(self):
        base = 1.0 if self.air_mode == "challenge" else 0.85
        return base * getattr(self, "dev_enemy_speed", 1.0)

    def _spawn_air_enemy(self, kind="scout", slot=0, count=1):
        spec = AIR_ENEMY_TYPES[kind]
        move_scale = self._air_enemy_move_scale()
        spread = AIR_PLAY_RECT.width - 100
        x = AIR_PLAY_RECT.left + 50 + ((slot * 97 + self.air_wave * 61) % spread)
        side = -1 if slot % 2 else 1
        hp = max(1, int((spec["hp"] + self.air_level // 5) * self._air_enemy_hp_scale()))
        enemy = {
            "kind": kind, "x": float(x), "y": float(AIR_PLAY_RECT.top - 25 - slot * 12),
            "base_x": float(x), "vx": side * (.55 + slot % 3 * .15) * move_scale,
            "vy": spec["speed"] * (.65 + self.air_level * .015) * move_scale,
            "r": spec["radius"], "hp": hp, "max_hp": hp,
            "value": spec["value"], "shot": -slot * 9,
            "phase": (slot + self.air_wave) * .7, "pattern": spec["pattern"],
            "boss": False, "weak": True, "flash": 0, "escaped": False,
        }
        self.air_enemies.append(enemy)
        self.air_spawned += 1

    def _spawn_air_wave(self):
        cfg = AIR_LEVELS[self.air_level]
        kinds = cfg["enemy_types"]
        kind = kinds[self.air_wave % len(kinds)]
        count = min(7, 3 + self.air_level // 4 + self.air_wave % 3)
        for slot in range(count):
            self._spawn_air_enemy(kind, slot, count)
        if self.air_wave in (3, 7) and self.air_level >= 4:
            elite = kinds[-1]
            self._spawn_air_enemy(elite, count + 1, count + 2)
        self.air_wave += 1

    def _spawn_air_boss(self):
        cfg = AIR_LEVELS[self.air_level]
        hp = int(cfg["boss_hp"] * self._air_enemy_hp_scale())
        move_scale = self._air_enemy_move_scale()
        self.air_enemies.append({
            "kind": "boss", "name": cfg["name"], "x": float(AIR_PLAY_RECT.centerx),
            "y": float(AIR_PLAY_RECT.top + 115), "base_x": float(AIR_PLAY_RECT.centerx),
            "vx": 1.6 * move_scale, "vy": 0.0, "r": 52, "hp": hp, "max_hp": hp,
            "value": 6000 + self.air_level * 400, "shot": 0, "phase": 0.0,
            "pattern": cfg["patterns"][0], "patterns": cfg["patterns"],
            "boss": True, "weak": True, "flash": 0, "escaped": False,
        })
        self.air_spawned = 1
        self._record_stat("air", "bosses_encountered")
        self._show_air_story(f"WARNING // {cfg['name']} // PHASE 1", 210)

    def _fire_air_player_weapon(self):
        player = self.air_player
        weapon = self.air_loadout["active"]
        level = max(1, self.air_loadout[weapon])
        color = AIR_WEAPON_COLORS[weapon]
        shots = []
        if weapon == "cannon":
            offsets = [0] if level == 1 else [-7, 7]
            if level >= 4:
                offsets += [-15, 15]
            for offset in offsets:
                shots.append((offset, 0.0, -10.5, 1 + level // 3, False))
            cooldown = max(3, 8 - level)
        elif weapon == "spread":
            angles = list(range(-level, level + 1))
            for angle in angles:
                shots.append((0, angle * .9, -8.6 + abs(angle) * .12, 1, False))
            cooldown = max(5, 11 - level)
        else:
            width = 4 + level * 2
            shots.append((0, 0.0, -13.0, 1 + level, True))
            if level >= 4:
                shots += [(-width, 0.0, -12.0, 2, True), (width, 0.0, -12.0, 2, True)]
            cooldown = max(2, 6 - level // 2)
        for offset, vx, vy, damage, pierce in shots:
            self.air_bullets.append({
                "x": player["x"] + offset, "y": player["y"] - 22,
                "vx": vx, "vy": vy, "damage": damage, "pierce": pierce,
                "color": color, "life": 90,
            })
        player["cool"] = cooldown
        player["muzzle"] = 3

    def _launch_air_missile(self):
        if not self.air_missile_ready or self.state != self.AIR_PLAYING:
            self.audio.play("air_empty", 0.55)
            return
        targets = sorted(
            self.air_enemies, key=lambda enemy: (not enemy["boss"], -enemy["hp"]))[:8]
        if not targets:
            return
        self.air_missile_ready = False
        self.air_missile_charge = 0
        for index, target in enumerate(targets):
            self.air_missiles.append({
                "x": self.air_player["x"] + (-12 if index % 2 else 12),
                "y": self.air_player["y"] - 12, "target": target, "life": 90,
                "damage": 55 if target["boss"] else 999,
            })
        self.audio.play("air_missile", 0.9)
        self._spawn_air_particles(self.air_player["x"], self.air_player["y"], AIR_PALETTE["accent_light"], 18)

    def _fire_enemy_bullet(self, enemy, angle, speed=3.0, radius=5, warning=False):
        self.air_bullet_serial += 1
        self.air_enemy_bullets.append({
            "id": self.air_bullet_serial, "x": enemy["x"], "y": enemy["y"],
            "vx": math.cos(angle) * speed, "vy": math.sin(angle) * speed,
            "r": radius, "graze": False, "warning": warning, "life": 360,
        })

    def _aim_angle(self, enemy):
        return math.atan2(
            self.air_player["y"] - enemy["y"], self.air_player["x"] - enemy["x"])

    def _enemy_fire_pattern(self, enemy):
        if getattr(self, "dev_freeze_enemies", False):
            return
        pattern = enemy["pattern"]
        aim = self._aim_angle(enemy)
        phase = enemy["phase"]
        speed_scale = (
            self.air_threat
            * self._air_enemy_bullet_scale()
            * (1.08 if self.air_mode == "challenge" else 1.0)
        )
        if pattern in ("aim", "snipe"):
            count = 1 if pattern == "aim" else 3
            for index in range(count):
                self._fire_enemy_bullet(enemy, aim + (index - (count - 1) / 2) * .08,
                                        (3.1 + (pattern == "snipe") * 1.5) * speed_scale)
        elif pattern in ("fan", "choir"):
            count = 5 if pattern == "fan" else 9
            for index in range(count):
                self._fire_enemy_bullet(enemy, aim + (index - count // 2) * .16,
                                        2.7 * speed_scale)
        elif pattern in ("ring", "halo", "nova"):
            count = 12 if pattern == "ring" else 18 if pattern == "halo" else 24
            for index in range(count):
                self._fire_enemy_bullet(enemy, math.tau * index / count + phase,
                                        (2.2 + self.air_boss_phase * .18) * speed_scale)
        elif pattern in ("wall", "citadel"):
            for index in range(9):
                angle = math.pi / 2 + (index - 4) * .105
                if (index + int(phase * 4)) % 4:
                    self._fire_enemy_bullet(enemy, angle, 2.9 * speed_scale, 6)
        elif pattern in ("spiral", "seraph", "sovereign"):
            arms = 3 if pattern == "spiral" else 5
            for arm in range(arms):
                self._fire_enemy_bullet(
                    enemy, phase + math.tau * arm / arms, 2.5 * speed_scale)
        elif pattern in ("cross", "mirror"):
            for angle in (0, math.pi / 2, math.pi, math.pi * 1.5):
                self._fire_enemy_bullet(enemy, angle + phase * .45, 3.0 * speed_scale)
            if pattern == "mirror":
                self._fire_enemy_bullet(enemy, aim, 4.2 * speed_scale, 5, True)
        elif pattern == "mine":
            self._fire_enemy_bullet(enemy, math.pi / 2, 1.35 * speed_scale, 9)
        elif pattern in ("spawn", "command"):
            for offset in (-.18, 0, .18):
                self._fire_enemy_bullet(enemy, aim + offset, 2.8 * speed_scale)

    def _air_player_hit(self, damage=1, source_x=None):
        if getattr(self, "dev_invincible", False):
            return False
        player = self.air_player
        if player.get("invuln", 0) > 0:
            return False
        if player.get("shield", 0) > 0:
            player["shield"] = 0
            player["invuln"] = 55
            self.audio.play("air_shield")
            self._spawn_air_particles(player["x"], player["y"], (100, 230, 255), 14)
            return False
        self.air_health -= damage
        self.air_hits += damage
        player["invuln"] = 105
        player["hit_flash"] = 20
        if source_x is not None:
            player["vx"] = 4.5 if player["x"] >= source_x else -4.5
        self.audio.play("air_hit")
        self._record_stat("air", "damage_taken", damage)
        self._spawn_air_particles(player["x"], player["y"], (255, 90, 75), 24)
        if self.screen_shake_enabled:
            self.shake_duration = 10
        if self.air_health <= 0:
            self._finish_air(False)
        return True

    def _spawn_air_particles(self, x, y, color, count=10):
        if getattr(self, "animation_level", "full") == "off":
            return
        amount = count // 2 if self.animation_level == "reduced" else count
        for index in range(max(2, amount)):
            angle = math.tau * index / max(1, amount)
            speed = 1.2 + (index % 5) * .45
            self.air_particles.append({
                "x": x, "y": y, "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed, "life": 22 + index % 14,
                "max": 36, "color": color, "size": 2 + index % 4,
            })

    def _destroy_air_enemy(self, enemy, missile=False):
        if enemy not in self.air_enemies:
            return
        self.air_enemies.remove(enemy)
        self.air_destroyed += 1
        self.air_combo += 1
        self.air_combo_timer = 150
        self.air_multiplier = min(5.0, 1.0 + self.air_combo // 8 * .5)
        gained = int(enemy["value"] * self.air_multiplier)
        self.air_score += gained
        self.air_missile_charge = min(100, self.air_missile_charge + (18 if enemy["boss"] else 8))
        if self.air_missile_charge >= 100:
            self.air_missile_ready = True
        self._record_stat("air", "enemies_destroyed")
        if enemy["boss"]:
            self._record_stat("air", "bosses_defeated")
        self._spawn_air_particles(enemy["x"], enemy["y"],
                                  AIR_ENEMY_COLORS.get(enemy["kind"], (255, 90, 120)),
                                  40 if enemy["boss"] else 14)
        self.audio.play("air_blast", 0.9 if enemy["boss"] else 0.55)
        if missile:
            self.air_best_missile_kills += 1
            self._record_stat("air", "best_missile_kills",
                              self.air_best_missile_kills, mode="max")
        else:
            self.air_best_missile_kills = 0
        self._update_air_mission_on_kill(enemy)
        drop_index = self.air_destroyed + self.air_level * 3
        repair_mod = 29 if self.air_mode == "challenge" else 21
        if drop_index % repair_mod == 0:
            self._drop_air_powerup(enemy, "repair")
        elif drop_index % 17 == 0:
            self._drop_air_powerup(enemy, "shield")
        elif drop_index % 7 == 0:
            weapons = ("cannon", "spread", "laser")
            self._drop_air_powerup(enemy, weapons[(drop_index // 7) % 3])

    def _drop_air_powerup(self, enemy, kind):
        self.air_powerups.append({
            "x": enemy["x"], "y": enemy["y"], "kind": kind,
            "phase": self.air_stage_tick * .05,
        })

    def _update_air_mission_on_kill(self, enemy):
        mission = AIR_LEVELS[self.air_level]["mission"]
        if mission in ("intercept", "breakthrough"):
            self.air_mission_value = self.air_destroyed
        elif mission == "nodes" and enemy["kind"] in ("layer", "commander"):
            self.air_mission_value += 1
        elif mission == "fortress" and enemy["kind"] in ("bomber", "shield", "commander"):
            self.air_mission_value += 1
        elif mission == "convoy" and enemy["kind"] in ("carrier", "commander"):
            self.air_mission_value += 1

    def _collect_air_powerup(self, power):
        kind = power["kind"]
        if kind in AIR_WEAPON_COLORS:
            self.air_loadout["active"] = kind
            self.air_loadout[kind] = min(5, self.air_loadout.get(kind, 0) + 1)
            self._record_stat("air", f"{kind}_level",
                              self.air_loadout[kind], mode="max")
        elif kind == "repair":
            self.air_health = min(5, self.air_health + 1)
            self._record_stat("air", "repairs")
        elif kind == "shield":
            self.air_player["shield"] = 1
        self._record_stat("air", "powerups")
        self.audio.play("air_power")
        self._spawn_air_particles(power["x"], power["y"], (170, 245, 255), 12)

    def _update_air_player(self):
        player = self.air_player
        keys = pygame.key.get_pressed()
        focus = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        speed = 2.6 if focus else 5.2
        dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (
            keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (
            keys[pygame.K_UP] or keys[pygame.K_w])
        length = max(1.0, math.hypot(dx, dy))
        target_vx = dx / length * speed if dx or dy else 0.0
        target_vy = dy / length * speed if dx or dy else 0.0
        player["vx"] = player["vx"] * .65 + target_vx * .35
        player["vy"] = player["vy"] * .65 + target_vy * .35
        player["x"] = max(AIR_PLAY_RECT.left + 18,
                          min(AIR_PLAY_RECT.right - 18, player["x"] + player["vx"]))
        player["y"] = max(AIR_PLAY_RECT.top + 105,
                          min(AIR_PLAY_RECT.bottom - 18, player["y"] + player["vy"]))
        player["cool"] -= 1
        player["invuln"] = max(0, player["invuln"] - 1)
        player["hit_flash"] = max(0, player["hit_flash"] - 1)
        player["muzzle"] = max(0, player["muzzle"] - 1)
        if player["cool"] <= 0:
            self._fire_air_player_weapon()

    def _update_air_regular_stage(self):
        cfg = AIR_LEVELS[self.air_level]
        self.air_spawn_tick += 1
        interval = max(480, int(650 / self.air_threat))
        if self.air_wave < cfg["waves"] and self.air_spawn_tick >= interval:
            self.air_spawn_tick = 0
            self._spawn_air_wave()
        if cfg["mission"] in ("escort", "evac"):
            self.air_mission_value = max(
                0, 100 - sum(8 for enemy in self.air_enemies if enemy.get("escaped")))
        elif cfg["mission"] == "gauntlet":
            self.air_mission_value = min(cfg["target"], self.air_stage_tick)
        if self.air_wave >= cfg["waves"] and not self.air_enemies:
            self._finish_air(True)

    def _update_air_enemy(self, enemy):
        enemy["phase"] += (
            .025 + self.air_boss_phase * .003
        ) * self._air_enemy_move_scale()
        enemy["flash"] = max(0, enemy["flash"] - 1)
        if enemy["boss"]:
            enemy["x"] += enemy["vx"]
            if enemy["x"] < AIR_PLAY_RECT.left + 80 or enemy["x"] > AIR_PLAY_RECT.right - 80:
                enemy["vx"] *= -1
            ratio = enemy["hp"] / max(1, enemy["max_hp"])
            phase = 1 if ratio > .67 else 2 if ratio > .34 else 3
            if phase != self.air_boss_phase:
                self.air_boss_phase = phase
                enemy["pattern"] = enemy["patterns"][phase - 1]
                enemy["weak"] = False
                self.air_boss_phase_flash = 100
                self.air_enemy_bullets.clear()
                self._show_air_story(
                    f"{enemy['name']} // PHASE {phase} // ARMOR SHIFT", 150)
                self.audio.play("air_phase", 0.85)
            if self.air_boss_phase_flash > 55:
                enemy["weak"] = False
            else:
                enemy["weak"] = True
        else:
            kind = enemy["kind"]
            if kind in ("scout", "striker"):
                amplitude = 42 if kind == "scout" else 68
                enemy["x"] = enemy["base_x"] + math.sin(enemy["phase"] * 2) * amplitude
            elif kind in ("sniper", "shield"):
                enemy["x"] += enemy["vx"]
                if enemy["x"] < AIR_PLAY_RECT.left + 35 or enemy["x"] > AIR_PLAY_RECT.right - 35:
                    enemy["vx"] *= -1
            else:
                enemy["x"] = enemy["base_x"] + math.sin(enemy["phase"]) * 45
            enemy["y"] += enemy["vy"]
        enemy["shot"] += 1
        fire_interval = max(
            30 if self.air_mode != "challenge" else 24,
            int((108 - self.air_level * 2 - self.air_boss_phase * 6) / self.air_threat))
        if enemy["shot"] >= fire_interval:
            enemy["shot"] = 0
            self._enemy_fire_pattern(enemy)
        if not enemy["boss"] and enemy["y"] > AIR_PLAY_RECT.bottom + 35:
            enemy["escaped"] = True
            self.air_enemies.remove(enemy)
            if AIR_LEVELS[self.air_level]["mission"] in ("escort", "evac"):
                self.air_mission_value = max(0, self.air_mission_value - 8)
            else:
                self._air_player_hit(1, enemy["x"])
            return
        if math.hypot(enemy["x"] - self.air_player["x"],
                      enemy["y"] - self.air_player["y"]) < enemy["r"] + 14:
            self._air_player_hit(1, enemy["x"])
            if not enemy["boss"] and enemy in self.air_enemies:
                self._destroy_air_enemy(enemy)

    def _update_air_projectiles(self):
        for bullet in self.air_bullets[:]:
            bullet["x"] += bullet["vx"]
            bullet["y"] += bullet["vy"]
            bullet["life"] -= 1
            hit = False
            for enemy in self.air_enemies[:]:
                if math.hypot(bullet["x"] - enemy["x"], bullet["y"] - enemy["y"]) <= enemy["r"] + 5:
                    if enemy.get("weak", True):
                        enemy["hp"] -= bullet["damage"]
                        enemy["flash"] = 3
                    if not bullet["pierce"]:
                        hit = True
                    if enemy["hp"] <= 0:
                        self._destroy_air_enemy(enemy)
                    if hit:
                        break
            if hit or bullet["life"] <= 0 or bullet["y"] < AIR_PLAY_RECT.top - 20:
                if bullet in self.air_bullets:
                    self.air_bullets.remove(bullet)
        focus = pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT]
        for bullet in self.air_enemy_bullets[:]:
            bullet["x"] += bullet["vx"]
            bullet["y"] += bullet["vy"]
            bullet["life"] -= 1
            distance = math.hypot(
                bullet["x"] - self.air_player["x"], bullet["y"] - self.air_player["y"])
            if distance <= bullet["r"] + self.air_player["r"]:
                self.air_enemy_bullets.remove(bullet)
                self._air_player_hit(1, bullet["x"])
            elif focus and not bullet["graze"] and distance <= bullet["r"] + 24:
                bullet["graze"] = True
                self.air_grazes += 1
                self.air_score += int(25 * self.air_multiplier)
                self._record_stat("air", "grazes")
                self.audio.play("air_graze", 0.35)
            elif (bullet["life"] <= 0 or bullet["x"] < AIR_PLAY_RECT.left - 30
                  or bullet["x"] > AIR_PLAY_RECT.right + 30
                  or bullet["y"] < AIR_PLAY_RECT.top - 40
                  or bullet["y"] > AIR_PLAY_RECT.bottom + 40):
                self.air_enemy_bullets.remove(bullet)
        for missile in self.air_missiles[:]:
            target = missile["target"]
            if target not in self.air_enemies:
                self.air_missiles.remove(missile)
                continue
            dx, dy = target["x"] - missile["x"], target["y"] - missile["y"]
            length = max(1.0, math.hypot(dx, dy))
            missile["x"] += dx / length * 11
            missile["y"] += dy / length * 11
            missile["life"] -= 1
            if length < target["r"] + 12:
                target["hp"] -= missile["damage"]
                self.air_missiles.remove(missile)
                if target["hp"] <= 0:
                    self._destroy_air_enemy(target, missile=True)
            elif missile["life"] <= 0:
                self.air_missiles.remove(missile)

    def _update_air_pickups_and_effects(self):
        for power in self.air_powerups[:]:
            power["phase"] += .08
            power["y"] += 1.7
            if math.hypot(power["x"] - self.air_player["x"],
                          power["y"] - self.air_player["y"]) < 27:
                self.air_powerups.remove(power)
                self._collect_air_powerup(power)
            elif power["y"] > AIR_PLAY_RECT.bottom + 20:
                self.air_powerups.remove(power)
        for particle in self.air_particles[:]:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["vx"] *= .96
            particle["vy"] *= .96
            particle["life"] -= 1
            if particle["life"] <= 0:
                self.air_particles.remove(particle)
        self.air_combo_timer = max(0, self.air_combo_timer - 1)
        if self.air_combo_timer == 0:
            self.air_combo = 0
            self.air_multiplier = 1.0
        self.air_boss_phase_flash = max(0, self.air_boss_phase_flash - 1)
        if self.air_story_timer > 0:
            self.air_story_timer -= 1
            if self.air_story_timer == 0:
                self.air_story_message = None

    def _update_air_threat(self):
        performance = 1.0 + min(.06, self.air_combo / 180) - min(.10, self.air_hits * .025)
        self.air_threat = max(.90, min(1.06, performance))

    def _update_air_raid(self):
        if self.air_unlock_notice_frames > 0:
            self.air_unlock_notice_frames -= 1
            if self.air_unlock_notice_frames == 0:
                self.air_challenge_unlocked_notice = False
        if self.state == self.AIR_MENU:
            self.air_preview_tick += 1
            self.air_demo_scene_tick += 1
            if self.air_demo_scene_tick >= 360:
                self.air_demo_scene_tick = 0
                self.air_demo_scene = (self.air_demo_scene + 1) % 3
            return
        if self.state != self.AIR_PLAYING or self.air_paused:
            return
        self.air_stage_tick += 1
        self._update_air_player()
        if not AIR_LEVELS[self.air_level]["boss"]:
            self._update_air_regular_stage()
        for enemy in self.air_enemies[:]:
            self._update_air_enemy(enemy)
        self._update_air_projectiles()
        self._update_air_pickups_and_effects()
        self._update_air_threat()
        if AIR_LEVELS[self.air_level]["boss"] and not self.air_enemies:
            self._finish_air(True)

    def _air_mission_completion(self):
        cfg = AIR_LEVELS[self.air_level]
        if cfg["boss"]:
            return 1.0
        if cfg["mission"] in ("escort", "evac"):
            return max(0.0, min(1.0, self.air_mission_value / 100))
        return max(0.0, min(1.0, self.air_mission_value / max(1, cfg["target"])))

    def _calculate_air_rating(self):
        cfg = AIR_LEVELS[self.air_level]
        expected_score = 9000 + self.air_level * 2500 + (16000 if cfg["boss"] else 0)
        score_part = min(1.0, self.air_score / expected_score) * 40
        kill_part = (self.air_destroyed / max(1, self.air_spawned)) * 25
        mission_part = self._air_mission_completion() * 20
        health_part = (max(0, self.air_health) / 5) * 15
        total = score_part + kill_part + mission_part + health_part
        threshold_shift = 5 if self.air_mode == "challenge" else 0
        if total >= 90 + threshold_shift:
            return "S", round(total)
        if total >= 75 + threshold_shift:
            return "A", round(total)
        if total >= 55 + threshold_shift:
            return "B", round(total)
        return "C", round(total)

    def _finish_air(self, won):
        if self.state == self.AIR_END:
            return
        self.air_result = "MISSION CLEAR" if won else "AIRCRAFT LOST"
        self.air_rank, self.air_rating_score = self._calculate_air_rating()
        self.state = self.AIR_END
        self._record_stat("air", "games_completed")
        self._record_stat("air", "best_score", self.air_score, mode="max")
        self._record_stat("air", "highest_level", self.air_level + 1, mode="max")
        progress = self._air_progress()
        if won:
            self.air_run_score += self.air_score
            mode_key = "challenge" if self.air_mode == "challenge" else "standard"
            if self.air_mode == "boss_rush":
                self._complete_air_boss_rush_stage()
                return
            progress["unlocked"] = max(
                progress.get("unlocked", 1), min(16, self.air_level + 2))
            progress["completed"] = max(progress.get("completed", 0), self.air_level + 1)
            ratings = progress["ratings"][mode_key]
            key = str(self.air_level + 1)
            previous = ratings.get(key, {})
            if AIR_RANK_ORDER[self.air_rank] >= AIR_RANK_ORDER.get(previous.get("rank", "C"), 0):
                ratings[key] = {
                    "rank": self.air_rank, "score": max(self.air_score, previous.get("score", 0)),
                    "kill_rate": max(round(self.air_destroyed / max(1, self.air_spawned) * 100),
                                     previous.get("kill_rate", 0)),
                }
            progress["archive_unlocked"] = max(
                progress.get("archive_unlocked", 1), AIR_LEVELS[self.air_level]["chapter"])
            self._record_stat("air", "levels_cleared",
                              progress["completed"], mode="max")
            if self.air_rank == "S":
                self._record_stat("air", "s_ranks")
            if self.air_mode == "challenge":
                self._record_stat("air", "challenge_clears")
            if self.air_campaign_active:
                if self.air_level >= 15:
                    progress["run_active"] = False
                    self._clear_run_state("air")
                    if self.air_mode == "standard":
                        progress["challenge_unlocked"] = True
                        progress["campaign_complete"] = True
                        self.air_challenge_unlocked_notice = True
                        self.air_unlock_notice_frames = AIR_UNLOCK_NOTICE_FRAMES
                        self._record_stat("air", "campaigns_completed")
                    else:
                        progress["challenge_complete"] = True
                        self._record_stat("air", "challenge_campaigns_completed")
                else:
                    progress["run_active"] = True
                    progress["run_level"] = self.air_level + 1
                    progress["run_mode"] = self.air_mode
                    progress["run_loadout"] = dict(self.air_loadout)
            self.audio.play("air_clear")
        else:
            self._record_stat("air", "deaths")
            self.audio.play_gameover("air")
            self._clear_run_state("air")
        # Unlock skins based on newly earned achievements
        unlocked_achievements = self.save_data.get("achievements", {})
        progress = self._air_progress()
        skins = list(progress.get("skins_unlocked", ["default"]))
        if "air_cannon_five" in unlocked_achievements and "crimson" not in skins:
            skins.append("crimson")
        if "air_first_s" in unlocked_achievements and "azure" not in skins:
            skins.append("azure")
        if "air_all_s" in unlocked_achievements and "gold" not in skins:
            skins.append("gold")
        progress["skins_unlocked"] = skins
        self._save_now()

    def _complete_air_boss_rush_stage(self):
        progress = self._air_progress()
        self.air_boss_rush_index += 1
        if self.air_boss_rush_index >= 8:
            progress["boss_rush_complete"] = True
            best = progress["boss_rush_best"]
            best["score"] = max(best.get("score", 0), self.air_run_score)
            best["health"] = max(best.get("health", 0), self.air_health)
            self._record_stat("air", "boss_rush_clears")
            self.air_result = "BOSS RUSH CLEAR"
            self.state = self.AIR_END
            self._clear_run_state("air")
        else:
            self.air_boss_rush_health = min(5, self.air_health + 1)
            self.air_supply_index = 0
            self.air_supply_next_level = self.air_boss_rush_index * 2 + 1
            self.state = self.AIR_SUPPLY
        self._save_now()

    def _choose_air_supply(self, weapon):
        self.air_loadout[weapon] = min(5, self.air_loadout[weapon] + 1)
        self.air_loadout["active"] = weapon
        self.air_level = self.air_supply_next_level
        self.air_entry_snapshot = {
            "loadout": dict(self.air_loadout),
            "missile_charge": self.air_missile_charge,
            "missile_ready": self.air_missile_ready,
            "health": self.air_boss_rush_health,
        }
        self._prepare_air_level(self.air_level, preserve_loadout=True)

    def _advance_air_after_clear(self):
        if self.air_mode == "boss_rush" or not self.air_campaign_active or self.air_level >= 15:
            self.state = self.AIR_MENU
            return
        self._prepare_air_level(self.air_level + 1, preserve_loadout=True)

    def _handle_air_menu_key(self, event):
        items = self._air_menu_items()
        if event.key in (pygame.K_UP, pygame.K_w):
            self.air_menu_index = (self.air_menu_index - 1) % len(items)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.air_menu_index = (self.air_menu_index + 1) % len(items)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._activate_air_menu(items[self.air_menu_index][1])
        elif event.key == pygame.K_ESCAPE:
            self._go_desktop()

    def _activate_air_menu(self, action):
        enabled = {item[1]: item[2] for item in self._air_menu_items()}.get(action, False)
        if not enabled:
            self.audio.play("error", .6)
            self._show_air_story("COMMAND: COMPLETE STANDARD CAMPAIGN TO UNLOCK.", 160)
            return
        actions = {
            "new_campaign": lambda: self._start_air_campaign("standard"),
            "continue": self._continue_air_campaign,
            "select": lambda: setattr(self, "state", self.AIR_SELECT),
            "challenge": lambda: self._start_air_campaign("challenge"),
            "boss_rush": self._start_air_boss_rush,
            "archive": lambda: setattr(self, "state", self.AIR_ARCHIVE),
            "controls": lambda: setattr(self, "state", self.AIR_CONTROLS),
            "skins": lambda: self._start_transition(self.AIR_SKINS, "fade", frames=28),
            "story_archive": self._open_air_story_archive,
            "desktop": self._go_desktop,
        }
        actions[action]()

    def _handle_air_event(self, event):
        if self.state == self.AIR_PLAYING and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.air_paused = not self.air_paused
            elif event.key == pygame.K_SPACE and not self.air_paused:
                self._launch_air_missile()
            elif event.key == pygame.K_r:
                self._retry_air_level()
            elif event.key == pygame.K_ESCAPE:
                self.state = self.AIR_MENU
            return
        if self.state == self.AIR_MENU:
            if event.type == pygame.KEYDOWN:
                self._handle_air_menu_key(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in self._air_menu_buttons():
                    if button["rect"].collidepoint(event.pos):
                        self.air_pressed = button["action"]
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                for button in self._air_menu_buttons():
                    if button["rect"].collidepoint(event.pos) and self.air_pressed == button["action"]:
                        self._activate_air_menu(button["action"])
                self.air_pressed = None
        elif self.state == self.AIR_SELECT:
            self._handle_level_select(
                event, "air", 16, lambda level: self._start_air_level(level, "standard"),
                self.AIR_MENU)
        elif self.state == self.AIR_CONTROLS:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.state = self.AIR_MENU
        elif self.state == self.AIR_BRIEF:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._begin_air_combat()
                elif event.key == pygame.K_ESCAPE:
                    self.state = self.AIR_MENU
        elif self.state == self.AIR_ARCHIVE:
            if event.type == pygame.KEYDOWN:
                unlocked = self._air_progress().get("archive_unlocked", 1)
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.air_archive_index = max(0, self.air_archive_index - 1)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.air_archive_index = min(unlocked - 1, self.air_archive_index + 1)
                elif event.key == pygame.K_ESCAPE:
                    self.state = self.AIR_MENU
        elif self.state == self.AIR_SUPPLY and event.type == pygame.KEYDOWN:
            choices = ("cannon", "spread", "laser")
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.air_supply_index = (self.air_supply_index - 1) % 3
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.air_supply_index = (self.air_supply_index + 1) % 3
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._choose_air_supply(choices[self.air_supply_index])
        elif self.state == self.AIR_END and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self._retry_air_level()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.air_result in ("MISSION CLEAR", "BOSS RUSH CLEAR"):
                    self._advance_air_after_clear()
                else:
                    self._retry_air_level()
            elif event.key == pygame.K_ESCAPE:
                self.state = self.AIR_MENU
        elif self.state == self.AIR_END:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in self._air_end_buttons():
                    if button["rect"].collidepoint(event.pos):
                        self.air_pressed = button["action"]
                        break
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                for button in self._air_end_buttons():
                    if button["rect"].collidepoint(event.pos) and self.air_pressed == button["action"]:
                        self._activate_air_end_button(button["action"])
                        break
                self.air_pressed = None

    def _activate_air_end_button(self, action):
        if action == "continue":
            self._advance_air_after_clear()
        elif action == "retry":
            self._retry_air_level()
        elif action == "menu":
            self.state = self.AIR_MENU
        elif action == "desktop":
            self._go_desktop()

    def _draw_air_raid(self):
        if self.state == self.AIR_MENU:
            self._draw_air_menu()
        elif self.state == self.AIR_SELECT:
            self._draw_level_select(
                "AIR RAID", 16, self._air_progress().get("unlocked", 1),
                AIR_PALETTE, "air")
            self._draw_air_rating_marks()
        elif self.state == self.AIR_CONTROLS:
            draw_arcade_frame(self, "AIR RAID", "FLIGHT MANUAL", AIR_PALETTE)
            self._draw_controls(
                ["WASD / ARROWS  MOVE", "SHIFT  FOCUS / SHOW CORE",
                 "SPACE  CHARGED MISSILE", "P  PAUSE   R  RETRY   ESC  MENU"],
                AIR_PALETTE)
        elif self.state == self.AIR_BRIEF:
            self._draw_air_brief()
        elif self.state == self.AIR_ARCHIVE:
            self._draw_air_archive()
        elif self.state == self.AIR_SUPPLY:
            self._draw_air_supply()
        else:
            self._draw_air_combat()

    def _draw_air_menu(self):
        if self._check_air_prologue():
            return
        from .lore import get_world
        world = get_world("air")
        sub_en = "WARDEN FLIGHT / AUTONOMOUS WAR NETWORK"
        sub_zh = "守望者飞行队 / 自主战争网络"
        if world:
            sub_en = world["desktop_subtitle_en"]
            sub_zh = world["desktop_subtitle_zh"]
        draw_arcade_frame(
            self, "AIR RAID",
            sub_zh if is_chinese() else sub_en,
            AIR_PALETTE)
        self._draw_air_cinematic_demo()
        mouse = self._logical_mouse_pos()
        for index, button in enumerate(self._air_menu_buttons()):
            selected = index == self.air_menu_index
            hovered = button["rect"].collidepoint(mouse)
            palette = AIR_PALETTE
            draw_arcade_button(
                self, button, palette, hovered or selected,
                self.air_pressed == button["action"])
            if not button["enabled"]:
                shade = pygame.Surface(button["rect"].size, pygame.SRCALPHA)
                shade.fill((0, 0, 0, 115))
                self.screen.blit(shade, button["rect"])
        if self.air_story_message:
            message = render_pixel_text(
                self.font_small, self.air_story_message, AIR_PALETTE["accent_light"], scale=2)
            self.screen.blit(message, (640 - message.get_width() // 2, 624))

    def _draw_air_cinematic_demo(self):
        area = pygame.Rect(170, 156, 940, 151)
        pygame.draw.rect(self.screen, AIR_PALETTE["panel_dark"], area)
        pygame.draw.rect(self.screen, AIR_PALETTE["accent"], area, 2)
        tick = self.air_demo_scene_tick
        scene = self.air_demo_scene
        for index in range(35):
            x = area.x + (index * 83 + tick * (1 + index % 3)) % area.width
            y = area.y + 12 + (index * 37) % (area.height - 24)
            pygame.draw.rect(self.screen, (30, 88, 115), (x, y, 2, 5))
        player_x = area.x + 150 + int(math.sin(tick * .025) * 70)
        player_y = area.bottom - 35
        self._draw_air_ship(player_x, player_y, 1.0)
        if scene == 0:
            for index in range(5):
                ex = area.x + 470 + index * 80
                ey = area.y + 45 + abs(2 - index) * 15
                self._draw_air_enemy_shape(
                    {"kind": "scout", "x": ex, "y": ey, "r": 13, "boss": False,
                     "flash": 0}, .85)
                pygame.draw.line(self.screen, AIR_WEAPON_COLORS["cannon"],
                                 (player_x, player_y - 20), (ex, ey + 15), 2)
        elif scene == 1:
            colors = list(AIR_WEAPON_COLORS.values())
            for index, color in enumerate(colors):
                x = player_x + (index - 1) * 28
                pygame.draw.line(self.screen, color, (x, player_y - 18),
                                 (x + (index - 1) * 35, area.y + 22), 4)
            label = render_pixel_text(
                self.font_small, "WEAPON CORE SHIFT", AIR_PALETTE["text"], scale=2)
            self.screen.blit(label, (area.right - label.get_width() - 25, area.y + 20))
        else:
            boss = {"kind": "boss", "name": "SOVEREIGN", "x": area.right - 180,
                    "y": area.centery, "r": 48, "boss": True, "flash": 0,
                    "hp": 1, "max_hp": 1}
            self._draw_air_enemy_shape(boss, .8)
            for index in range(6):
                t = (tick * .035 + index / 6) * math.tau
                mx = player_x + math.cos(t) * (35 + index * 5)
                my = player_y - 20 - index * 9
                pygame.draw.circle(self.screen, (255, 240, 160), (int(mx), int(my)), 4)
            warning = render_pixel_text(
                self.font_small, "MISSILE LOCK // BOSS SIGNAL", (255, 105, 120), scale=2)
            self.screen.blit(warning, (area.centerx - warning.get_width() // 2, area.y + 12))

    def _draw_air_brief(self):
        cfg = AIR_LEVELS[self.air_level]
        self.screen.fill(AIR_PALETTE["bg"])
        panel = pygame.Rect(140, 70, 1000, 580)
        pygame.draw.rect(self.screen, C.OUTLINE, panel, 5)
        pygame.draw.rect(self.screen, AIR_PALETTE["panel"], panel.inflate(-10, -10))
        pygame.draw.rect(self.screen, AIR_PALETTE["accent"], panel.inflate(-24, -24), 2)
        chapter = render_pixel_text(
            self.font_small, f"CHAPTER {cfg['chapter']:02d} // {self.air_mode.upper()}",
            AIR_PALETTE["muted"], scale=2)
        title = render_pixel_text(
            self.font_menu_title, cfg["title"], AIR_PALETTE["accent_light"], scale=3)
        self.screen.blit(chapter, (panel.centerx - chapter.get_width() // 2, 105))
        self.screen.blit(title, (panel.centerx - title.get_width() // 2, 145))
        radar = pygame.Rect(220, 255, 300, 245)
        pygame.draw.rect(self.screen, AIR_PALETTE["panel_dark"], radar)
        pygame.draw.rect(self.screen, AIR_PALETTE["accent"], radar, 2)
        for radius in (35, 70, 105):
            pygame.draw.circle(self.screen, (25, 90, 110), radar.center, radius, 1)
        sweep = self.anim_tick * .035
        pygame.draw.line(
            self.screen, AIR_PALETTE["accent_light"], radar.center,
            (radar.centerx + math.cos(sweep) * 110, radar.centery + math.sin(sweep) * 110), 2)
        for index, line in enumerate(cfg["brief"]):
            text = render_pixel_text(self.font_small, line, AIR_PALETTE["text"], scale=2)
            self.screen.blit(text, (575, 285 + index * 48))
        objective = render_pixel_text(
            self.font_status, self._air_objective_text(), AIR_WEAPON_COLORS["cannon"], scale=2)
        self.screen.blit(objective, (575, 405))
        hint = render_pixel_text(
            self.font_small, "ENTER / SPACE  DEPLOY     ESC  ABORT", AIR_PALETTE["muted"], scale=2)
        self.screen.blit(hint, (panel.centerx - hint.get_width() // 2, 580))

    def _air_objective_text(self):
        cfg = AIR_LEVELS[self.air_level]
        labels = {
            "intercept": "OBJECTIVE: INTERCEPT SCOUT GROUPS",
            "escort": "OBJECTIVE: ESCORT RELAY CRAFT",
            "nodes": "OBJECTIVE: DESTROY JAMMER NODES",
            "evac": "OBJECTIVE: PROTECT EVACUATION LANE",
            "fortress": "OBJECTIVE: DESTROY GUN DECKS",
            "gauntlet": "OBJECTIVE: SURVIVE STATIC CORRIDOR",
            "convoy": "OBJECTIVE: DESTROY MEMORY CONVOY",
            "breakthrough": "OBJECTIVE: BREAK THE FINAL SCREEN",
            "boss": f"OBJECTIVE: DESTROY {cfg['name']}",
        }
        return labels[cfg["mission"]]

    def _draw_air_archive(self):
        self.screen.fill(AIR_PALETTE["bg"])
        panel = pygame.Rect(100, 55, 1080, 610)
        pygame.draw.rect(self.screen, C.OUTLINE, panel, 5)
        pygame.draw.rect(self.screen, AIR_PALETTE["panel"], panel.inflate(-10, -10))
        pygame.draw.rect(self.screen, AIR_PALETTE["accent"], panel.inflate(-24, -24), 2)
        unlocked = self._air_progress().get("archive_unlocked", 1)
        entry = AIR_ARCHIVE[min(self.air_archive_index, unlocked - 1)]
        title = render_pixel_text(
            self.font_menu_title, f"ARCHIVE {entry['chapter']:02d} // {entry['title']}",
            AIR_PALETTE["accent_light"], scale=3)
        self.screen.blit(title, (panel.centerx - title.get_width() // 2, 88))
        boss = render_pixel_text(
            self.font_status, f"COMMAND FRAME: {entry['boss']}",
            (255, 105, 130), scale=2)
        self.screen.blit(boss, (panel.centerx - boss.get_width() // 2, 175))
        for index, line in enumerate(entry["lines"]):
            text = render_pixel_text(self.font_small, line, AIR_PALETTE["text"], scale=2)
            self.screen.blit(text, (panel.centerx - text.get_width() // 2, 250 + index * 62))
        footer = render_pixel_text(
            self.font_small,
            f"A / D  RECORD {self.air_archive_index + 1:02d} / {unlocked:02d}     ESC  RETURN",
            AIR_PALETTE["muted"], scale=2)
        self.screen.blit(footer, (panel.centerx - footer.get_width() // 2, 610))

    def _draw_air_supply(self):
        self.screen.fill(AIR_PALETTE["bg"])
        panel = pygame.Rect(150, 90, 980, 540)
        pygame.draw.rect(self.screen, C.OUTLINE, panel, 5)
        pygame.draw.rect(self.screen, AIR_PALETTE["panel"], panel.inflate(-10, -10))
        pygame.draw.rect(self.screen, AIR_PALETTE["accent"], panel.inflate(-24, -24), 2)
        title = render_pixel_text(
            self.font_menu_title, "BOSS RUSH // FIELD SUPPLY",
            AIR_PALETTE["accent_light"], scale=3)
        self.screen.blit(title, (panel.centerx - title.get_width() // 2, 125))
        note = render_pixel_text(
            self.font_small, "HULL +1  //  SELECT ONE WEAPON CORE",
            AIR_PALETTE["text"], scale=2)
        self.screen.blit(note, (panel.centerx - note.get_width() // 2, 205))
        choices = ("cannon", "spread", "laser")
        for index, weapon in enumerate(choices):
            rect = pygame.Rect(245 + index * 270, 285, 250, 190)
            selected = index == self.air_supply_index
            pygame.draw.rect(self.screen, C.OUTLINE, rect, 5)
            pygame.draw.rect(
                self.screen,
                AIR_PALETTE["hover"] if selected else AIR_PALETTE["panel_dark"],
                rect.inflate(-10, -10))
            pygame.draw.rect(self.screen, AIR_WEAPON_COLORS[weapon], rect.inflate(-24, -24), 3)
            name = render_pixel_text(
                self.font_status, weapon.upper(), AIR_WEAPON_COLORS[weapon], scale=2)
            level = render_pixel_text(
                self.font_small,
                f"LEVEL {self.air_loadout[weapon]} > {min(5, self.air_loadout[weapon] + 1)}",
                AIR_PALETTE["text"], scale=2)
            self.screen.blit(name, (rect.centerx - name.get_width() // 2, rect.y + 45))
            self.screen.blit(level, (rect.centerx - level.get_width() // 2, rect.y + 105))
        hint = render_pixel_text(
            self.font_small, "A / D  SELECT     ENTER / SPACE  CONFIRM",
            AIR_PALETTE["muted"], scale=2)
        self.screen.blit(hint, (panel.centerx - hint.get_width() // 2, 555))

    def _draw_air_rating_marks(self):
        ratings = self._air_progress().get("ratings", {}).get("standard", {})
        page = self.air_select_page
        start = page * 12
        for index in range(start, min(16, start + 12)):
            col, row = (index - start) % 6, (index - start) // 6
            rank = ratings.get(str(index + 1), {}).get("rank")
            if rank:
                text = render_pixel_text(
                    self.font_status, rank,
                    {"S": (255, 220, 80), "A": (110, 245, 210),
                     "B": (110, 185, 255), "C": (190, 150, 160)}[rank], scale=2)
                self.screen.blit(text, (235 + col * 174, 252 + row * 100))

    def _draw_air_combat(self):
        self.screen.fill(AIR_PALETTE["bg"])
        self._draw_air_background()
        pygame.draw.rect(self.screen, C.OUTLINE, AIR_PLAY_RECT, 5)
        pygame.draw.rect(self.screen, AIR_PALETTE["accent"], AIR_PLAY_RECT, 2)
        for bullet in self.air_bullets:
            pygame.draw.line(
                self.screen, bullet["color"],
                (int(bullet["x"]), int(bullet["y"] + 6)),
                (int(bullet["x"]), int(bullet["y"] - 8)),
                4 if bullet["pierce"] else 2)
        for bullet in self.air_enemy_bullets:
            color = (255, 245, 245) if bullet["warning"] else (
                (255, 75, 125) if bullet["id"] % 2 else (185, 80, 245))
            pygame.draw.circle(
                self.screen, C.OUTLINE, (int(bullet["x"]), int(bullet["y"])),
                bullet["r"] + 2)
            pygame.draw.circle(
                self.screen, color, (int(bullet["x"]), int(bullet["y"])), bullet["r"])
        for missile in self.air_missiles:
            pygame.draw.circle(
                self.screen, (255, 240, 155),
                (int(missile["x"]), int(missile["y"])), 5)
            pygame.draw.line(
                self.screen, (255, 120, 70),
                (int(missile["x"]), int(missile["y"] + 4)),
                (int(missile["x"]), int(missile["y"] + 13)), 3)
        for enemy in self.air_enemies:
            self._draw_air_enemy_shape(enemy)
        for power in self.air_powerups:
            self._draw_air_powerup(power)
        for particle in self.air_particles:
            alpha = max(0.2, particle["life"] / particle["max"])
            color = tuple(int(channel * alpha) for channel in particle["color"])
            pygame.draw.rect(
                self.screen, color,
                (int(particle["x"]), int(particle["y"]),
                 particle["size"], particle["size"]))
        player = self.air_player
        if player.get("invuln", 0) % 8 < 4:
            self._draw_air_ship(player["x"], player["y"])
        if player.get("shield"):
            pygame.draw.circle(
                self.screen, self.air_shield_color,
                (int(player["x"]), int(player["y"])), 27, 2)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            pygame.draw.circle(
                self.screen, (255, 255, 255),
                (int(player["x"]), int(player["y"])), 5)
            pygame.draw.circle(
                self.screen, (255, 80, 100),
                (int(player["x"]), int(player["y"])), 2)
        self._draw_air_hud()
        if self.air_story_message:
            self._draw_air_story_strip()
        if self.air_boss_phase_flash > 0:
            self._draw_air_phase_overlay()
        if self.state == self.AIR_END:
            self._draw_air_end()
        elif self.air_paused:
            draw_pause_overlay(self, AIR_PALETTE)

    def _draw_air_background(self):
        cfg = AIR_LEVELS[self.air_level]
        themes = {
            "coast": ((8, 35, 58), (35, 105, 130)),
            "storm": ((12, 18, 38), (75, 90, 120)),
            "night": ((7, 8, 28), (45, 55, 105)),
            "red": ((35, 8, 20), (120, 35, 45)),
            "fort": ((18, 25, 32), (85, 100, 110)),
            "static": ((12, 18, 25), (55, 125, 130)),
            "aurora": ((6, 24, 28), (45, 130, 105)),
            "horizon": ((30, 8, 20), (150, 55, 45)),
        }
        base, accent = themes[cfg["theme"]]
        pygame.draw.rect(self.screen, base, AIR_PLAY_RECT)
        for index in range(70):
            x = AIR_PLAY_RECT.left + (index * 97) % AIR_PLAY_RECT.width
            y = AIR_PLAY_RECT.top + (
                index * 53 + self.air_stage_tick * (1 + index % 3)) % AIR_PLAY_RECT.height
            pygame.draw.rect(self.screen, accent, (x, y, 2, 5 + index % 5))
        if cfg["theme"] in ("fort", "horizon"):
            for index in range(7):
                y = AIR_PLAY_RECT.top + 90 + index * 82
                pygame.draw.line(
                    self.screen, (*accent,), (AIR_PLAY_RECT.left, y),
                    (AIR_PLAY_RECT.right, y + 30), 1)

    def _draw_air_ship(self, x, y, scale=1.0):
        x, y = int(x), int(y)
        wing = int(18 * scale)
        nose = int(23 * scale)
        pygame.draw.polygon(
            self.screen, C.OUTLINE,
            [(x, y - nose - 3), (x - wing - 3, y + wing + 3),
             (x, y + 9), (x + wing + 3, y + wing + 3)])
        pygame.draw.polygon(
            self.screen, self.air_ship_color,
            [(x, y - nose), (x - wing, y + wing),
             (x, y + 7), (x + wing, y + wing)])
        flame = 7 + (self.anim_tick % 4) * 2
        pygame.draw.polygon(
            self.screen, self.air_engine_color,
            [(x - 5, y + 13), (x, y + 13 + flame), (x + 5, y + 13)])

    def _draw_air_enemy_shape(self, enemy, scale=1.0):
        x, y, radius = int(enemy["x"]), int(enemy["y"]), int(enemy["r"] * scale)
        color = AIR_ENEMY_COLORS.get(enemy["kind"], (235, 75, 115))
        if enemy.get("flash", 0):
            color = (255, 245, 225)
        if enemy["boss"]:
            pygame.draw.polygon(
                self.screen, C.OUTLINE,
                [(x, y + radius + 5), (x - radius - 5, y - radius // 2),
                 (x - radius // 2, y - radius), (x, y - radius // 2),
                 (x + radius // 2, y - radius), (x + radius + 5, y - radius // 2)])
            pygame.draw.polygon(
                self.screen, color,
                [(x, y + radius), (x - radius, y - radius // 2),
                 (x - radius // 2, y - radius), (x, y - radius // 2),
                 (x + radius // 2, y - radius), (x + radius, y - radius // 2)])
            pygame.draw.circle(self.screen, (255, 220, 120), (x, y), 9)
            if not enemy.get("weak", True):
                pygame.draw.circle(self.screen, (150, 180, 220), (x, y), radius + 8, 3)
        else:
            kind = enemy["kind"]
            if kind in ("bomber", "carrier", "commander"):
                pygame.draw.rect(
                    self.screen, C.OUTLINE,
                    (x - radius - 3, y - radius // 2 - 3,
                     radius * 2 + 6, radius + 6))
                pygame.draw.rect(
                    self.screen, color,
                    (x - radius, y - radius // 2, radius * 2, radius))
                pygame.draw.polygon(
                    self.screen, color,
                    [(x, y + radius), (x - radius, y), (x + radius, y)])
            else:
                pygame.draw.polygon(
                    self.screen, C.OUTLINE,
                    [(x, y + radius + 3), (x - radius - 3, y - radius // 2),
                     (x + radius + 3, y - radius // 2)])
                pygame.draw.polygon(
                    self.screen, color,
                    [(x, y + radius), (x - radius, y - radius // 2),
                     (x + radius, y - radius // 2)])
            if kind == "shield":
                pygame.draw.circle(self.screen, (125, 150, 255), (x, y), radius + 5, 2)

    def _draw_air_powerup(self, power):
        colors = {
            **AIR_WEAPON_COLORS, "repair": (100, 245, 125), "shield": (100, 220, 255)}
        color = colors[power["kind"]]
        x, y = int(power["x"]), int(power["y"])
        radius = 11 + int(math.sin(power["phase"]) * 2)
        pygame.draw.circle(self.screen, C.OUTLINE, (x, y), radius + 3)
        pygame.draw.circle(self.screen, color, (x, y), radius, 3)
        letter = {"cannon": "C", "spread": "S", "laser": "L",
                  "repair": "+", "shield": "D"}[power["kind"]]
        text = render_pixel_text(self.font_small, letter, color, scale=1)
        self.screen.blit(text, (x - text.get_width() // 2, y - text.get_height() // 2))

    def _draw_air_hud(self):
        cfg = AIR_LEVELS[self.air_level]
        left = pygame.Rect(24, 42, 286, 636)
        right = pygame.Rect(970, 42, 286, 636)
        for panel in (left, right):
            pygame.draw.rect(self.screen, C.OUTLINE, panel, 4)
            pygame.draw.rect(self.screen, AIR_PALETTE["panel"], panel.inflate(-8, -8))
            pygame.draw.rect(self.screen, AIR_PALETTE["accent"], panel.inflate(-18, -18), 2)
        self._draw_air_hud_text(
            f"CHAPTER {cfg['chapter']:02d}", left.x + 24, 72, AIR_PALETTE["accent_light"], 2)
        self._draw_air_hud_text(cfg["name"], left.x + 24, 105, AIR_PALETTE["text"], 2)
        self._draw_air_hud_text("HULL", left.x + 24, 160, AIR_PALETTE["muted"], 2)
        for index in range(5):
            rect = pygame.Rect(left.x + 24 + index * 45, 193, 34, 22)
            pygame.draw.rect(self.screen, C.OUTLINE, rect)
            pygame.draw.rect(
                self.screen, (90, 230, 145) if index < self.air_health else (38, 55, 62),
                rect.inflate(-4, -4))
        shield = "READY" if self.air_player.get("shield") else "NONE"
        self._draw_air_hud_text(
            f"SHIELD  {shield}", left.x + 24, 245,
            (100, 225, 255) if shield == "READY" else AIR_PALETTE["muted"], 2)
        self._draw_air_hud_text(
            f"COMBO  {self.air_combo:03d}", left.x + 24, 305, AIR_PALETTE["text"], 2)
        self._draw_air_hud_text(
            f"MULTI  x{self.air_multiplier:.1f}", left.x + 24, 340,
            AIR_WEAPON_COLORS["cannon"], 2)
        self._draw_air_hud_text(
            f"GRAZE  {self.air_grazes:04d}", left.x + 24, 375, AIR_PALETTE["text"], 2)
        self._draw_air_hud_text("OBJECTIVE", left.x + 24, 445, AIR_PALETTE["muted"], 2)
        objective = self._air_objective_text().replace("OBJECTIVE: ", "")
        self._draw_air_wrapped(objective, left.x + 24, 480, 235, AIR_PALETTE["text"])
        mission_percent = int(self._air_mission_completion() * 100)
        self._draw_air_bar(left.x + 24, 555, 230, 16, mission_percent / 100,
                           AIR_PALETTE["accent"])
        self._draw_air_hud_text(
            f"{mission_percent:03d}%", left.x + 110, 580, AIR_PALETTE["accent_light"], 2)

        self._draw_air_hud_text(
            f"SCORE {self.air_score:07d}", right.x + 22, 72, AIR_PALETTE["accent_light"], 2)
        self._draw_air_hud_text("WEAPONS", right.x + 22, 130, AIR_PALETTE["muted"], 2)
        for index, weapon in enumerate(("cannon", "spread", "laser")):
            active = weapon == self.air_loadout["active"]
            color = AIR_WEAPON_COLORS[weapon]
            label = f"{'>' if active else ' '} {weapon.upper():7s} L{self.air_loadout[weapon]}"
            self._draw_air_hud_text(label, right.x + 22, 170 + index * 42,
                                    color if active else AIR_PALETTE["text"], 2)
        self._draw_air_hud_text("MISSILE", right.x + 22, 320, AIR_PALETTE["muted"], 2)
        self._draw_air_bar(
            right.x + 22, 355, 235, 18, self.air_missile_charge / 100,
            (255, 210, 80) if self.air_missile_ready else AIR_PALETTE["accent"])
        missile_text = "SPACE // READY" if self.air_missile_ready else f"CHARGE {self.air_missile_charge:03d}%"
        self._draw_air_hud_text(
            missile_text, right.x + 22, 385,
            (255, 225, 100) if self.air_missile_ready else AIR_PALETTE["text"], 2)
        rank, score = self._calculate_air_rating()
        self._draw_air_hud_text("LIVE RATING", right.x + 22, 455, AIR_PALETTE["muted"], 2)
        rank_color = {"S": (255, 220, 80), "A": (110, 245, 210),
                      "B": (110, 185, 255), "C": (190, 150, 160)}[rank]
        rank_text = render_pixel_text(self.font_menu_title, rank, rank_color, scale=4)
        self.screen.blit(rank_text, (right.centerx - rank_text.get_width() // 2, 495))
        self._draw_air_hud_text(
            f"INDEX {score:03d}", right.x + 82, 595, AIR_PALETTE["text"], 2)
        if cfg["boss"] and self.air_enemies:
            boss = self.air_enemies[0]
            self._draw_air_bar(
                AIR_PLAY_RECT.x + 50, AIR_PLAY_RECT.y + 18, AIR_PLAY_RECT.width - 100,
                14, boss["hp"] / max(1, boss["max_hp"]), (255, 70, 115))
            name = render_pixel_text(
                self.font_small, f"{boss['name']} // PHASE {self.air_boss_phase}",
                (255, 190, 205), scale=2)
            self.screen.blit(name, (AIR_PLAY_RECT.centerx - name.get_width() // 2, 65))

    def _draw_air_hud_text(self, text, x, y, color, scale=1):
        surface = render_pixel_text(self.font_small, text, color, scale=scale)
        self.screen.blit(surface, (x, y))

    def _draw_air_wrapped(self, text, x, y, width, color):
        words = text.split()
        lines = []
        line = ""
        for word in words:
            candidate = f"{line} {word}".strip()
            surface = render_pixel_text(self.font_small, candidate, color, scale=2)
            if surface.get_width() > width and line:
                lines.append(line)
                line = word
            else:
                line = candidate
        lines.append(line)
        for index, value in enumerate(lines[:2]):
            surface = render_pixel_text(self.font_small, value, color, scale=2)
            self.screen.blit(surface, (x, y + index * 27))

    def _draw_air_bar(self, x, y, width, height, value, color):
        pygame.draw.rect(self.screen, C.OUTLINE, (x, y, width, height))
        pygame.draw.rect(self.screen, (25, 38, 45), (x + 3, y + 3, width - 6, height - 6))
        fill = int((width - 6) * max(0.0, min(1.0, value)))
        if fill:
            pygame.draw.rect(self.screen, color, (x + 3, y + 3, fill, height - 6))

    def _draw_air_story_strip(self):
        rect = pygame.Rect(AIR_PLAY_RECT.x + 20, AIR_PLAY_RECT.bottom - 78,
                           AIR_PLAY_RECT.width - 40, 52)
        shade = pygame.Surface(rect.size, pygame.SRCALPHA)
        shade.fill((4, 12, 25, 215))
        self.screen.blit(shade, rect)
        pygame.draw.rect(self.screen, AIR_PALETTE["accent"], rect, 2)
        label = render_pixel_text(
            self.font_small, "TACTICAL LINK", AIR_PALETTE["muted"], scale=1)
        text = render_pixel_text(
            self.font_small, self.air_story_message, AIR_PALETTE["text"], scale=1)
        self.screen.blit(label, (rect.x + 12, rect.y + 7))
        self.screen.blit(text, (rect.x + 12, rect.y + 27))

    def _draw_air_phase_overlay(self):
        alpha = int(160 * self.air_boss_phase_flash / 100)
        overlay = pygame.Surface(AIR_PLAY_RECT.size, pygame.SRCALPHA)
        overlay.fill((255, 30, 80, alpha // 3))
        self.screen.blit(overlay, AIR_PLAY_RECT.topleft)
        text = render_pixel_text(
            self.font_menu_title, f"PHASE {self.air_boss_phase}",
            (255, 225, 230), scale=3)
        self.screen.blit(text, (AIR_PLAY_RECT.centerx - text.get_width() // 2,
                                AIR_PLAY_RECT.centery - text.get_height() // 2))

    def _draw_air_end(self):
        shade = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 210))
        self.screen.blit(shade, (0, 0))
        panel = pygame.Rect(240, 110, 800, 510)
        pygame.draw.rect(self.screen, C.OUTLINE, panel, 6)
        pygame.draw.rect(self.screen, AIR_PALETTE["panel"], panel.inflate(-12, -12))
        pygame.draw.rect(self.screen, AIR_PALETTE["accent"], panel.inflate(-28, -28), 2)
        title = render_pixel_text(
            self.font_menu_title, self.air_result,
            AIR_PALETTE["accent_light"] if self.air_health > 0 else (255, 105, 120), scale=3)
        self.screen.blit(title, (panel.centerx - title.get_width() // 2, 145))
        rank_color = {"S": (255, 220, 80), "A": (110, 245, 210),
                      "B": (110, 185, 255), "C": (190, 150, 160)}[self.air_rank]
        rank = render_pixel_text(self.font_menu_title, self.air_rank, rank_color, scale=5)
        self.screen.blit(rank, (panel.centerx - rank.get_width() // 2, 220))
        details = [
            f"SCORE {self.air_score:07d}",
            f"DESTROYED {self.air_destroyed:03d} / {self.air_spawned:03d}",
            f"GRAZES {self.air_grazes:04d}   HULL {max(0, self.air_health)} / 5",
        ]
        for index, line in enumerate(details):
            text = render_pixel_text(self.font_small, line, AIR_PALETTE["text"], scale=2)
            self.screen.blit(text, (panel.centerx - text.get_width() // 2, 330 + index * 34))
        if self.air_challenge_unlocked_notice:
            unlocked = render_pixel_text(
                self.font_small, "CHALLENGE CAMPAIGN + BOSS RUSH UNLOCKED",
                (255, 220, 90), scale=1 if is_chinese() else 2)
            self.screen.blit(unlocked, (panel.centerx - unlocked.get_width() // 2, 455))
        action = "ENTER  CONTINUE" if self.air_result in ("MISSION CLEAR", "BOSS RUSH CLEAR") else "ENTER / R  RETRY"
        hint = render_pixel_text(
            self.font_small, f"{action}     ESC  MENU", AIR_PALETTE["muted"], scale=1 if is_chinese() else 2)
        self.screen.blit(hint, (panel.centerx - hint.get_width() // 2, 508))
        mouse = self._logical_mouse_pos()
        for button in self._air_end_buttons():
            draw_arcade_button(
                self, button, AIR_PALETTE,
                button["rect"].collidepoint(mouse),
                self.air_pressed == button["action"],
            )

    def _archive_chapter_unlocked(self, chapter_num):
        """Chapter N is readable once the campaign has reached it."""
        return chapter_num <= self._air_progress().get("completed", 0) // 2 + 1

    def _open_archive_story(self, index):
        """Open archive entry ``index`` (0 is the prologue) if it is unlocked.

        Shared by the keyboard and mouse paths so both honour the same gate.
        """
        if index == 0:
            self.air_story_lines = list(AIR_PROLOGUE)
            self.air_story_source = "prologue"
        elif 1 <= index <= len(AIR_CHAPTER_STORIES) and self._archive_chapter_unlocked(index):
            self.air_story_lines = list(AIR_CHAPTER_STORIES[index])
            self.air_story_source = f"chapter_{index}"
        else:
            return False
        self.air_story_page = 0
        return True

    def _handle_air_story_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.air_story_source == "archive_index":
                # The archive is a reader, not the level gate, so it is handled
                # before the branch below — otherwise ENTER would leave the
                # archive instead of opening the highlighted chapter.
                if event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                    direction = -1 if event.key in (pygame.K_UP, pygame.K_w) else 1
                    max_stories = 1 + len(AIR_CHAPTER_STORIES)
                    self.air_story_page = (self.air_story_page + direction) % max_stories
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._open_archive_story(self.air_story_page)
                elif event.key == pygame.K_ESCAPE:
                    self.state = self.AIR_MENU
                return
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                # ESC deliberately matches ENTER: both dismiss the story and
                # start the level it was gating.
                if self._pending_brief_level is not None:
                    level = self._pending_brief_level
                    self._pending_brief_level = None
                    self._prepare_air_level(level)
                else:
                    self.state = self.AIR_MENU
                return
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                lines_per_page = 4
                max_page = max(0, (len(self.air_story_lines) - 1) // lines_per_page)
                self.air_story_page = min(self.air_story_page + 1, max_page)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.air_story_page = max(0, self.air_story_page - 1)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.air_story_source == "archive_index":
                panel = pygame.Rect(100, 50, WINDOW_W - 200, WINDOW_H - 100)
                for i in range(1 + len(AIR_CHAPTER_STORIES)):
                    rect = pygame.Rect(panel.x + 40, panel.y + 70 + i * 45, panel.width - 80, 36)
                    if rect.collidepoint(event.pos):
                        self._open_archive_story(i)
                        return
            else:
                self._handle_air_story_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    def _draw_air_story(self):
        self.screen.fill((6, 14, 32))
        panel = pygame.Rect(100, 50, WINDOW_W - 200, WINDOW_H - 100)
        pygame.draw.rect(self.screen, C.OUTLINE, panel, 4)
        pygame.draw.rect(self.screen, (10, 22, 44), panel.inflate(-8, -8))
        pygame.draw.rect(self.screen, C.AIR_ACCENT, panel.inflate(-16, -16), 2)

        if self.air_story_source == "archive_index":
            title = render_pixel_text(self.font_status, translate("STORY ARCHIVE"), C.AIR_ACCENT_LIGHT, scale=3)
            self.screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 18))
            all_ids = ["prologue"] + [i for i in range(1, 9)]
            names = ["PROLOGUE"] + [f"CHAPTER {i}" for i in range(1, 9)]
            completed_ch = self._air_progress().get("completed", 0) // 2 + 1
            for i, ch_id in enumerate(all_ids):
                rect = pygame.Rect(panel.x + 40, panel.y + 70 + i * 45, panel.width - 80, 36)
                unlocked = (i == 0) or (1 <= i <= 8 and i <= completed_ch)
                sel = self.air_story_page == i
                fill = (15, 35, 60) if sel else (8, 18, 35)
                border = C.AIR_ACCENT_LIGHT if sel else (C.AIR_MUTED if unlocked else (30, 30, 45))
                pygame.draw.rect(self.screen, C.OUTLINE, rect)
                pygame.draw.rect(self.screen, fill, rect.inflate(-2, -2))
                pygame.draw.rect(self.screen, border, rect.inflate(-6, -6), 1)
                label = translate(names[i]) if unlocked else "??? (LOCKED)"
                story_font = get_chinese_font(12)
                txt = render_pixel_text(story_font, label, C.AIR_ACCENT_LIGHT if unlocked else C.AIR_MUTED, scale=1)
                self.screen.blit(txt, (rect.x + 16, rect.centery - txt.get_height() // 2))
            hint = render_pixel_text(story_font, translate("UP/DOWN SELECT   ENTER READ   ESC BACK"), C.AIR_MUTED, scale=1)
            self.screen.blit(hint, (panel.centerx - hint.get_width() // 2, panel.bottom - 36))
            return

        # Story text display
        lines_per_page = 4
        start = self.air_story_page * lines_per_page
        page_lines = self.air_story_lines[start:start + lines_per_page]
        max_page = max(0, (len(self.air_story_lines) - 1) // lines_per_page)

        # Source label
        if self.air_story_source == "prologue":
            source_label = translate("PROLOGUE")
        else:
            ch_num = self.air_story_source.replace("chapter_", "")
            chapter_names = {1:"COAST WATCH",2:"IRON CLOUD",3:"NIGHT VECTOR",4:"RED SQUALL",5:"SKY FORT",6:"DEEP STATIC",7:"BLACK AURORA",8:"LAST HORIZON"}
            ch_name = chapter_names.get(int(ch_num), f"CHAPTER {ch_num}")
            source_label = f"CHAPTER {ch_num}: {translate(ch_name) if ch_name else ''}"
        src = render_pixel_text(self.font_status, source_label, C.AIR_ACCENT_LIGHT, scale=2)
        self.screen.blit(src, (panel.centerx - src.get_width() // 2, panel.y + 18))

        story_font = get_chinese_font(14)
        for li, line in enumerate(page_lines):
            y = panel.y + 70 + li * 90
            txt = render_pixel_text(story_font, line, C.AIR_TEXT, scale=1)
            self.screen.blit(txt, (panel.x + 50, y))

        # Page indicator
        page_text = f"PAGE {self.air_story_page + 1} / {max_page + 1}"
        pg = render_pixel_text(story_font, page_text, C.AIR_MUTED, scale=1)
        self.screen.blit(pg, (panel.right - pg.get_width() - 28, panel.bottom - 34))

        nav = render_pixel_text(story_font, "A/D  PAGE   ENTER  CLOSE", C.AIR_MUTED, scale=1)
        self.screen.blit(nav, (panel.x + 24, panel.bottom - 34))

    def _handle_air_skins_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._start_transition(self.AIR_MENU, "fade", frames=28)
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            skins = self._air_progress().get("skins_unlocked", ["default"])
            all_skins = ["default", "crimson", "azure", "gold"]
            for i, skin_id in enumerate(all_skins):
                col, row = i % 2, i // 2
                card = pygame.Rect(180 + col * 470, 190 + row * 240, 430, 210)
                if card.collidepoint(event.pos) and skin_id in skins:
                    self.air_skin = skin_id
                    self._apply_air_preferences()
                    self._save_now()
                    return

    def _draw_air_skins(self):
        self.screen.fill(C.AIR_BG)
        panel = pygame.Rect(80, 60, WINDOW_W - 160, WINDOW_H - 120)
        pygame.draw.rect(self.screen, C.AIR_PANEL_DARK, panel)
        pygame.draw.rect(self.screen, C.OUTLINE, panel, 3)
        pygame.draw.rect(self.screen, C.AIR_ACCENT, panel.inflate(-10, -10), 2)

        title = render_pixel_text(self.font_status, translate("SHIP SKINS"), C.AIR_ACCENT_LIGHT, scale=3)
        self.screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 14))

        all_skins = ["default", "crimson", "azure", "gold"]
        skins = self._air_progress().get("skins_unlocked", ["default"])
        names = {"default": "DEFAULT", "crimson": "CRIMSON", "azure": "AZURE", "gold": "GOLD"}
        ship_colors = {
            "default": C.AIR_SKIN_DEFAULT_SHIP, "crimson": C.AIR_SKIN_CRIMSON_SHIP,
            "azure": C.AIR_SKIN_AZURE_SHIP, "gold": C.AIR_SKIN_GOLD_SHIP,
        }
        req_achievements = {
            "crimson": "GUNLINE", "azure": "PERFECT VECTOR", "gold": "WARDEN PRIME",
        }

        for i, skin_id in enumerate(all_skins):
            col, row = i % 2, i // 2
            card = pygame.Rect(180 + col * 470, 190 + row * 240, 430, 210)
            unlocked = skin_id in skins
            selected = self.air_skin == skin_id

            # Card background
            pygame.draw.rect(self.screen, C.OUTLINE, card)
            if selected:
                pygame.draw.rect(self.screen, (20, 55, 85), card.inflate(-4, -4))
                pygame.draw.rect(self.screen, C.GOLD_LIGHT, card.inflate(-8, -8), 2)
            else:
                pygame.draw.rect(self.screen, C.AIR_PANEL if unlocked else (10, 20, 35), card.inflate(-4, -4))

            # Ship preview — large, centered in the upper portion of the card
            saved_ship = self.air_ship_color
            saved_engine = self.air_engine_color
            if unlocked:
                self.air_ship_color = ship_colors[skin_id]
                self.air_engine_color = {
                    "default": C.AIR_SKIN_DEFAULT_ENGINE, "crimson": C.AIR_SKIN_CRIMSON_ENGINE,
                    "azure": C.AIR_SKIN_AZURE_ENGINE, "gold": C.AIR_SKIN_GOLD_ENGINE,
                }[skin_id]
            else:
                self.air_ship_color = (50, 55, 70)
                self.air_engine_color = (35, 38, 48)
            self._draw_air_ship(card.centerx, card.y + 65, scale=1.3)
            # Shield ring for unlocked, selected
            if unlocked:
                shield_c = {
                    "default": C.AIR_SKIN_DEFAULT_SHIELD, "crimson": C.AIR_SKIN_CRIMSON_SHIELD,
                    "azure": C.AIR_SKIN_AZURE_SHIELD, "gold": C.AIR_SKIN_GOLD_SHIELD,
                }[skin_id]
                pygame.draw.circle(self.screen, shield_c, (card.centerx, card.y + 65), 28, 1)
            self.air_ship_color = saved_ship
            self.air_engine_color = saved_engine

            # Skin name
            display_name = translate(names[skin_id]) if unlocked else "???"
            name_color = ship_colors[skin_id] if unlocked else C.AIR_MUTED
            txt = render_pixel_text(self.font_status, display_name, name_color, scale=2)
            self.screen.blit(txt, (card.x + 24, card.y + 108))

            # Selected / locked indicator
            if selected:
                sel = render_pixel_text(self.font_small, translate("SELECTED"), C.GOLD_LIGHT, scale=1)
                self.screen.blit(sel, (card.right - sel.get_width() - 20, card.y + 112))
            elif not unlocked:
                req_name = req_achievements.get(skin_id, "")
                req_zh = translate(req_name) if req_name else req_name
                lock_line = f"{translate('REQUIRES')}: {req_zh}"
                hint = render_pixel_text(self.font_small, lock_line, C.AIR_MUTED, scale=1)
                self.screen.blit(hint, (card.x + 24, card.y + 145))
                # Small lock icon (pixel-art)
                lx, ly = card.x + 24, card.y + 168
                for dx, dy in [(1,0),(2,0),(3,0),(0,1),(4,1),(0,2),(1,2),(2,2),(3,2),(4,2),(2,3)]:
                    pygame.draw.rect(self.screen, C.AIR_MUTED, (lx + dx * 3, ly + dy * 3, 3, 3))

            # Skin color swatch (bottom-right)
            if unlocked:
                swatch = pygame.Rect(card.right - 36, card.bottom - 28, 20, 12)
                pygame.draw.rect(self.screen, C.OUTLINE, swatch)
                pygame.draw.rect(self.screen, ship_colors[skin_id], swatch.inflate(-2, -2))
