"""Explicitly regenerate the bilingual visual-regression baselines."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import importlib
import os
from collections.abc import Sequence
from pathlib import Path
import sys
from uuid import uuid4

import pygame


REPO_ROOT = Path(__file__).resolve().parents[1]
BASELINE_ROOT = REPO_ROOT / "tests" / "visual_baselines"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_visual_scenes = importlib.import_module("tests.visual_scenes")
SCENE_NAMES = _visual_scenes.SCENE_NAMES
render_scene = _visual_scenes.render_scene


@contextmanager
def _isolated_save_environment():
    save_root = REPO_ROOT / ".test-tmp"
    save_root.mkdir(parents=True, exist_ok=True)
    save_path = save_root / f"visual-baseline-{uuid4().hex}.json"
    previous = os.environ.get("MERIDIAN_SAVE_PATH")
    os.environ["MERIDIAN_SAVE_PATH"] = str(save_path)
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("MERIDIAN_SAVE_PATH", None)
        else:
            os.environ["MERIDIAN_SAVE_PATH"] = previous
        for generated_path in (
            save_path,
            save_path.with_suffix(".json.bak"),
            save_path.with_suffix(".json.tmp"),
        ):
            generated_path.unlink(missing_ok=True)


def write_baselines(root: Path) -> list[Path]:
    """Render every scene in both languages beneath ``root``."""
    written: list[Path] = []
    for language in ("en", "zh_hans"):
        for scene in SCENE_NAMES:
            target = root / language / f"{scene}.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            pygame.image.save(render_scene(scene, language), target)
            written.append(target)
    return written


def main(
    argv: Sequence[str] | None = None,
    *,
    baseline_root: Path = BASELINE_ROOT,
) -> int:
    """Run the guarded command-line baseline update."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--yes",
        action="store_true",
        help="confirm overwriting the visual baseline directory",
    )
    args = parser.parse_args(argv)

    print(f"Visual baselines will be overwritten in: {baseline_root.resolve()}")
    if not args.yes:
        print("Refusing to update baselines without explicit --yes confirmation.")
        return 2

    with _isolated_save_environment():
        written = write_baselines(baseline_root)
    print(f"Wrote {len(written)} visual baselines.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
