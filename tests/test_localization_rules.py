"""R6.2 -- table-driven spec for :func:`meridian.localization._format_dynamic`.

The dynamic formatter is a first-match-wins ordered rule table, so *order is
part of the contract*: a generic rule placed before a specialised one makes the
specialised rule unreachable (that is exactly V-6, where
``^(.+) // PHASE (\\d+)$`` shadowed ``^WARNING // (.+) // PHASE (\\d+)$``).

Every one of the 34 shipped rules gets one positive case (the rule fires and
yields the expected Chinese string) and one negative case (the rule must not
match).  The rule table is read back out of ``localization.py`` with ``ast`` so
the spec cannot silently drift from the code, and the case table is asserted to
cover the shipped table one-for-one, in order.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

import meridian.localization as localization
from meridian.localization import ZH, set_language, translate

SOURCE_PATH = Path(localization.__file__).resolve()

# (pattern, replacement, positive input, expected translation, negative input)
CASES: list[tuple[str, str, str, str, str]] = [
    (r"^SCORE (\d+)$", r"得分 \1", "SCORE 120", "得分 120", "SCORE 12X"),
    (r"^BEST (\d+)$", r"最高 \1", "BEST 5", "最高 5", "BEST SCORE"),
    (
        r"^LINES (\d+)\s+LEVEL (\d+)$",
        r"消行 \1　等级 \2",
        "LINES 12  LEVEL 3",
        "消行 12　等级 3",
        "LINES 12 LEVEL",
    ),
    (r"^TIME (\d{1,3}:\d{2})$", r"时间 \1", "TIME 03:21", "时间 03:21", "TIME ATTACK"),
    (r"^Current: (.+)$", r"当前：\1", "Current: 3", "当前：3", "current: 3"),
    (r"^OPEN (\d+)$", r"已翻开 \1", "OPEN 4", "已翻开 4", "OPEN X"),
    (r"^CHAPTER (\d+)$", r"章节 \1", "CHAPTER 2", "章节 2", "CHAPTER"),
    (r"^CHAPTER (\d+) // (.+)$", r"章节 \1 // \2", "CHAPTER 1 // DAWN", "章节 1 // DAWN", "CHAPTER // DAWN"),
    (r"^(.+) / MISSION$", r"\1 / 任务", "ALPHA / MISSION", "ALPHA / 任务", "ALPHA / MISSION 2"),
    (r"^(.+) / BOSS$", r"\1 / Boss", "TEMPEST / BOSS", "TEMPEST / Boss", "TEMPEST / BOSSES"),
    (
        r"^OBJECTIVE: DESTROY (.+)$",
        r"任务目标：摧毁 \1",
        "OBJECTIVE: DESTROY RADAR ARRAY",
        "任务目标：摧毁 RADAR ARRAY",
        "OBJECTIVE: DESTROY",
    ),
    # --- the // PHASE family: specialised rules must come first (V-6) -------
    (
        r"^WARNING // (.+) // PHASE (\d+)$",
        r"警报 // \1 // 阶段 \2",
        "WARNING // TEMPEST // PHASE 1",
        "警报 // TEMPEST // 阶段 1",
        "WARNING // TEMPEST",
    ),
    (
        r"^(.+) // PHASE (\d+) // ARMOR SHIFT$",
        r"\1 // 阶段 \2 // 装甲切换",
        "MIRROR // PHASE 3 // ARMOR SHIFT",
        "MIRROR // 阶段 3 // 装甲切换",
        "MIRROR // PHASE 3",
    ),
    (r"^(.+) // PHASE (\d+)$", r"\1 // 阶段 \2", "TEMPEST // PHASE 2", "TEMPEST // 阶段 2", "PHASE 2"),
    (
        r"^ALERT: HOSTILE COMMAND FRAME (.+) CONFIRMED\.$",
        r"警报：确认敌方指挥机体 \1。",
        "ALERT: HOSTILE COMMAND FRAME SOVEREIGN CONFIRMED.",
        "警报：确认敌方指挥机体 SOVEREIGN。",
        "ALERT: HOSTILE COMMAND FRAME SOVEREIGN CONFIRMED",
    ),
    (
        r"^COMMAND: CHAPTER (\d+) FLIGHT WINDOW IS OPEN\.$",
        r"指挥部：第 \1 章飞行窗口已开启。",
        "COMMAND: CHAPTER 3 FLIGHT WINDOW IS OPEN.",
        "指挥部：第 3 章飞行窗口已开启。",
        "COMMAND: CHAPTER 3 FLIGHT WINDOW IS OPEN",
    ),
    (r"^ARCHIVE (\d+) // (.+)$", r"档案 \1 // \2", "ARCHIVE 2 // LORE", "档案 2 // LORE", "ARCHIVE // LORE"),
    (r"^COMMAND FRAME: (.+)$", r"指挥机体：\1", "COMMAND FRAME: SOVEREIGN", "指挥机体：SOVEREIGN", "COMMAND FRAME:"),
    (
        r"^A / D  RECORD (\d+) / (\d+)\s+ESC  RETURN$",
        r"A / D：档案 \1 / \2　ESC：返回",
        "A / D  RECORD 3 / 8  ESC  RETURN",
        "A / D：档案 3 / 8　ESC：返回",
        "A / D  RECORD 3 ESC  RETURN",
    ),
    (r"^(.+)\s+ESC  MENU$", r"\1　ESC：菜单", "P  PAUSE ESC  MENU", "P  PAUSE　ESC：菜单", "ESC  MENU"),
    (r"^(.+)  PLAY (.+)$", r"\1　游玩时间 \2", "2048  PLAY 00:10", "2048　游玩时间 00:10", "2048 PLAY 00:10"),
    (r"^CHARGE (\d+)%$", r"充能 \1%", "CHARGE 75%", "充能 75%", "CHARGE 75"),
    (r"^DESTROYED (\d+) / (\d+)$", r"击破 \1 / \2", "DESTROYED 3 / 8", "击破 3 / 8", "DESTROYED 3"),
    (
        r"^GRAZES (\d+)\s+HULL (\d+) / 5$",
        r"擦弹 \1　耐久 \2 / 5",
        "GRAZES 12  HULL 3 / 5",
        "擦弹 12　耐久 3 / 5",
        "GRAZES 12 HULL 3 / 4",
    ),
    (r"^COMBO\s+(\d+)$", r"连击 \1", "COMBO  7", "连击 7", "COMBO"),
    (r"^GRAZE\s+(\d+)$", r"擦弹 \1", "GRAZE 9", "擦弹 9", "GRAZES 9"),
    (r"^MULTI\s+x(.+)$", r"倍率 x\1", "MULTI x3.5", "倍率 x3.5", "MULTI 3.5"),
    (
        r"^COMPLETE (\d+) / (\d+)\s+(\d+)%$",
        r"完成 \1 / \2　\3%",
        "COMPLETE 3 / 8  42%",
        "完成 3 / 8　42%",
        "COMPLETE 3 / 8 42",
    ),
    (r"^(.+) / LOCKED$", r"\1 / 未解锁", "TANK DUEL / LOCKED", "TANK DUEL / 未解锁", "TANK DUEL / LOCKED 2"),
    (r"^UNLOCKED (\d+) / (\d+)$", r"已解锁 \1 / \2", "UNLOCKED 3 / 8", "已解锁 3 / 8", "UNLOCKED 3"),
    (r"^(.+) WINS$", r"\1胜利", "TEMPEST WINS", "TEMPEST胜利", "TEMPEST WON"),
    (r"^(.+)'S TURN$", r"轮到\1", "PLAYER'S TURN", "轮到PLAYER", "PLAYERS TURN"),
    (r"^FPS (.+)$", r"帧率 \1", "FPS 60", "帧率 60", "FPS"),
    (r"^INDEX (\d+)$", r"指数 \1", "INDEX 42", "指数 42", "INDEX"),
]

IDS = [pattern for pattern, *_ in CASES]


@pytest.fixture(autouse=True)
def _chinese():
    set_language("zh_hans")
    yield
    set_language("en")


def _shipped_patterns() -> list[tuple[str, str]]:
    """Read ``_format_dynamic``'s rule tuple straight out of the source file."""
    tree = ast.parse(SOURCE_PATH.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_format_dynamic":
            for stmt in node.body:
                if isinstance(stmt, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == "patterns" for t in stmt.targets
                ):
                    return [tuple(pair) for pair in ast.literal_eval(stmt.value)]
    pytest.fail("could not find the `patterns` tuple inside _format_dynamic")


# --------------------------------------------------------------------------- #
# The spec table itself
# --------------------------------------------------------------------------- #

def test_shipped_table_matches_the_spec_in_order():
    shipped = _shipped_patterns()
    spec = [(pattern, replacement) for pattern, replacement, *_ in CASES]

    assert shipped == spec, (
        "the shipped _format_dynamic table drifted from the spec (order matters: "
        "the first matching rule wins):\n"
        f"shipped={shipped}\nspec={spec}"
    )


def test_shipped_table_has_no_duplicate_rules():
    patterns = [pattern for pattern, _ in _shipped_patterns()]

    assert len(patterns) == 34, f"expected 34 rules, found {len(patterns)}"
    # `^UNLOCKED (\d+) / (\d+)$` used to be defined twice, byte for byte.
    assert len(set(patterns)) == len(patterns), (
        "duplicate dynamic rule(s): the later copy is dead code -- "
        f"{sorted({p for p in patterns if patterns.count(p) > 1})}"
    )


def test_spec_covers_every_shipped_rule():
    shipped = {pattern for pattern, _ in _shipped_patterns()}
    spec = {pattern for pattern, *_ in CASES}

    assert shipped == spec, (
        f"rules without a test case: {sorted(shipped - spec)}; "
        f"cases without a rule: {sorted(spec - shipped)}"
    )


# --------------------------------------------------------------------------- #
# Positive / negative cases
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_positive_case(case):
    pattern, _, positive, expected, _ = case

    assert positive not in ZH, (
        f"{positive!r} is a literal ZH key, so it would bypass the regex rule; "
        "pick an input that exercises _format_dynamic"
    )

    assert translate(positive) == expected, (
        f"rule {pattern!r}: translate({positive!r}) != {expected!r}"
    )


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_negative_case(case):
    pattern, _, _, expected, negative = case

    assert re.match(pattern, negative) is None, (
        f"rule {pattern!r} must not match {negative!r}"
    )
    assert translate(negative) != expected, (
        f"{negative!r} must not be translated as if it matched {pattern!r}"
    )


# --------------------------------------------------------------------------- #
# V-6: ordering regressions
# --------------------------------------------------------------------------- #

def test_warning_rule_precedes_the_generic_phase_rule():
    patterns = [pattern for pattern, _ in _shipped_patterns()]

    warning = patterns.index(r"^WARNING // (.+) // PHASE (\d+)$")
    generic = patterns.index(r"^(.+) // PHASE (\d+)$")
    assert warning < generic, (
        "the generic '// PHASE' rule shadows 'WARNING // ... // PHASE ...' "
        "because the first match wins"
    )


def test_armor_shift_rule_precedes_the_generic_phase_rule():
    patterns = [pattern for pattern, _ in _shipped_patterns()]

    armor = patterns.index(r"^(.+) // PHASE (\d+) // ARMOR SHIFT$")
    generic = patterns.index(r"^(.+) // PHASE (\d+)$")
    assert armor < generic, "a specialised '// PHASE' rule must outrank the generic one"


def test_warning_phase_translation_is_reachable():
    """V-6: air_raid.py:445 emits this string."""
    assert translate("WARNING // TEMPEST // PHASE 1") == "警报 // TEMPEST // 阶段 1"


def test_armor_shift_translation_is_not_broken_by_the_reorder():
    assert translate("MIRROR // PHASE 3 // ARMOR SHIFT") == "MIRROR // 阶段 3 // 装甲切换"


def test_time_rule_no_longer_translates_non_time_labels():
    assert translate("TIME ATTACK") == "TIME ATTACK"
    assert translate("TIME 03:21") == "时间 03:21"
