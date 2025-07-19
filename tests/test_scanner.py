import pytest
from pathlib import Path
from repo_to_text_ai.scanner import find_all_files
import logging
from pathspec import PathSpec


@pytest.fixture
def nested_repo(tmp_path: Path) -> Path:
    repo_root = tmp_path / "nested_repo"
    repo_root.mkdir()

    (repo_root / ".gitignore").write_text("*.log\n")

    frontend_dir = repo_root / "frontend"
    frontend_dir.mkdir()
    (frontend_dir / ".gitignore").write_text("dist/\n")

    (repo_root / "main.py").touch()
    (frontend_dir / "app.js").touch()

    return repo_root


def test_finds_and_parses_nested_gitignores(nested_repo: Path, caplog):
    with caplog.at_level(logging.DEBUG):
        spec_map_result = find_all_files(nested_repo)

        assert "Found 2 .gitignore file(s)." in caplog.text
        assert f"Loaded 1 patterns from {nested_repo / '.gitignore'}" in caplog.text
        assert (
            f"Loaded 1 patterns from {nested_repo / 'frontend' / '.gitignore'}"
            in caplog.text
        )

        assert isinstance(spec_map_result, dict)
        assert len(spec_map_result) == 2

        assert nested_repo in spec_map_result
        assert (nested_repo / "frontend") in spec_map_result

        assert isinstance(spec_map_result[nested_repo], PathSpec)
