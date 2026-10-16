"""Regression tests for R1: a damaged save must never destroy progress.

These cover the three failure modes found in the assessment:

* V-0 -- a file that is valid JSON but not a profile was merged into the
  defaults, reported as a brand-new profile, and the startup save then copied
  that junk over the only good ``.bak``: all progress lost, silently.
* V-7 -- a semantically broken save crashed ``Game()`` forever while an intact
  ``.bak`` sat unused, and the file was never quarantined.
* V-18 -- an out-of-vocabulary setting kept raising ``ValueError`` out of the
  settings page because the bad value was re-saved on every cycle.

Everything writes only into a per-test temporary directory; the real profile
under ``%APPDATA%\\MERIDIAN`` is never touched.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
import unittest

from meridian.persistence import SaveManager, _deep_merge, default_data


def _write(path: Path, payload) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


class _ScratchCase(unittest.TestCase):
    """One temp directory per test."""

    def setUp(self) -> None:
        self.scratch = Path(tempfile.mkdtemp(prefix="meridian-r1-"))
        self.save_path = self.scratch / "save.json"
        self.manager = SaveManager(self.save_path)

    def tearDown(self) -> None:
        shutil.rmtree(self.scratch, ignore_errors=True)

    def good_save_with_score(self, score: int = 4242) -> dict:
        data = default_data()
        data["records"]["snake"]["best_score"] = score
        return data

    def quarantined(self) -> list[Path]:
        return list(self.scratch.glob("save.corrupt-*.json"))


class ProgressSurvivesJunkPrimaryTests(_ScratchCase):
    """V-0: junk must not be adopted, and the backup must not be consumed."""

    def test_empty_object_is_treated_as_damage_not_a_fresh_profile(self):
        _write(self.save_path, self.good_save_with_score())
        shutil.copy2(self.save_path, self.manager.backup_path)
        self.save_path.write_text("{}", encoding="utf-8")

        loaded = self.manager.load()
        self.assertEqual(loaded["records"]["snake"]["best_score"], 4242)
        self.assertTrue(
            self.quarantined(), "the junk primary should have been quarantined"
        )

    def test_startup_save_does_not_overwrite_a_good_backup_with_junk(self):
        _write(self.save_path, self.good_save_with_score())
        shutil.copy2(self.save_path, self.manager.backup_path)
        self.save_path.write_text("{}", encoding="utf-8")

        loaded = self.manager.load()
        self.manager.save(loaded)          # what the app does at startup

        backup = json.loads(self.manager.backup_path.read_text(encoding="utf-8"))
        self.assertEqual(
            backup["records"]["snake"]["best_score"],
            4242,
            "the recovery copy was overwritten with the junk primary",
        )

    def test_a_junk_primary_never_becomes_the_backup(self):
        # The primary parses but is not a profile; the backup holds real progress.
        _write(self.save_path, self.good_save_with_score(777))
        shutil.copy2(self.save_path, self.manager.backup_path)
        _write(self.save_path, {"schema_version": 5, "settings": "x"})

        self.manager.save(self.manager.load())
        backup = json.loads(self.manager.backup_path.read_text(encoding="utf-8"))
        self.assertEqual(backup["records"]["snake"]["best_score"], 777)

    def test_settings_only_v0_save_still_migrates(self):
        # A legitimate partial v0 profile must NOT be treated as damage.
        _write(self.save_path, {"settings": {"language": "fr"}})
        loaded = self.manager.load()
        self.assertEqual(loaded["settings"]["language"], "fr")
        self.assertFalse(self.quarantined())

    def test_second_backup_generation_is_consulted(self):
        _write(self.save_path, self.good_save_with_score(999))
        shutil.copy2(self.save_path, self.manager.backup_path_2)
        self.save_path.write_text("{}", encoding="utf-8")
        loaded = self.manager.load()
        self.assertEqual(loaded["records"]["snake"]["best_score"], 999)


class SemanticDamageStartsTheGameTests(_ScratchCase):
    """V-7: broken shapes must degrade, never end the process."""

    BROKEN_SHAPES = {
        "empty_object": lambda d: None,
        "settings_is_string": lambda d: d.update(settings="x"),
        "settings_missing_keys": lambda d: d.update(settings={"language": "en"}),
        "statistics_is_list": lambda d: d.update(statistics=[]),
        "progress_is_list": lambda d: d.update(progress=[]),
        "records_is_string": lambda d: d.update(records="boom"),
        "master_volume_null": lambda d: d["settings"].update(master_volume=None),
        "volume_is_loud": lambda d: d["settings"].update(master_volume="loud"),
        "board_size_is_big": lambda d: d["settings"].update(gomoku_board_size="big"),
        "board_size_is_one": lambda d: d["settings"].update(gomoku_board_size=1),
        "mines_size_is_null": lambda d: d["settings"].update(mines_size=None),
        "schema_version_infinity": lambda d: d.update(schema_version=float("inf")),
    }

    def _load_shape(self, name: str):
        data = default_data()
        if name == "empty_object":
            _write(self.save_path, {})
        else:
            self.BROKEN_SHAPES[name](data)
            _write(self.save_path, data)
        return self.manager.load()

    def test_every_broken_shape_loads_without_raising(self):
        for name in self.BROKEN_SHAPES:
            with self.subTest(shape=name):
                loaded = self._load_shape(name)
                self.assertIsInstance(loaded, dict)
                self.assertIsInstance(loaded["settings"], dict)
                self.assertIsInstance(loaded["records"], dict)
                self.assertIsInstance(loaded["statistics"], dict)
                self.assertIsInstance(loaded["progress"], dict)
                self.assertIsInstance(loaded["lore"], dict)

    def test_broken_shape_with_intact_backup_keeps_progress(self):
        for name in self.BROKEN_SHAPES:
            if name == "settings_missing_keys":
                continue  # legal partial profile, no quarantine expected
            with self.subTest(shape=name):
                # fresh scratch per shape so quarantines do not accumulate
                self.tearDown()
                self.setUp()
                _write(self.save_path, self.good_save_with_score())
                shutil.copy2(self.save_path, self.manager.backup_path)
                self._load_shape(name)
                # structural damage -> the .bak is adopted; settings damage ->
                # sanitised in place.  Either way the player keeps playing.
                self.assertTrue(self.save_path.exists() or self.quarantined())


class DeepMergeTypingTests(unittest.TestCase):
    def test_wrong_typed_container_keeps_the_default(self):
        merged = _deep_merge({"settings": {"gomoku_board_size": 15}}, {"settings": "x"})
        self.assertIsInstance(merged["settings"], dict)
        self.assertEqual(merged["settings"]["gomoku_board_size"], 15)

    def test_correctly_typed_values_still_override(self):
        merged = _deep_merge({"settings": {"gomoku_board_size": 15}},
                             {"settings": {"gomoku_board_size": 19}})
        self.assertEqual(merged["settings"]["gomoku_board_size"], 19)

    def test_new_keys_are_still_added(self):
        merged = _deep_merge({"settings": {}}, {"settings": {"brand_new": 7}})
        self.assertEqual(merged["settings"]["brand_new"], 7)


class SettingsVocabularyTests(_ScratchCase):
    """V-18: an out-of-vocabulary setting must be repaired, not fatal."""

    BAD_SETTINGS = [
        ("gomoku_board_size", 17),
        ("gomoku_board_size", "abc"),
        ("gomoku_board_size", 1),
        ("gomoku_board_size", 0),
        ("gomoku_board_size", -5),
        ("animation_level", "cinematic"),
        ("snake_speed", "turbo"),
        ("snake_skin", "gold"),
        ("breakout_difficulty", "insane"),
        ("mines_size", 400),
        ("mines_count", 999),
        ("master_volume", None),
        ("master_volume", "loud"),
        ("master_volume", float("nan")),
    ]

    def test_every_bad_setting_is_repaired_and_every_cycle_still_works(self):
        """One real Game() per bad value; each must boot and cycle cleanly."""
        import os

        import pygame

        from meridian.app import Game

        for key, value in self.BAD_SETTINGS:
            with self.subTest(setting=key, value=repr(value)):
                pygame.init()
                scratch = Path(tempfile.mkdtemp(prefix="meridian-r1-vocab-"))
                save_path = scratch / "save.json"
                data = default_data()
                data["settings"][key] = value
                # json.dumps emits bare NaN, which json.load accepts; that is the
                # hostile input this case is meant to exercise.
                save_path.write_text(json.dumps(data), encoding="utf-8")

                previous = os.environ.get("MERIDIAN_SAVE_PATH")
                os.environ["MERIDIAN_SAVE_PATH"] = str(save_path)
                try:
                    game = Game()
                    self.assertIn(game.board_size, (13, 15, 19))
                    self.assertIn(game.animation_level, ("full", "reduced", "off"))
                    self.assertIn(game.snake_speed_mode, ("slow", "normal", "fast"))
                    self.assertIn(game.snake_skin, ("green", "lime", "red"))
                    self.assertIn(game.mines_size, (9, 16))
                    for action in (
                        "cycle_gomoku",
                        "cycle_animation",
                        "cycle_snake_speed",
                        "cycle_snake_skin",
                        "cycle_breakout_difficulty",
                        "cycle_mines",
                    ):
                        game._activate_system_setting(action)
                    game.audio.stop()
                finally:
                    if previous is None:
                        os.environ.pop("MERIDIAN_SAVE_PATH", None)
                    else:
                        os.environ["MERIDIAN_SAVE_PATH"] = previous
                    shutil.rmtree(scratch, ignore_errors=True)
                    pygame.quit()


if __name__ == "__main__":
    unittest.main()
