"""R-06 reproducer: Air Raid chapter-story resume picks the wrong level.

Problem
-------
``AirRaidMixin._prepare_air_level(level)`` derives a 0-based *chapter* index and
parks it in ``self._pending_brief_level`` when a chapter story interrupts the
launch (air_raid.py:219-222 -> air_raid.py:128).

After the story, ``_handle_air_story_event`` feeds that parked value straight
back into ``_prepare_air_level()`` as if it were a *level* index
(air_raid.py:1665-1668).

So the story resumes at ``AIR_LEVELS[chapter - 1]`` instead of the level that
was actually interrupted. Only chapter 1 works, and only because its chapter
index and its first level index are both 0.

Run
---
    python tools/repro_r06_air_chapter.py

The script drives the real code paths (no gameplay required) and exits
non-zero while the mapping is wrong. It writes to a throwaway save file and
never touches the real one.
"""

from __future__ import annotations

import os
import pathlib
import sys
import tempfile

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import pygame  # noqa: E402

from meridian import Game  # noqa: E402
from meridian.arcade_levels import AIR_CHAPTERS, AIR_LEVELS  # noqa: E402

TOTAL_LEVELS = len(AIR_LEVELS)
CHAPTER_COUNT = len(AIR_CHAPTERS)

ENTER = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)


def describe(level: int) -> str:
    """Human-readable identity of a level index."""
    if not 0 <= level < TOTAL_LEVELS:
        return f"L{level:02d} <out of range>"
    stage = AIR_LEVELS[level]
    kind = "BOSS" if stage["boss"] else "MISSION"
    return f"L{level:02d} ch{stage['chapter']} {stage['name']} / {kind}"


def first_level_of_chapter(chapter_num: int) -> int:
    """Chapter N owns level indices [2*(N-1), 2*(N-1)+1]."""
    return 2 * (chapter_num - 1)


def make_game() -> tuple[Game, pathlib.Path]:
    tmp_dir = pathlib.Path(tempfile.mkdtemp(prefix="meridian-r06-"))
    save_path = tmp_dir / "save.json"
    os.environ["MERIDIAN_SAVE_PATH"] = str(save_path)
    return Game(), save_path


def setup_campaign(game: Game, chapters_already_read: int) -> None:
    """Reproduce the real save state when the player reaches a given chapter.

    Everything up to ``chapters_already_read`` has been seen; nothing after.
    """
    game._air_progress()["stories_read"] = list(
        range(1, chapters_already_read + 1)
    )
    game.air_story_source = ""
    game._pending_brief_level = None
    game.air_campaign_active = True
    game.air_mode = "standard"


def probe_chapter(game: Game, chapter_num: int) -> dict:
    """Ask to launch the chapter's first mission and read the story that fires."""
    target_level = first_level_of_chapter(chapter_num)
    setup_campaign(game, chapters_already_read=chapter_num - 1)

    game._prepare_air_level(target_level)

    story_shown = game.state == game.AIR_STORY
    parked = getattr(game, "_pending_brief_level", None)
    level_during_story = game.air_level  # deliberately observed before ENTER

    if story_shown:
        game._handle_air_story_event(ENTER)  # exactly what the player presses

    return {
        "chapter": chapter_num,
        "target": target_level,
        "story_shown": story_shown,
        "parked": parked,
        "level_during_story": level_during_story,
        "resumed": game.air_level,
    }


def consume_story(game: Game, resume_level: int | None = None) -> None:
    """Press ENTER on the story page.

    When ``resume_level`` is given, the parked value is overwritten first.
    That is exactly the one-line fix (park the *level* instead of the chapter
    index), so passing it here simulates the repaired behaviour.
    """
    if resume_level is not None:
        game._pending_brief_level = resume_level
    game._handle_air_story_event(ENTER)


