import pytest
from pathlib import Path
from typer.testing import CliRunner
from repo_to_text.cli import app


runner = CliRunner()


@pytest.fixture
def temp_repo(tmp_path: Path) -> Path:
    repo_root = tmp_path / "test_repo"
    repo_root.mkdir()

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

    expected_tree = """Project Tree:
=============
├── README.md
├── docs
│   └── guide.md
└── src
    └── main.py

File Contents:
============="""

    expected_readme = """--- START OF README.md ---
# Test Repo
--- END OF README.md ---"""

    expected_guide = """--- START OF docs/guide.md ---
# Guide
--- END OF docs/guide.md ---"""

    expected_main = """--- START OF src/main.py ---
print('hello world')
--- END OF src/main.py ---"""

    assert expected_tree in content

    assert expected_readme in content
    assert expected_guide in content
    assert expected_main in content

    assert "dist/" not in content
    assert "node_modules" not in content
    assert "secret.key" not in content
    assert ".gitignore" not in content
    assert ".context_ignore" not in content
    assert "logo.png" not in content
