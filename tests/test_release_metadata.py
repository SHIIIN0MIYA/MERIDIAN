from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_changelog_has_v3_2_release_metadata_without_mojibake():
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    assert text.startswith("# Changelog\n")
    assert "## [Unreleased]" in text
    assert "## [3.2.0] - 2026-07-13" in text
    assert "Tank Duel" in text
    assert "坦克对决" in text
    assert "�" not in text
    for marker in ("鈥", "馃", "銆"):
        assert marker not in text
    assert text.index("## [Unreleased]") < text.index("## [3.2.0] - 2026-07-13")
