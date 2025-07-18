from pathlib import Path
import pathspec
from .utils import is_binary


def process_repository(repo_path: Path, output_file: Path):
    gitignore_path = repo_path / ".gitignore"
    spec = None
    if gitignore_path.is_file():
        with open(gitignore_path, "r") as f:
            spec = pathspec.PathSpec.from_lines("gitwildmatch", f)

    all_content = []

    for item in repo_path.rglob("*"):
        relative_item_path = item.relative_to(repo_path)
        if spec and spec.match_file(str(relative_item_path)):
            continue

        if ".git" in item.parts:
            continue

        if item.name == ".gitignore":
            continue

        if item.is_file():
            if is_binary(item):
                all_content.append(
                    f"--- SKIPPED BINARY FILE: {relative_item_path} ---\n\n"
                )
                continue

            try:
                file_content = item.read_text(encoding="utf-8")
                file_block = (
                    f"--- START OF {relative_item_path} ---\n"
                    f"{file_content}\n"
                    f"--- END OF {relative_item_path} ---\n\n"
                )
                all_content.append(file_block)
            except Exception as e:
                all_content.append(
                    f"--- ERROR READING FILE: {relative_item_path}: {e} ---\n\n"
                )

    output_file.write_text("".join(all_content), encoding="utf-8")
