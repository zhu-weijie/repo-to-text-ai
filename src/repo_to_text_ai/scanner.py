import logging
from pathlib import Path
import pathspec
from .utils import is_binary

logger = logging.getLogger(__name__)


def find_all_files(repo_path: Path) -> list[Path]:
    logger.debug(f"Scanning for files in: {repo_path}")

    def _load_effective_patterns(file_path: Path) -> list[str]:
        if not file_path.is_file():
            return []
        with open(file_path, "r") as f:
            return [
                line.strip()
                for line in f
                if line.strip() and not line.strip().startswith("#")
            ]

    gitignore_path = repo_path / ".gitignore"
    context_ignore_path = repo_path / ".context_ignore"

    gitignore_patterns = _load_effective_patterns(gitignore_path)
    if gitignore_patterns:
        logger.debug(
            f"Loaded {len(gitignore_patterns)} effective patterns from .gitignore"
        )

    context_ignore_patterns = _load_effective_patterns(context_ignore_path)
    if context_ignore_patterns:
        logger.debug(
            f"Loaded {len(context_ignore_patterns)} effective patterns from .context_ignore"
        )

    all_ignore_patterns = gitignore_patterns + context_ignore_patterns
    spec = (
        pathspec.PathSpec.from_lines("gitwildmatch", all_ignore_patterns)
        if all_ignore_patterns
        else None
    )

    included_files = []
    all_paths = list(repo_path.rglob("*"))
    logger.debug(f"Found {len(all_paths)} total paths to consider.")

    for path in all_paths:
        if not path.is_file():
            continue

        relative_path = path.relative_to(repo_path)

        if spec and spec.match_file(str(relative_path)):
            logger.debug(f"IGNORE (pathspec): {relative_path}")
            continue
        if ".git" in relative_path.parts:
            logger.debug(f"IGNORE (.git dir): {relative_path}")
            continue
        if relative_path.name in [".gitignore", ".context_ignore"]:
            logger.debug(f"IGNORE (metafile): {relative_path}")
            continue
        if is_binary(path):
            logger.debug(f"IGNORE (binary): {relative_path}")
            continue

        logger.debug(f"INCLUDE: {relative_path}")
        included_files.append(path)

    return sorted(included_files)