def walk_campaign(game: Game, apply_fix: bool) -> list[dict]:
    """Walk levels 0..15 through the real advance path and log every story gate.

    ``_advance_air_after_clear`` (air_raid.py:985-989) is what runs after each
    cleared mission, so this is the sequence a real campaign experiences.
    """
    setup_campaign(game, chapters_already_read=0)
    game._prepare_air_level(0)
    if game.state == game.AIR_STORY:
        consume_story(game, resume_level=0 if apply_fix else None)

    rows = []
    for expected in range(1, TOTAL_LEVELS):
        game.air_level = expected - 1          # pretend the previous level cleared
        game._advance_air_after_clear()
        story = game.state == game.AIR_STORY
        if story:
            consume_story(game, resume_level=expected if apply_fix else None)
        rows.append({
            "expected": expected,
            "story_shown": story,
            "resumed": game.air_level,
            "boss_level": AIR_LEVELS[expected]["boss"],
        })
    return rows


def probe_boss_rush(game: Game) -> list[dict]:
    """Boss Rush feeds boss levels through the same story gate.

    ``_start_air_boss_rush`` (air_raid.py:203-210) and ``_choose_air_supply``
    (air_raid.py:974-983) both call ``_prepare_air_level`` with an odd (boss)
    level.  Reachable when the chapter stories are still unread, i.e. when Boss
    Rush was unlocked through the developer panel (developer.py:111-118) rather
    than by finishing the standard campaign.
    """
    rows = []
    for index in range(CHAPTER_COUNT):
        target = index * 2 + 1  # boss-rush stage levels are 1,3,5,...,15
        chapter_num = AIR_LEVELS[target]["chapter"]
        setup_campaign(game, chapters_already_read=chapter_num - 1)
        game.air_mode = "boss_rush"
        game.air_boss_rush_index = index

        game._prepare_air_level(target, preserve_loadout=True)
        story = game.state == game.AIR_STORY
        parked = getattr(game, "_pending_brief_level", None)
        if story:
            game._handle_air_story_event(ENTER)

        rows.append({
            "stage": index,
            "target": target,
            "story_shown": story,
            "parked": parked,
            "resumed": game.air_level,
            "resumed_is_boss": AIR_LEVELS[game.air_level]["boss"],
        })
    return rows


