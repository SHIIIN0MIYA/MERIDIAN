"""R6.1 -- AST replay audit of the ``ZH`` translation table.

``meridian/localization.py`` fills ``ZH`` with **four** writes, in source order:

1. ``ZH: dict[str, str] = {...}``             -- main table (module level)
2. ``ZH.update({...})``                       -- achievements / campaign text
3. ``ZH.update(collect_lore_translations())`` -- inside a ``try:`` block
4. ``ZH.update({...})``                       -- tank duel

Python dict semantics make the *last* write win, so a key defined twice with two
different values is a silent translation bug: nothing raises, the game simply
shows the wrong word under one of the two meanings.

Two implementation traps this audit exists to catch:

* The main table is an ``ast.AnnAssign`` (``ZH: dict[str, str] = {...}``), so a
  scanner that only matches ``ast.Assign`` skips all ~307 of its keys -- and the
  ``README``-style "no duplicate keys" result is then meaningless.
* Scanning only dict *literals* misses the ~267 lore keys merged at runtime by
  ``ZH.update(collect_lore_translations())``.

So the scan replays every module-level write in statement order and resolves the
runtime call for real.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import meridian.localization as localization
from meridian.localization import ZH, set_language, translate
from meridian.lore import collect_lore_translations

SOURCE_PATH = Path(localization.__file__).resolve()

#: Duplicate keys whose two definitions carry the SAME value.  The later write
#: is a no-op, so these are harmless; they are pinned here so that a future
#: value change turns into a loud failure instead of a silent meaning flip.
KNOWN_BENIGN_DUPLICATES = {
    "ALL REALMS STABLE",
    "BYE BYE SEE U NEXT TIME~",
    "DRAW",
    "LORE",
    "PAUSED",
    "SHIELD",
}


@pytest.fixture(autouse=True)
def _chinese():
    set_language("zh_hans")
    yield
    set_language("en")


def _iter_statements(body):
    """Yield ``body``'s statements in source order, descending into blocks.

    Function/class bodies are skipped on purpose: ``register_game_translations``
    also calls ``ZH.update(translations)``, but with a caller-supplied dict, so
    it is not a module-level table write.
    """
    for stmt in body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        yield stmt
        for field in ("body", "orelse", "finalbody"):
            nested = getattr(stmt, field, None)
            if isinstance(nested, list):
                yield from _iter_statements(nested)
        for handler in getattr(stmt, "handlers", ()):
            yield from _iter_statements(handler.body)


def _dict_pairs(node: ast.AST) -> list[tuple[str, str]]:
    if not isinstance(node, ast.Dict):
        pytest.fail(f"expected a dict literal, got {type(node).__name__}")
    pairs = []
    for key, value in zip(node.keys, node.values):
        if not (isinstance(key, ast.Constant) and isinstance(key.value, str)):
            pytest.fail(f"non-literal ZH key at line {getattr(key, 'lineno', '?')}")
        if not (isinstance(value, ast.Constant) and isinstance(value.value, str)):
            pytest.fail(f"non-literal ZH value at line {getattr(value, 'lineno', '?')}")
        pairs.append((key.value, value.value))
    return pairs


def _update_pairs(call: ast.Call) -> list[tuple[str, str]]:
    arg = call.args[0] if call.args else None
    if isinstance(arg, ast.Dict):
        return _dict_pairs(arg)
    if (
        isinstance(arg, ast.Call)
        and isinstance(arg.func, ast.Name)
        and arg.func.id == "collect_lore_translations"
    ):
        return list(collect_lore_translations().items())
    pytest.fail(
        "unsupported ZH.update(...) argument in localization.py "
        f"(line {call.lineno}); the audit cannot see its keys"
    )


def _zh_writes() -> list[tuple[int, str, list[tuple[str, str]]]]:
    """Replay the module's ``ZH`` writes as ``(line, kind, pairs)`` in order."""
    tree = ast.parse(SOURCE_PATH.read_text(encoding="utf-8"))
    writes: list[tuple[int, str, list[tuple[str, str]]]] = []
    for stmt in _iter_statements(tree.body):
        if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
            targets = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
            if not any(
                isinstance(t, ast.Name) and t.id == "ZH" for t in targets
            ) or not isinstance(stmt.value, ast.Dict):
                continue
            kind = "main-literal" if isinstance(stmt, ast.AnnAssign) else "assign-literal"
            writes.append((stmt.lineno, kind, _dict_pairs(stmt.value)))
        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            call = stmt.value
            func = call.func
            if not (
                isinstance(func, ast.Attribute)
                and func.attr == "update"
                and isinstance(func.value, ast.Name)
                and func.value.id == "ZH"
            ):
                continue
            kind = (
                "update-collect"
                if isinstance(call.args[0], ast.Call)
                else "update-literal"
            )
            writes.append((stmt.lineno, kind, _update_pairs(call)))
    return writes


