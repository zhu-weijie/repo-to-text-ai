import pytest
from pathlib import Path
from typer.testing import CliRunner
from repo_to_text.cli import app, setup_logging
from repo_to_text.core import process_repository
import logging

runner = CliRunner()


@pytest.fixture
def temp_repo(tmp_path: Path) -> Path:
    repo_root = tmp_path / "test_repo"
    repo_root.mkdir()
    (repo_root / ".git").mkdir()
    (repo_root / "src").mkdir()
    (repo_root / "src" / "main.py").write_text("print('hello world')")
    (repo_root / "docs").mkdir()
    (repo_root / "docs" / "guide.md").write_text("# Guide")
    (repo_root / "README.md").write_text("# Test Repo")
    (repo_root / "logo.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00")
    (repo_root / "node_modules").mkdir()
    (repo_root / "node_modules" / "some_lib.js").write_text("var x = 1;")
    (repo_root / "dist").mkdir()
    (repo_root / "dist" / "output.js").write_text("var x = 1;")
    (repo_root / "secret.key").write_text("TOP_SECRET")
    (repo_root / ".gitignore").write_text(
        """
        # Node modules
        node_modules/
        # Build output
        dist/
        """
    )
    (repo_root / ".context_ignore").write_text(
        """
        # Ignore secrets
        *.key
        """
    )
    return repo_root


def test_cli_integration(temp_repo: Path):
    output_file = temp_repo.parent / "output.txt"
    result = runner.invoke(app, [str(temp_repo), "-o", str(output_file)])

    assert result.exit_code == 0
    assert "Success! Context file created" in result.stdout
    assert output_file.exists()
    content = output_file.read_text()
    assert len(content) > 0
    expected_tree = "Project Tree:\n=============\n├── README.md\n├── docs\n│   └── guide.md\n└── src\n    └── main.py\n\nFile Contents:\n============="
    assert expected_tree in content
    assert "--- START OF README.md ---" in content
    assert "dist/" not in content
    assert "node_modules" not in content
    assert "secret.key" not in content


def test_error_on_non_git_repo(tmp_path: Path):
    result = runner.invoke(app, [str(tmp_path)])
    assert result.exit_code == 1


def test_core_logic_logging(temp_repo: Path, caplog):
    setup_logging(verbose=True)
    output_file = temp_repo.parent / "output.txt"

    with caplog.at_level(logging.DEBUG):
        process_repository(temp_repo, output_file, disable_progress=True)

    messages = [record.message for record in caplog.records]

    def assert_in_logs(substring):
        assert any(
            substring in msg for msg in messages
        ), f"'{substring}' not found in logs"

    assert_in_logs("Starting repository processing")
    assert_in_logs("Loaded 2 effective patterns from .gitignore")
    assert_in_logs("Loaded 1 effective patterns from .context_ignore")
    assert_in_logs("IGNORE (pathspec): dist/output.js")
    assert_in_logs("INCLUDE: README.md")