def main() -> int:
    pygame.init()
    game, save_path = make_game()

    line = "=" * 82
    thin = "-" * 82

    print(line)
    print("R-06  Air Raid chapter story -> resumed level")
    print(line)
    print()
    print("Chapter N owns level indices [2*(N-1), 2*(N-1)+1]:")
    for index, chapter in enumerate(AIR_CHAPTERS):
        first = first_level_of_chapter(index + 1)
        print(
            f"  chapter {index + 1}  {chapter['name']:<14}"
            f"levels {first:02d}-{first + 1:02d}   boss {chapter['boss']}"
        )
    print()

    print(thin)
    print("Each row: launch the chapter's FIRST mission, then press ENTER on its story")
    print(thin)
    print(
        f"{'chapter':<9}{'launched':<34}{'parked':<8}"
        f"{'resumed':<34}{'verdict'}"
    )
    print(thin)

    rows = []
    for chapter_num in range(1, CHAPTER_COUNT + 1):
        row = probe_chapter(game, chapter_num)
        rows.append(row)

        if not row["story_shown"]:
            verdict = "no story"
        elif row["resumed"] == row["target"]:
            verdict = "OK"
        else:
            verdict = "WRONG"

        parked = row["parked"]
        print(
            f"{row['chapter']:<9}"
            f"{describe(row['target']):<34}"
            f"{str(parked) if parked is not None else '-':<8}"
            f"{describe(row['resumed']):<34}"
            f"{verdict}"
        )
    print()

    wrong = [row for row in rows if row["resumed"] != row["target"]]
    ok = [row for row in rows if row["resumed"] == row["target"]]

    # ── Probe B: full campaign walk, current vs repaired ──────────────
    print(line)
    print("B.  Full campaign walk: every story gate, current vs repaired")
    print(line)
    print("'resume the interrupted level' = the one-line fix (park the level).")
    print()

    for apply_fix in (False, True):
        label = "REPAIRED (park the level)" if apply_fix else "CURRENT (park the chapter)"
        print(thin)
        print(f"{label}")
        print(thin)
        print(f"{'next level':<34}{'story?':<9}{'resumed':<34}{'verdict'}")
        print(thin)
        walk = walk_campaign(game, apply_fix=apply_fix)
        gates = 0
        for row in walk:
            expected, actual = row["expected"], row["resumed"]
            if not row["story_shown"]:
                continue
            gates += 1
            verdict = "OK" if actual == expected else "WRONG"
            print(
                f"{describe(expected):<34}"
                f"{'story':<9}"
                f"{describe(actual):<34}"
                f"{verdict}"
            )
        print(f"{gates} story gates; "
              f"{'all resume correctly' if apply_fix else 'all but chapter 1 mis-resume'}")
        print()

    # ── Probe C: Boss Rush ────────────────────────────────────────────
    print(line)
    print("C.  Boss Rush: every stage is a BOSS level, put through the same gate")
    print(line)
    print("Reachable when Boss Rush is unlocked from the developer panel, since")
    print("that path never marks the chapter stories as read.")
    print()
    print(f"{'stage':<7}{'asked for':<34}{'resumed':<34}{'kind change':<20}{'verdict'}")
    print(thin)

    rush_rows = probe_boss_rush(game)
    demoted = []
    for row in rush_rows:
        verdict = "OK" if row["resumed"] == row["target"] else "WRONG"
        if row["resumed"] != row["target"]:
            demoted.append(row)
        if row["resumed_is_boss"]:
            change = "boss -> boss"
        else:
            change = "boss -> MISSION"
        print(
            f"{row['stage']:<7}"
            f"{describe(row['target']):<34}"
            f"{describe(row['resumed']):<34}"
            f"{change:<20}"
            f"{verdict}"
        )
    missions = [row for row in demoted if not row["resumed_is_boss"]]
    print()
    print(f"{len(demoted)} of {CHAPTER_COUNT} boss-rush stages are redirected; "
          f"{len(missions)} of them land on a regular mission instead of a boss.")
    print()

    print(line)
    print("SUMMARY")
    print(line)
    if wrong:
        print(f"{len(wrong)} of {CHAPTER_COUNT} chapter stories resume at the WRONG level.")
        print()
        print("Mechanism: 'parked' is a 0-based CHAPTER index, but it is consumed")
        print("as a LEVEL index (air_raid.py:128 sets it, air_raid.py:1665-1668 reads it).")
        print("Result: the story restarts level (chapter - 1) instead of the chapter's")
        print("first mission.")
        print()
        print(f"{'story of':<12}{'should resume':<34}{'actually resumes':<34}{'jump'}")
        print(thin)
        for row in wrong:
            delta = row["resumed"] - row["target"]
            print(
                f"chapter {row['chapter']:<4}"
                f"{describe(row['target']):<34}"
                f"{describe(row['resumed']):<34}"
                f"{delta:+d} levels"
            )
        print()
        print("Player-visible effect, chapter by chapter:")
        for row in wrong:
            stage = AIR_LEVELS[row["resumed"]]
            kind = "boss" if stage["boss"] else "mission"
            print(
                f"  chapter {row['chapter']} story ({AIR_CHAPTERS[row['chapter'] - 1]['name']})"
                f" -> replays chapter {stage['chapter']}'s {kind} {stage['name']}"
            )
        if ok:
            print()
            print(
                "Correct by coincidence: chapter "
                + ", ".join(str(row["chapter"]) for row in ok)
                + " (chapter index == first level index == 0)"
            )
    else:
        print("No mismatch detected (the bug appears to be fixed).")

    print()
    print(f"throwaway save: {save_path}")
    print("The real save under %APPDATA%\\MERIDIAN was not touched.")

    game.audio.stop()
    pygame.quit()
    return 1 if wrong else 0


if __name__ == "__main__":
    raise SystemExit(main())
