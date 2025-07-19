import logging
from pathlib import Path
import pathspec

logger = logging.getLogger(__name__)


def find_all_files(repo_path: Path) -> list[Path]:
    logger.debug(f"Scanning for files in: {repo_path}")
    ignore_file_paths = list(repo_path.rglob(".gitignore"))
    logger.debug(f"Found {len(ignore_file_paths)} .gitignore file(s).")

    spec_map = {}
    for ignore_file in ignore_file_paths:
        directory = ignore_file.parent
        with open(ignore_file, "r") as f:
            patterns = [
                line.strip()
                for line in f
                if line.strip() and not line.strip().startswith("#")
            ]

        if patterns:
            spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns)
            spec_map[directory] = spec
            logger.debug(f"Loaded {len(patterns)} patterns from {ignore_file}")

    return spec_map
