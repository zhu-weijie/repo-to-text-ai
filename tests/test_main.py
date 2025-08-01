import pytest
from pathlib import Path
from typer.testing import CliRunner
from repo_to_text_ai.cli import app, setup_logging
from repo_to_text_ai.core import process_repository
import logging
from repo_to_text_ai import __version__
from repo_to_text_ai.utils import get_files_from_context

runner = CliRunner()


@pytest.fixture
def temp_repo(tmp_path: Path) -> Path:
    repo_root = tmp_path / "test_repo"
    repo_root.mkdir()
    (repo_root / ".git").mkdir()

    (repo_root / ".gitignore").write_text(
        """
        # General ignores
        *.log
        /secret.key
        """
    )
    (repo_root / "app.py").write_text("print('main app')")
    (repo_root / "config.log").write_text("some log data")
    (repo_root / "secret.key").write_text("ROOT_SECRET")

    frontend_dir = repo_root / "frontend"
    frontend_dir.mkdir()
    (frontend_dir / ".gitignore").write_text(
        """
        # Frontend specific ignores
        node_modules/
        dist/
        """
    )
    (frontend_dir / "app.js").write_text("console.log('frontend app');")
    (frontend_dir / "secret.key").write_text("FRONTEND_SECRET")

    (frontend_dir / "dist").mkdir()
    (frontend_dir / "dist" / "bundle.js").write_text("var app;")
    (frontend_dir / "node_modules").mkdir()
    (frontend_dir / "node_modules" / "react.js").write_text("var react;")
    (repo_root / ".context_ignore").write_text("*.md")
    return repo_root


def test_cli_integration(temp_repo: Path):
    output_file = temp_repo.parent / "output.txt"
    result = runner.invoke(app, [str(temp_repo), "-o", str(output_file)])

    assert result.exit_code == 0
    assert "Success! Context file created" in result.stdout
    assert output_file.exists()
    content = output_file.read_text()
    assert len(content) > 0

    expected_tree = """Project Tree:
=============
├── app.py
└── frontend
    ├── app.js
    └── secret.key

File Contents:
============="""
    assert expected_tree in content

    assert "print('main app')" in content
    assert "console.log('frontend app');" in content
    assert "FRONTEND_SECRET" in content

    assert "config.log" not in content
    assert "ROOT_SECRET" not in content
    assert "bundle.js" not in content
    assert "react.js" not in content


def test_error_on_non_git_repo(tmp_path: Path):
    result = runner.invoke(app, [str(tmp_path)])
    assert result.exit_code == 1


def test_core_logic_logging(temp_repo: Path, caplog):
    setup_logging(verbose=True)
    output_file = temp_repo.parent / "output.txt"

    with caplog.at_level(logging.DEBUG):
        process_repository(temp_repo, output_file, disable_progress=True)

    log_text = caplog.text

    assert "Loaded 2 effective patterns from .gitignore" in log_text
    assert "Loaded 2 effective patterns from frontend/.gitignore" in log_text
    assert "Loaded 1 effective patterns from .context_ignore" in log_text

    assert "IGNORE (matched in .gitignore): config.log" in log_text
    assert "IGNORE (matched in .gitignore): secret.key" in log_text
    assert "IGNORE (matched in .gitignore): frontend/dist/bundle.js" in log_text
    assert "INCLUDE: app.py" in log_text


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
