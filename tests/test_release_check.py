from pathlib import Path
import shutil
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
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
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


def write_cli_repo(repo: Path, version: str = "3.2.0") -> None:
    write_version(repo, version)
    (repo / "CHANGELOG.md").write_text(f"## [{version}]\n", encoding="utf-8")
    tools = repo / "tools"
    tools.mkdir()
    shutil.copyfile(ROOT / "tools" / "check_release.py", tools / "check_release.py")
    init_git_repo(repo)


def run_cli(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "tools/check_release.py"],
        cwd=repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
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


def test_version_drift_is_rejected_even_when_changelog_matches(tmp_path):
    write_version(tmp_path, "3.3.0")
    (tmp_path / "CHANGELOG.md").write_text("## [3.3.0]\n", encoding="utf-8")

    assert check_metadata(tmp_path) == ["version does not match release target 3.2.0"]


def test_existing_local_release_tag_has_stable_problem_text(tmp_path):
    init_git_repo(tmp_path)
    subprocess.run(["git", "tag", "v3.2.0"], cwd=tmp_path, check=True)

    assert "local tag v3.2.0 already exists" in check_git(tmp_path)


def test_cli_clean_repository_exits_zero_without_output(tmp_path):
    write_cli_repo(tmp_path)

    result = run_cli(tmp_path)

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


def test_cli_prints_each_problem_and_exits_one(tmp_path):
    write_cli_repo(tmp_path)
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")

    result = run_cli(tmp_path)

    assert result.returncode == 1
    assert result.stdout.splitlines() == [
        "version missing from CHANGELOG.md",
        "working tree is not clean",
    ]
    assert result.stderr == ""


def test_cli_rejects_version_drift_in_clean_repository(tmp_path):
    write_cli_repo(tmp_path, "3.3.0")

    result = run_cli(tmp_path)

    assert result.returncode == 1
    assert result.stdout == "version does not match release target 3.2.0\n"
    assert result.stderr == ""
