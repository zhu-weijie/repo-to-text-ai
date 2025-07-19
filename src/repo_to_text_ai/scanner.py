import logging
from pathlib import Path
import pathspec
from .utils import is_binary

logger = logging.getLogger(__name__)


def find_all_files(repo_path: Path) -> list[Path]:
    logger.debug(f"Scanning for files in: {repo_path}")

    ignore_files = list(repo_path.rglob(".gitignore")) + list(
        repo_path.rglob(".context_ignore")
    )

    spec_map = {}
    for ignore_file in ignore_files:
        with open(ignore_file, "r") as f:
            patterns = [
                line.strip()
                for line in f
                if line.strip() and not line.strip().startswith("#")
            ]
        if patterns:
            logger.debug(
                f"Loaded {len(patterns)} effective patterns from {ignore_file.relative_to(repo_path)}"
            )
            spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns)
            spec_map[ignore_file] = spec

    included_files = []
    all_paths = list(repo_path.rglob("*"))
    logger.debug(f"Found {len(all_paths)} total paths to consider.")

    for path in all_paths:
        if not path.is_file():
            continue

        if ".git" in path.parts:
            continue
        if path.name in [".gitignore", ".context_ignore"]:
            continue
        if is_binary(path):
            continue

        is_ignored = False
        for ignore_file, spec in spec_map.items():
            ignore_dir = ignore_file.parent
            try:
                relative_to_ignore_dir = path.relative_to(ignore_dir)
                if spec.match_file(str(relative_to_ignore_dir)):
                    logger.debug(
                        f"IGNORE (matched in {ignore_file.name}): {path.relative_to(repo_path)}"
                    )
                    is_ignored = True
                    break
            except ValueError:
                continue

        if not is_ignored:
            logger.debug(f"INCLUDE: {path.relative_to(repo_path)}")
            included_files.append(path)

    return sorted(included_files)
