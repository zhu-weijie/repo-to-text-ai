from pathlib import Path
import logging
from tqdm import tqdm
from .scanner import find_all_files
from .utils import generate_tree_from_files

logger = logging.getLogger(__name__)


def process_repository(
    repo_path: Path, output_file: Path, disable_progress: bool = False
):
    logger.debug(f"Starting repository processing for: {repo_path}")

    included_files = find_all_files(repo_path)

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
