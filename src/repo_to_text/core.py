from pathlib import Path
import pathspec
import logging
from tqdm import tqdm
from .utils import is_binary, generate_tree_from_files

logger = logging.getLogger(__name__)


def process_repository(
    repo_path: Path, output_file: Path, disable_progress: bool = False
):
    logger.debug(f"Starting repository processing for: {repo_path}")

    def load_effective_patterns(file_path: Path) -> list[str]:
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

    gitignore_patterns = load_effective_patterns(gitignore_path)
    if gitignore_patterns:
        logger.debug(
            f"Loaded {len(gitignore_patterns)} effective patterns from .gitignore"
        )

    context_ignore_patterns = load_effective_patterns(context_ignore_path)
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

    included_files = sorted(included_files)

    tree_string = generate_tree_from_files(included_files, repo_path)
    header = (
        "Project Tree:\n"
        "=============\n"
        f"{tree_string}\n\n"
        "File Contents:\n"
        "==============\n\n"
    )
    all_content = [header]

    for item in tqdm(
        included_files,
        desc="Processing files",
        unit="file",
        disable=disable_progress,
    ):
        try:
            relative_item_path = item.relative_to(repo_path)
            file_content = item.read_text(encoding="utf-8")
            file_block = (
                f"--- START OF {relative_item_path} ---\n"
                f"{file_content}\n"
                f"--- END OF {relative_item_path} ---\n\n"
            )
            all_content.append(file_block)
        except Exception as e:
            all_content.append(
                f"--- ERROR READING FILE: {item.relative_to(repo_path)}: {e} ---\n\n"
            )
            pass

    output_file.write_text("".join(all_content), encoding="utf-8")
