from pathlib import Path
import pathspec
import logging
from tqdm import tqdm

from .utils import is_binary, generate_tree_from_files, get_files_from_context

logger = logging.getLogger(__name__)


def process_repository(
    repo_path: Path, output_file: Path, disable_progress: bool = False
):
    logger.debug(f"Starting repository processing for: {repo_path}")

    potential_files = get_files_from_context(repo_path)
    if potential_files is None:
        logger.debug("No .context file found, scanning all repository files.")
        potential_files = list(repo_path.rglob("*"))
    else:
        logger.debug(
            f"Found .context file, processing {len(potential_files)} specified paths."
        )

    ignore_patterns = []
    for gitignore_path in repo_path.rglob(".gitignore"):
        with open(gitignore_path, "r") as f:
            lines = f.readlines()
            ignore_patterns.extend(lines)
        logger.debug(
            f"Loaded {len(lines)} patterns from {gitignore_path.relative_to(repo_path)}"
        )

    for context_ignore_path in repo_path.rglob(".context_ignore"):
        with open(context_ignore_path, "r") as f:
            lines = f.readlines()
            ignore_patterns.extend(lines)
            logger.debug(
                f"Loaded {len(lines)} patterns from {context_ignore_path.relative_to(repo_path)}"
            )

    spec = (
        pathspec.PathSpec.from_lines("gitwildmatch", ignore_patterns)
        if ignore_patterns
        else None
    )

    included_files = []
    logger.debug(f"Found {len(potential_files)} total paths to consider.")

    for path in potential_files:
        if not path.is_file():
            continue

        relative_path = path.relative_to(repo_path)

        if spec and spec.match_file(str(relative_path)):
            logger.debug(f"IGNORE (pathspec): {relative_path}")
            continue
        if ".git" in relative_path.parts:
            logger.debug(f"IGNORE (.git dir): {relative_path}")
            continue
        if relative_path.name in [".gitignore", ".context_ignore", ".context"]:
            logger.debug(f"IGNORE (metafile): {relative_path}")
            continue
        if is_binary(path):
            logger.debug(f"IGNORE (binary): {relative_path}")
            continue

        logger.debug(f"INCLUDE: {relative_path}")
        included_files.append(path)

    included_files = sorted(included_files)

    if not included_files:
        logger.warning("No files to process. Output will be empty.")
        output_file.write_text("")
        return

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
