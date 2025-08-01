import pytest
from pathlib import Path
from typer.testing import CliRunner
from repo_to_text_ai.cli import app
from repo_to_text_ai.core import process_repository
import logging
from repo_to_text_ai import __version__
from repo_to_text_ai.utils import get_files_from_context

runner = CliRunner()


@pytest.fixture
def temp_repo(tmp_path: Path) -> Path:
    """A more complex fixture with nested .gitignore files."""
    repo_root = tmp_path / "test_repo"
    repo_root.mkdir()
    (repo_root / ".git").mkdir()

    (repo_root / "frontend").mkdir()
    (repo_root / "frontend" / "dist").mkdir()
    (repo_root / "frontend" / "node_modules").mkdir()

    (repo_root / "app.py").write_text("import flask")
    (repo_root / "config.log").write_text("some log data")
    (repo_root / "secret.key").write_text("TOP_SECRET")

    (repo_root / "frontend" / "app.js").write_text("console.log('app')")
    (repo_root / "frontend" / "secret.key").write_text("FRONTEND_SECRET")
    (repo_root / "frontend" / "dist" / "bundle.js").write_text("bundle")
    (repo_root / "frontend" / "node_modules" / "react.js").write_text("react")

    (repo_root / ".gitignore").write_text("*.log\n*.key")
    (repo_root / "frontend" / ".gitignore").write_text("node_modules/")
    (repo_root / ".context_ignore").write_text("frontend/dist/")

    return repo_root


@pytest.mark.parametrize(
    "use_context_file, expected_in_output, not_expected_in_output",
    [
        (
            False,
            ["--- START OF app.py ---", "--- START OF frontend/app.js ---"],
            [
                "config.log",
                "secret.key",
                "frontend/secret.key",
                "node_modules",
                "bundle.js",
            ],
        ),
        (
            True,
            ["--- START OF app.py ---"],
            [
                "frontend/app.js",
                "config.log",
            ],
        ),
    ],
)
def test_cli_integration(
    temp_repo: Path,
    use_context_file: bool,
    expected_in_output: list[str],
    not_expected_in_output: list[str],
):
    if use_context_file:
        (temp_repo / ".context").write_text("app.py\nconfig.log\n")

    output_file = temp_repo.parent / "output.txt"
    result = runner.invoke(app, [str(temp_repo), "-o", str(output_file)])

    assert result.exit_code == 0
    content = output_file.read_text()

    for part in expected_in_output:
        assert part in content, f"Expected to find '{part}' in output"
    for part in not_expected_in_output:
        assert part not in content, f"Did not expect to find '{part}' in output"


def test_core_logic_logging(temp_repo: Path, caplog):
    output_file = temp_repo.parent / "output.txt"

    with caplog.at_level(logging.DEBUG):
        process_repository(temp_repo, output_file, disable_progress=True)

    messages = [record.message for record in caplog.records]

    def assert_in_logs(substring):
        assert any(
            substring in msg for msg in messages
        ), f"'{substring}' not found in logs"

    assert_in_logs("No .context file found")

    assert any("patterns from .gitignore" in msg for msg in messages)
    assert any("patterns from frontend/.gitignore" in msg for msg in messages)
    assert any("patterns from .context_ignore" in msg for msg in messages)

    assert_in_logs("IGNORE (pathspec): config.log")
    assert_in_logs("IGNORE (pathspec): frontend/node_modules/react.js")

    assert_in_logs("IGNORE (pathspec): frontend/dist/bundle.js")
    assert_in_logs("INCLUDE: app.py")


def test_version_flag():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert f"repo-to-text-ai version: {__version__}" in result.stdout


def test_get_files_from_context_utility(tmp_path: Path):
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "src").mkdir()
    (project_root / "src" / "main.py").write_text("main")
    (project_root / "src" / "utils.py").write_text("utils")
    (project_root / "docs").mkdir()
    (project_root / "docs" / "guide.md").write_text("guide")
    (project_root / "README.md").write_text("readme")

    (project_root / ".context").write_text(
        """
        # This is a comment, should be ignored

        README.md        # A specific file
        src/             # A whole directory
        
        # An empty line above should be ignored
        docs/guide.md    # Another specific file
        non_existent_file.txt # Should be ignored
        """
    )

    result_files = get_files_from_context(project_root)

    expected_files = {
        (project_root / "README.md").resolve(),
        (project_root / "src" / "main.py").resolve(),
        (project_root / "src" / "utils.py").resolve(),
        (project_root / "docs" / "guide.md").resolve(),
    }

    assert result_files is not None
    assert isinstance(result_files, set)
    assert result_files == expected_files


def test_get_files_from_context_returns_none_if_no_file(tmp_path: Path):
    assert get_files_from_context(tmp_path) is None
