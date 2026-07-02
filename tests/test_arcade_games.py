import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


import pygame

from meridian import Game
from meridian.arcade_levels import (
    AIR_CHAPTERS, AIR_ENEMY_TYPES, AIR_LEVELS,
)


class _Keys(dict):
    def __getitem__(self, key):
        return self.get(key, False)


class AirRaidReworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.temp = tempfile.TemporaryDirectory()
        cls.previous_save = os.environ.get("MERIDIAN_SAVE_PATH")
        os.environ["MERIDIAN_SAVE_PATH"] = str(Path(cls.temp.name) / "save.json")

    @classmethod
    def tearDownClass(cls):
        if cls.previous_save is None:
            os.environ.pop("MERIDIAN_SAVE_PATH", None)
        else:
            os.environ["MERIDIAN_SAVE_PATH"] = cls.previous_save
        cls.temp.cleanup()

    def make_game(self, level=0):
        game = Game()
        game._start_air_level(level)
        game._begin_air_combat()
        return game

    def test_campaign_has_eight_chapters_and_sixteen_alternating_stages(self):
        self.assertEqual(len(AIR_CHAPTERS), 8)
        self.assertEqual(len(AIR_LEVELS), 16)
        self.assertEqual(len(AIR_ENEMY_TYPES), 8)
        for index, stage in enumerate(AIR_LEVELS):
            self.assertEqual(stage["boss"], bool(index % 2))
            self.assertEqual(stage["chapter"], index // 2 + 1)
        self.assertTrue(all(len(stage["patterns"]) == 3 for stage in AIR_LEVELS[1::2]))

    def test_stage_starts_with_brief_and_standard_loadout(self):
        game = Game()
        game._start_air_level(10)
        self.assertEqual(game.state, game.AIR_BRIEF)
        game._begin_air_combat()
        self.assertEqual(game.state, game.AIR_PLAYING)
        self.assertEqual(game.air_health, 5)
        self.assertGreaterEqual(game.air_loadout["cannon"], 1)

    def test_shield_absorbs_hit_then_hull_takes_damage_and_knockback(self):
        game = self.make_game()
        game.air_player["invuln"] = 0
        game.air_player["shield"] = 1
        game._air_player_hit(1, game.air_player["x"] - 10)
        self.assertEqual(game.air_health, 5)
        self.assertEqual(game.air_player["shield"], 0)
        game.air_player["invuln"] = 0
        game._air_player_hit(1, game.air_player["x"] - 10)
        self.assertEqual(game.air_health, 4)
        self.assertGreater(game.air_player["vx"], 0)

    def test_weapon_cores_switch_and_upgrade_three_routes(self):
        game = self.make_game()
        for weapon in ("cannon", "spread", "laser"):
            before = game.air_loadout[weapon]
            game._collect_air_powerup({"kind": weapon, "x": 0, "y": 0})
            self.assertEqual(game.air_loadout["active"], weapon)
            self.assertEqual(game.air_loadout[weapon], min(5, before + 1))

    def test_standard_enemy_motion_is_slower_than_challenge(self):
        standard = self.make_game()
        standard._spawn_air_enemy("striker")
        challenge = self.make_game()
        challenge.air_mode = "challenge"
        challenge._spawn_air_enemy("striker")
        self.assertLess(
            abs(standard.air_enemies[-1]["vy"]),
            abs(challenge.air_enemies[-1]["vy"]),
        )

        standard._start_air_level(1)
        standard._begin_air_combat()
        challenge._start_air_level(1, mode="challenge")
        challenge._begin_air_combat()
        self.assertLess(
            abs(standard.air_enemies[0]["vx"]),
            abs(challenge.air_enemies[0]["vx"]),
        )

    def test_regular_enemy_survives_real_update_and_collision_paths(self):
        game = self.make_game()
        game._spawn_air_enemy("scout")
        enemy = game.air_enemies[-1]
        self.assertEqual(enemy["r"], AIR_ENEMY_TYPES["scout"]["radius"])
        for _ in range(5):
            game._update_air_enemy(enemy)
            game._update_air_projectiles()

    def test_retry_restores_entry_loadout(self):
        game = self.make_game(4)
        entry = dict(game.air_entry_snapshot["loadout"])
        game.air_loadout["laser"] = 5
        game._retry_air_level()
        self.assertEqual(game.air_loadout, entry)
        self.assertEqual(game.air_health, 5)

    def test_charged_missile_locks_up_to_eight_targets(self):
        game = self.make_game()
        game.air_enemies.clear()
        for index in range(10):
            game._spawn_air_enemy("scout", index)
        game.air_missile_ready = True
        game.air_missile_charge = 100
        game._launch_air_missile()
        self.assertEqual(len(game.air_missiles), 8)
        self.assertFalse(game.air_missile_ready)
        self.assertEqual(game.air_missile_charge, 0)

    def test_focus_graze_counts_each_enemy_bullet_once(self):
        game = self.make_game()
        game.air_player["invuln"] = 0
        game.air_enemy_bullets = [{
            "id": 1, "x": game.air_player["x"] + 15, "y": game.air_player["y"],
            "vx": 0, "vy": 0, "r": 4, "graze": False, "warning": False, "life": 20,
        }]
        keys = _Keys({pygame.K_LSHIFT: True})
        with patch("meridian.air_raid.pygame.key.get_pressed", return_value=keys):
            game._update_air_projectiles()
            game._update_air_projectiles()
        self.assertEqual(game.air_grazes, 1)

    def test_boss_switches_at_sixty_seven_and_thirty_four_percent(self):
        game = self.make_game(1)
        boss = game.air_enemies[0]
        boss["hp"] = int(boss["max_hp"] * .66)
        game._update_air_enemy(boss)
        self.assertEqual(game.air_boss_phase, 2)
        boss["hp"] = int(boss["max_hp"] * .33)
        game.air_boss_phase_flash = 0
        game._update_air_enemy(boss)
        self.assertEqual(game.air_boss_phase, 3)

    def test_rating_thresholds_and_challenge_shift(self):
        game = self.make_game()
        game.air_score = 999999
        game.air_destroyed = 30
        game.air_spawned = 30
        game.air_mission_value = game.air_mission_target
        game.air_health = 5
        game.air_mode = "standard"
        self.assertEqual(game._calculate_air_rating()[0], "S")
        game.air_mode = "challenge"
        self.assertEqual(game._calculate_air_rating()[0], "S")

    def test_standard_completion_unlocks_challenge_modes(self):
        game = self.make_game(15)
        game.air_campaign_active = True
        game.air_mode = "standard"
        game.air_enemies.clear()
        game._finish_air(True)
        progress = game._air_progress()
        self.assertTrue(progress["challenge_unlocked"])
        self.assertTrue(progress["campaign_complete"])

    def test_boss_rush_uses_supply_choice_between_bosses(self):
        game = self.make_game(1)
        game.air_mode = "boss_rush"
        game.air_boss_rush_index = 0
        game.air_health = 2
        game._complete_air_boss_rush_stage()
        self.assertEqual(game.state, game.AIR_SUPPLY)
        self.assertEqual(game.air_boss_rush_health, 3)
        before = game.air_loadout["spread"]
        game._choose_air_supply("spread")
        game._begin_air_combat()
        self.assertEqual(game.air_loadout["spread"], min(5, before + 1))
        self.assertEqual(game.air_health, 3)
        self.assertEqual(game.state, game.AIR_PLAYING)

    def test_menu_cinematic_and_archive_do_not_mutate_progress(self):
        game = Game()
        before = repr(game.save_data["progress"]["air"])
        game.state = game.AIR_MENU
        for _ in range(400):
            game._update_air_raid()
        game._draw_air_menu()
        game.state = game.AIR_ARCHIVE
        game._draw_air_archive()
        self.assertEqual(repr(game.save_data["progress"]["air"]), before)

    def test_all_air_pages_draw_without_errors(self):
        game = Game()
        game.transition_active = False
        game._start_air_level(0)
        for state in (
            game.AIR_MENU, game.AIR_SELECT, game.AIR_CONTROLS,
            game.AIR_BRIEF, game.AIR_ARCHIVE, game.AIR_SUPPLY,
        ):
            game.state = state
            game.draw()
        game._begin_air_combat()
        game.draw()
        game._finish_air(False)
        game.draw()


if __name__ == "__main__":
    unittest.main()
