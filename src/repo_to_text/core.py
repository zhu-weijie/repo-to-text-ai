from pathlib import Path
import pathspec
from .utils import is_binary, generate_tree_from_files


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

    included_files = []
    all_paths = sorted(list(repo_path.rglob("*")))

    for path in all_paths:
        if not path.is_file():
            continue

        relative_path = path.relative_to(repo_path)

        if spec and spec.match_file(str(relative_path)):
            continue
        if ".git" in relative_path.parts:
            continue
        if relative_path.name in [".gitignore", ".context_ignore"]:
            continue
        if is_binary(path):
            continue

        included_files.append(path)

    tree_string = generate_tree_from_files(included_files, repo_path)

    header = (
        "Project Tree:\n"
        "=============\n"
        f"{tree_string}\n\n"
        "File Contents:\n"
        "==============\n\n"
    )

    all_content = [header]

    for item in included_files:
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

    output_file.write_text("".join(all_content), encoding="utf-8")
