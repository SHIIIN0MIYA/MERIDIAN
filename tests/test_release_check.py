from pathlib import Path
import subprocess
import sys

from tools.check_release import check_git, check_metadata


ROOT = Path(__file__).resolve().parents[1]


def write_version(repo: Path, version: str = "3.2.0") -> None:
    package = repo / "meridian"
    package.mkdir()
    (package / "version.py").write_text(f'__version__ = "{version}"\n', encoding="utf-8")


def init_git_repo(repo: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Release Check Test",
            "-c",
            "user.email=release-check@example.invalid",
            "commit",
            "--allow-empty",
            "-m",
            "initial",
            "-q",
        ],
        cwd=repo,
        check=True,
    )


def test_current_repository_metadata_is_valid():
    assert check_metadata(ROOT) == []


def test_version_missing_from_changelog_is_reported(tmp_path):
    write_version(tmp_path)
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")

    assert "version missing from CHANGELOG.md" in check_metadata(tmp_path)


def test_missing_changelog_has_stable_problem_text(tmp_path):
    write_version(tmp_path)

    assert check_metadata(tmp_path) == ["CHANGELOG.md is missing"]


def test_non_utf8_changelog_has_stable_problem_text(tmp_path):
    write_version(tmp_path)
    (tmp_path / "CHANGELOG.md").write_bytes(b"\xff")

    assert check_metadata(tmp_path) == ["CHANGELOG.md is not valid UTF-8"]


def test_existing_local_release_tag_has_stable_problem_text(tmp_path):
    init_git_repo(tmp_path)
    subprocess.run(["git", "tag", "v3.2.0"], cwd=tmp_path, check=True)

    assert "local tag v3.2.0 already exists" in check_git(tmp_path, "3.2.0")


def test_cli_runs_from_repository_root_without_pythonpath():
    result = subprocess.run(
        [sys.executable, "tools/check_release.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    assert result.returncode in {0, 1}
    assert "ModuleNotFoundError" not in result.stderr
