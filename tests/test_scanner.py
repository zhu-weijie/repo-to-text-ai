import pytest
from pathlib import Path
from repo_to_text_ai.scanner import find_all_files


@pytest.fixture
def nested_repo(tmp_path: Path) -> Path:
    repo_root = tmp_path / "nested_repo"
    repo_root.mkdir()

    (repo_root / ".gitignore").write_text("*.log\n")
    (repo_root / "app.py").touch()
    (repo_root / "data.log").touch()

    frontend_dir = repo_root / "frontend"
    frontend_dir.mkdir()
    (frontend_dir / ".gitignore").write_text("dist/\n")
    (frontend_dir / "app.js").touch()
    (frontend_dir / "debug.log").touch()

    frontend_dist_dir = frontend_dir / "dist"
    frontend_dist_dir.mkdir()
    (frontend_dist_dir / "bundle.js").touch()

    return repo_root


def test_scanner_with_nested_ignores(nested_repo: Path):
    included_files = find_all_files(nested_repo)

    relative_paths = [str(p.relative_to(nested_repo)) for p in included_files]

    assert "app.py" in relative_paths
    assert "frontend/app.js" in relative_paths

    assert "data.log" not in relative_paths
    assert "frontend/debug.log" not in relative_paths
    assert "frontend/dist/bundle.js" not in relative_paths

    assert len(included_files) == 2
