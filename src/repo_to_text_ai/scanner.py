import logging
from pathlib import Path
import pathspec
from .utils import is_binary

logger = logging.getLogger(__name__)


def find_all_files(repo_path: Path) -> list[Path]:
    logger.debug(f"Scanning for files in: {repo_path}")

    ignore_file_paths = list(repo_path.rglob(".gitignore"))
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
        for parent in [path.parent] + list(path.parent.parents):
            if parent in spec_map:
                path_relative_to_spec = path.relative_to(parent)
                if spec_map[parent].match_file(str(path_relative_to_spec)):
                    logger.debug(f"IGNORE (spec in {parent}): {path}")
                    is_ignored = True
                    break
            if parent == repo_path:
                break

        if not is_ignored:
            logger.debug(f"INCLUDE: {path}")
            included_files.append(path)

    return sorted(included_files)