def _census():
    definitions: dict[str, list[str]] = {}
    for _, _, pairs in _zh_writes():
        for key, value in pairs:
            definitions.setdefault(key, []).append(value)
    total = sum(len(values) for values in definitions.values())
    conflicting = {k: v for k, v in definitions.items() if len(set(v)) > 1}
    benign = {k: v for k, v in definitions.items() if len(v) > 1 and len(set(v)) == 1}
    return definitions, total, conflicting, benign


def _census_report() -> str:
    definitions, total, conflicting, benign = _census()
    lines = [f"ZH audit: {len(definitions)} distinct keys / {total} definitions"]
    for line, kind, pairs in _zh_writes():
        lines.append(f"  write @{line} ({kind}): {len(pairs)} definitions")
    if conflicting:
        lines.append("CONFLICTING keys (later write silently wins):")
        for key in sorted(conflicting):
            lines.append(f"  {key!r}: {conflicting[key]!r}")
    else:
        lines.append("no conflicting keys")
    lines.append(f"benign same-value duplicates: {sorted(benign)}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Scanner integrity -- these fail if the replay misses a write
# --------------------------------------------------------------------------- #

def test_scan_replays_all_four_zh_writes():
    writes = _zh_writes()

    assert [kind for _, kind, _ in writes] == [
        "main-literal",
        "update-literal",
        "update-collect",
        "update-literal",
    ], f"unexpected ZH write sequence: {[(line, kind) for line, kind, _ in writes]}"
    assert all(pairs for _, _, pairs in writes), "a ZH write contributed no keys"
    # ast.AnnAssign trap: matching only ast.Assign would skip the whole main table.
    assert len(writes[0][2]) > 300, (
        "the main ZH table is an AnnAssign (`ZH: dict[str, str] = {...}`); a "
        "scanner that only matches ast.Assign reports a bogus clean audit"
    )
    # runtime-merge trap: the lore keys are not a dict literal in localization.py.
    assert len(writes[2][2]) > 200, "the collect_lore_translations() merge was not replayed"


def test_census_totals_match_snapshot():
    definitions, total, _, _ = _census()

    assert (len(definitions), total) == (800, 806), (
        "the ZH table changed size. Re-run the audit and update the snapshot:\n"
        + _census_report()
    )


# --------------------------------------------------------------------------- #
# The actual content gate
# --------------------------------------------------------------------------- #

def test_no_conflicting_duplicate_keys():
    """A key defined twice with two different values is a silent bug."""
    assert _census()[2] == {}, (
        "duplicate ZH keys with conflicting values -- pick one meaning and "
        "delete/re-key the other:\n" + _census_report()
    )


def test_benign_duplicate_keys_are_pinned():
    _, _, _, benign = _census()

    assert set(benign) == KNOWN_BENIGN_DUPLICATES, (
        "same-value duplicates changed; harmless ones are allowed but must be "
        "reviewed explicitly:\n" + _census_report()
    )


# --------------------------------------------------------------------------- #
# R6 / V-6 regressions pinned by this table
# --------------------------------------------------------------------------- #

def test_2048_game_name_is_in_the_table():
    """system.py:1119 renders ``translate('2048')`` in the profile page."""
    assert "2048" in ZH, "missing game-name key: the profile page shows '2048'"
    assert translate("2048") == "数字合成"


def test_p_to_resume_hint_keeps_full_width_style():
    """One key, one value: the tank-duel block must not re-define the hint."""
    assert translate("P TO RESUME   ESC FOR MENU") == "P：继续　ESC：返回菜单"
