"""Smoke tests for the shared ``GameSaveTestCase`` harness.

These verify the harness itself: that it isolates the save file and that the
save/restart roundtrip helpers work against a real game.  Behaviour of the
games is covered by their own test modules.
"""

from __future__ import annotations

import os

from _game_fixture import RUN_STATE_GAME_IDS, GameSaveTestCase


class HarnessIsolationTests(GameSaveTestCase):
    def test_save_path_is_not_the_real_save(self):
        real_root = os.environ.get("APPDATA")
        recorded = os.environ.get("MERIDIAN_SAVE_PATH")
        self.assertEqual(recorded, str(self.save_path))
        self.assertTrue(str(self.save_path).startswith(str(self.save_dir)))
        if real_root:
            self.assertNotIn(str(real_root), str(self.save_path))

    def test_save_file_is_written_under_the_temp_dir(self):
        self.game._save_now()
        self.assertTrue(self.save_path.is_file())
        self.assertEqual(self.save_path.parent, self.save_dir)


class RunStateRoundtripTests(GameSaveTestCase):
    def test_snake_run_state_survives_a_restart(self):
        self.game._start_snake_game()
        self.game.snake_score = 7
        captured = self.assert_run_state_survives_restart("snake")
        self.assertEqual(captured["score"], 7)

    def test_roundtrip_helper_leaves_no_pending_state_before_a_game(self):
        self.assertIsNone(self.pending_run_state("snake"))
        self.assertFalse(self.progress("snake")["run_active"])

    def test_every_registered_game_exposes_a_capture_method(self):
        for game_id in RUN_STATE_GAME_IDS:
            with self.subTest(game_id=game_id):
                self.assertTrue(
                    hasattr(self.game, f"_capture_{game_id}_run_state"),
                    f"missing capture method for {game_id}",
                )
                self.assertIn(game_id, self.game.save_data["progress"])
