from pathlib import Path
import pathspec
from .utils import is_binary, generate_tree


def process_repository(repo_path: Path, output_file: Path):
    ignore_patterns = []
    gitignore_path = repo_path / ".gitignore"
    if gitignore_path.is_file():
        with open(gitignore_path, "r") as f:
            ignore_patterns.extend(f.readlines())

    context_ignore_path = repo_path / ".context_ignore"
    if context_ignore_path.is_file():
        with open(context_ignore_path, "r") as f:
            ignore_patterns.extend(f.readlines())

    spec = (
        pathspec.PathSpec.from_lines("gitwildmatch", ignore_patterns)
        if ignore_patterns
        else None
    )

    project_tree = generate_tree(repo_path, spec)

    header = (
        "Project Tree:\n"
        "=============\n"
        f"{project_tree}\n\n"
        "File Contents:\n"
        "==============\n\n"
    )

    all_content = [header]

    sorted_paths = sorted(list(repo_path.rglob("*")))

    for item in sorted_paths:
        relative_item_path = item.relative_to(repo_path)
        if spec and spec.match_file(str(relative_item_path)):
            continue

        if ".git" in item.parts:
            continue

        if item.name in [".gitignore", ".context_ignore"]:
            continue

        if item.is_file():
            if is_binary(item):
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
