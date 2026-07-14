"""Unit tests for the versioned save system.

Covers: default data structure, schema migration across every known version,
atomic-write protocol, crash recovery, and destructive reset helpers.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import unittest
import uuid

from meridian.persistence import (
    SCHEMA_VERSION,
    SaveManager,
    default_data,
    default_progress,
    default_records,
    default_settings,
    default_statistics,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _fresh_save_root() -> Path:
    return Path(os.environ.get("MERIDIAN_TEST_SAVE_ROOT", Path.cwd()))


# ---------------------------------------------------------------------------
# Default data
# ---------------------------------------------------------------------------

class DefaultDataTests(unittest.TestCase):
    def test_schema_version_matches_constant(self):
        data = default_data()
        self.assertEqual(data["schema_version"], SCHEMA_VERSION)

    def test_default_data_has_all_top_level_keys(self):
        data = default_data()
        for key in ("schema_version", "settings", "records", "statistics",
                     "achievements", "progress", "lore"):
            self.assertIn(key, data)

    def test_progress_covers_all_eight_games(self):
        progress = default_progress()
        for game_id in ("gomoku", "snake", "breakout", "2048", "mines",
                        "tetris", "tank", "air"):
            self.assertIn(game_id, progress)
            self.assertIn("run_active", progress[game_id])

    def test_records_covers_all_games(self):
        records = default_records()
        for game_id in ("gomoku", "snake", "breakout", "2048", "mines",
                        "tetris", "air"):
            self.assertIn(game_id, records)

    def test_statistics_covers_global_plus_all_games(self):
        stats = default_statistics()
        self.assertIn("global", stats)
        for game_id in ("gomoku", "snake", "breakout", "2048", "mines",
                        "tetris", "air", "tank"):
            self.assertIn(game_id, stats)

    def test_settings_have_expected_defaults(self):
        settings = default_settings()
        self.assertEqual(settings["language"], "en")
        self.assertEqual(settings["master_volume"], 1.0)
        self.assertEqual(settings["muted"], False)


# ---------------------------------------------------------------------------
# Schema migration
# ---------------------------------------------------------------------------

class SchemaMigrationTests(unittest.TestCase):
    def setUp(self):
        self.manager = SaveManager(
            _fresh_save_root() / f".meridian-migration-test-{uuid.uuid4().hex}.json"
        )

    def tearDown(self):
        for path in (self.manager.path, self.manager.backup_path,
                     self.manager.path.with_suffix(".json.tmp")):
            path.unlink(missing_ok=True)

    def test_v0_empty_dict_migrates_to_current(self):
        """An empty dict (v0) should become a complete v5 save."""
        result = self.manager.migrate({})
        self.assertEqual(result["schema_version"], SCHEMA_VERSION)
        self.assertIn("settings", result)
        self.assertIn("progress", result)
        # Tank stats should exist (added in v5)
        self.assertIn("tank", result["statistics"])
        self.assertIn("tank", result["progress"])

    def test_v3_to_v5_preserves_air_data(self):
        """v3 already has air records/progress; migration must not wipe them."""
        v3 = {
            "schema_version": 3,
            "settings": {"language": "zh_hans"},
            "records": {"air": {"best_score": 9999}},
            "statistics": {"air": {"games_completed": 42}},
            "progress": {"air": {"campaign_complete": True}},
            "achievements": {"air_first_clear": {"unlocked_at": "2025-01-01"}},
        }
        result = self.manager.migrate(v3)
        self.assertEqual(result["schema_version"], SCHEMA_VERSION)
        self.assertEqual(result["settings"]["language"], "zh_hans")
        self.assertEqual(result["records"]["air"]["best_score"], 9999)
        self.assertEqual(result["statistics"]["air"]["games_completed"], 42)
        self.assertTrue(result["progress"]["air"]["campaign_complete"])
        self.assertIn("air_first_clear", result["achievements"])

    def test_v3_migration_adds_progress_run_active(self):
        """v3 added run_active/run_state for all games."""
        v2 = {
            "schema_version": 2,
            "settings": {},
            "records": {},
            "statistics": {},
            "achievements": {},
        }
        result = self.manager.migrate(v2)
        progress = result["progress"]
        self.assertTrue(progress["gomoku"]["run_active"] is False)
        self.assertIsNone(progress["gomoku"]["run_state"])

    def test_v4_to_v5_adds_tank_data(self):
        """v5 added the tank game statistics and progress."""
        v4 = {
            "schema_version": 4,
            "settings": {},
            "records": {},
            "statistics": {},
            "achievements": {},
            "progress": {
                "gomoku": {"run_active": False, "run_state": None},
                "snake": {"run_active": False, "run_state": None},
                "breakout": {"run_active": False, "run_state": None},
                "2048": {"run_active": False, "run_state": None},
                "mines": {"run_active": False, "run_state": None},
                "tetris": {"run_active": False, "run_state": None},
                "air": {"run_active": False, "run_state": None},
            },
        }
        result = self.manager.migrate(v4)
        self.assertIn("tank", result["statistics"])
        self.assertIn("tank", result["progress"])
        self.assertEqual(result["progress"]["tank"]["run_active"], False)

    def test_future_version_merges_without_losing_data(self):
        """If schema_version > current, deep-merge preserves future data while
        filling in missing defaults, though the version number stays as-is."""
        future = {
            "schema_version": 99,
            "settings": {"custom_future_key": "retained"},
            "records": {"future_game": {"score": 888}},
        }
        result = self.manager.migrate(future)
        # Future version is retained (not downgraded) to avoid data loss
        self.assertEqual(result["schema_version"], 99)
        # Custom future data should be preserved
        self.assertEqual(result["settings"]["custom_future_key"], "retained")
        self.assertEqual(result["records"]["future_game"]["score"], 888)
        # But defaults should still be filled in for missing keys
        self.assertEqual(result["settings"]["language"], "en")

    def test_migration_is_idempotent(self):
        """Running migrate twice produces the same result."""
        data = default_data()
        first = self.manager.migrate(data)
        second = self.manager.migrate(first)
        self.assertEqual(first, second)


# ---------------------------------------------------------------------------
# Atomic write and crash recovery
# ---------------------------------------------------------------------------

class AtomicWriteRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.save_root = _fresh_save_root()
        self.save_path = self.save_root / f".meridian-atomic-test-{uuid.uuid4().hex}.json"
        self.manager = SaveManager(self.save_path)

    def tearDown(self):
        for path in (self.save_path, self.save_path.with_suffix(".json.bak"),
                     self.save_path.with_suffix(".json.tmp")):
            path.unlink(missing_ok=True)
        # Also clean up any corrupt snapshots
        for p in self.save_root.glob("save.corrupt-*.json"):
            if str(uuid.uuid4().hex)[:8] in str(p):
                continue
            p.unlink(missing_ok=True)

    def test_save_and_load_roundtrip(self):
        data = default_data()
        data["settings"]["language"] = "zh_hans"
        self.manager.save(data)
        loaded = self.manager.load()
        self.assertEqual(loaded["settings"]["language"], "zh_hans")

    def test_first_load_with_no_file_returns_defaults(self):
        self.assertFalse(self.save_path.exists())
        loaded = self.manager.load()
        self.assertEqual(loaded["schema_version"], SCHEMA_VERSION)

    def test_atomic_write_leaves_no_temp_file(self):
        data = default_data()
        self.manager.save(data)
        self.assertTrue(self.save_path.exists())
        self.assertFalse(self.save_path.with_suffix(".json.tmp").exists())

    def test_save_creates_backup(self):
        # First save: no backup yet
        data = default_data()
        self.manager.save(data)
        self.assertTrue(self.save_path.exists())
        self.assertFalse(self.manager.backup_path.exists())

        # Second save: backup appears
        data["settings"]["language"] = "zh_hans"
        self.manager.save(data)
        self.assertTrue(self.manager.backup_path.exists())

    def test_corrupt_save_falls_back_to_backup(self):
        # Create a valid save and backup
        data = default_data()
        data["settings"]["language"] = "zh_hans"
        self.manager.save(data)
        self.manager.save(data)  # creates backup
        # Corrupt the main save
        self.save_path.write_text("not valid json {{{", encoding="utf-8")
        loaded = self.manager.load()
        self.assertEqual(loaded["settings"]["language"], "zh_hans")

    def test_corrupt_save_with_no_backup_returns_defaults(self):
        self.save_path.write_text("garbage", encoding="utf-8")
        loaded = self.manager.load()
        self.assertEqual(loaded["schema_version"], SCHEMA_VERSION)

    def test_empty_file_returns_defaults(self):
        self.save_path.write_text("", encoding="utf-8")
        loaded = self.manager.load()
        self.assertEqual(loaded["schema_version"], SCHEMA_VERSION)

    def test_json_without_schema_version_receives_defaults(self):
        self.save_path.write_text(json.dumps({"settings": {"language": "fr"}}),
                                  encoding="utf-8")
        loaded = self.manager.load()
        # The language setting should survive migration
        self.assertEqual(loaded["settings"]["language"], "fr")
        self.assertEqual(loaded["schema_version"], SCHEMA_VERSION)

    def test_reset_settings_keeps_progress(self):
        data = default_data()
        data["settings"]["language"] = "ja"
        data["records"]["snake"]["best_score"] = 42
        result = self.manager.reset_settings(data)
        self.assertEqual(result["settings"]["language"], "en")
        self.assertEqual(result["records"]["snake"]["best_score"], 42)

    def test_erase_progress_wipes_everything(self):
        data = default_data()
        data["records"]["snake"]["best_score"] = 42
        data["achievements"]["test"] = {"unlocked_at": "2025-01-01"}
        result = self.manager.erase_progress(data)
        self.assertEqual(result["records"]["snake"]["best_score"], 0)
        self.assertEqual(result["achievements"], {})
        self.assertEqual(result["statistics"]["snake"]["games_started"], 0)


# ---------------------------------------------------------------------------
# Environment variable path
# ---------------------------------------------------------------------------

class EnvPathTests(unittest.TestCase):
    def test_env_var_overrides_save_path(self):
        custom = _fresh_save_root() / f".meridian-env-test-{uuid.uuid4().hex}.json"
        old = os.environ.get("MERIDIAN_SAVE_PATH")
        try:
            os.environ["MERIDIAN_SAVE_PATH"] = str(custom)
            manager = SaveManager()
            self.assertEqual(manager.path, custom)
        finally:
            if old is None:
                os.environ.pop("MERIDIAN_SAVE_PATH", None)
            else:
                os.environ["MERIDIAN_SAVE_PATH"] = old


if __name__ == "__main__":
    unittest.main()
