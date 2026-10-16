"""Regression tests for R8 cleanups.

* V-20 `_capture_data` rebuilt the Mines `best_times` dict from scratch, so
  records for any mode the current build does not offer were deleted at the
  first save (and every mode without a record gained an explicit null).
* V-21 the Gomoku size gate read `state.get("size", state.get("board_count"))`,
  so a decoy `size` key satisfied it while `board_count` stayed wrong: a 5x5
  grid passed a 15-wide check and the restore then walked off the grid.
* The shape-only validator checked key *presence* only, so a present-but-wrong
  typed value (`snake.body == 5`) was accepted and raised while restoring.
* R8.1 the source comments that were GBK/UTF-8 mojibake are repaired, and the
  two UTF-8 BOMs are gone (both broke tools that read with plain utf-8).
"""

from __future__ import annotations

import ast
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from meridian.runstate import RunStateVerdict, validate

PROJECT = Path(__file__).resolve().parents[1]


class MinesBestTimesTests(unittest.TestCase):
    def test_records_for_unknown_modes_survive_a_save(self):
        import os

        scratch = Path(tempfile.mkdtemp(prefix="meridian-r8-"))
        previous = os.environ.get("MERIDIAN_SAVE_PATH")
        save_path = scratch / "save.json"
        os.environ["MERIDIAN_SAVE_PATH"] = str(save_path)
        try:
            import pygame

            pygame.init()
            from meridian.app import Game
            from meridian.persistence import default_data

            data = default_data()
            data["records"]["mines"]["best_times"] = {
                "19x99": 1, "9x10": 4200, "9x12": 999,
            }
            save_path.write_text(json.dumps(data), encoding="utf-8")

            game = Game()
            game._save_now()
            after = json.loads(save_path.read_text(encoding="utf-8"))
            best_times = after["records"]["mines"]["best_times"]

            self.assertEqual(best_times.get("19x99"), 1, "an unknown mode was deleted")
            self.assertEqual(best_times.get("9x12"), 999, "an unknown mode was deleted")
            self.assertEqual(best_times.get("9x10"), 4200, "a real record was lost")
            game.audio.stop()
            pygame.quit()
        finally:
            if previous is None:
                os.environ.pop("MERIDIAN_SAVE_PATH", None)
            else:
                os.environ["MERIDIAN_SAVE_PATH"] = previous
            shutil.rmtree(scratch, ignore_errors=True)


class GomokuSizeGateTests(unittest.TestCase):
    def _snapshot(self, board_count, size=None):
        payload = {
            "format": 1, "board_count": board_count,
            "grid": [[0] * board_count for _ in range(board_count)],
            "move_history": [], "win_stones": [], "winner": 0,
            "current_player": 1, "move_count": 0, "last_move": None,
        }
        if size is not None:
            payload["size"] = size
        return payload

    def test_a_decoy_size_key_cannot_satisfy_the_gate(self):
        decoy = self._snapshot(board_count=5, size=15)
        self.assertEqual(
            validate("gomoku", decoy, expected_size=15),
            RunStateVerdict.REJECTED,
            "a decoy 'size' key let a 5x5 grid pass a 15-wide check",
        )

    def test_a_honest_15_wide_snapshot_is_accepted(self):
        snapshot = self._snapshot(board_count=15, size=15)
        # An empty, unresolved board is "nothing to resume", which is COMPLETED
        # rather than REJECTED -- the point is that it is not turned away as
        # malformed.
        self.assertNotEqual(
            validate("gomoku", snapshot, expected_size=15),
            RunStateVerdict.REJECTED,
        )

    def test_mismatched_size_is_still_rejected(self):
        self.assertEqual(
            validate("gomoku", self._snapshot(19), expected_size=15),
            RunStateVerdict.REJECTED,
        )


class ShapeTypePredicateTests(unittest.TestCase):
    def _snake(self, **overrides):
        snapshot = {"body": [[12, 10]], "dir": [1, 0], "next_dir": [1, 0],
                    "food": [1, 1], "score": 0, "move_timer": 0}
        snapshot.update(overrides)
        return snapshot

    def test_wrong_typed_body_is_rejected(self):
        self.assertEqual(
            validate("snake", self._snake(body=5)), RunStateVerdict.REJECTED
        )

    def test_wrong_typed_dir_is_rejected(self):
        self.assertEqual(
            validate("snake", self._snake(dir=1)), RunStateVerdict.REJECTED
        )

    def test_a_well_typed_snake_snapshot_is_still_resumable(self):
        self.assertEqual(
            validate("snake", self._snake()), RunStateVerdict.RESUMABLE
        )

    def test_breakout_bricks_must_be_a_list(self):
        snapshot = {"bricks": 5, "ball": {}, "paddle": {}, "score": 0,
                    "lives": 3, "level": 1}
        self.assertEqual(
            validate("breakout", snapshot), RunStateVerdict.REJECTED
        )

    def test_2048_grid_must_be_a_list(self):
        self.assertEqual(
            validate("2048", {"grid": 5, "score": 0, "moves": 0}),
            RunStateVerdict.REJECTED,
        )

    def test_missing_key_is_still_rejected(self):
        snapshot = self._snake()
        del snapshot["food"]
        self.assertEqual(validate("snake", snapshot), RunStateVerdict.REJECTED)

    def test_validate_never_raises(self):
        hostile = [None, [], "x", 5, {"body": object()}, {"dir": {}}]
        for value in hostile:
            with self.subTest(value=repr(value)):
                validate("snake", value)      # must not raise


class EncodingHygieneTests(unittest.TestCase):
    SOURCE_FILES = ("gomoku.py", "snake.py", "breakout.py", "shell_desktop.py")

    def test_no_utf8_bom_in_source(self):
        for path in sorted((PROJECT / "meridian").glob("*.py")):
            with self.subTest(path=path.name):
                self.assertFalse(
                    path.read_bytes().startswith(b"\xef\xbb\xbf"),
                    f"{path.name} still has a UTF-8 BOM",
                )

    def test_source_files_parse_as_plain_utf8(self):
        """A BOM makes `ast.parse(open(p, encoding="utf-8").read())` fail."""
        for path in sorted((PROJECT / "meridian").glob("*.py")):
            with self.subTest(path=path.name):
                ast.parse(path.read_text(encoding="utf-8"))

    def test_the_previously_corrupted_comments_are_repaired(self):
        import re

        def damaged(line: str) -> bool:
            if "\ufffd" in line:
                return False
            try:
                back = line.encode("gbk").decode("utf-8")
            except (UnicodeEncodeError, UnicodeDecodeError):
                return False
            return (
                back != line
                and re.search(r"[\u4e00-\u9fff]", back) is not None
                and re.search(r"[\u4e00-\u9fff]", line) is not None
            )

        for name in self.SOURCE_FILES:
            path = PROJECT / "meridian" / name
            text = path.read_text(encoding="utf-8")
            offenders = [i for i, line in enumerate(text.splitlines(), 1) if damaged(line)]
            with self.subTest(path=name):
                self.assertEqual(offenders, [], f"{name}: mojibake at {offenders[:5]}")


if __name__ == "__main__":
    unittest.main()
