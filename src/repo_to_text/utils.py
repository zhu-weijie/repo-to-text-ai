from pathlib import Path

import pathspec


def is_binary(file_path: Path) -> bool:
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            return b"\x00" in chunk
    except Exception:
        return True


def generate_tree(directory: Path, spec: pathspec.PathSpec = None) -> str:
    tree_lines = []

    all_paths = sorted(list(directory.rglob("*")))

    for path in all_paths:
        relative_path = path.relative_to(directory)

        if spec and spec.match_file(str(relative_path)):
            continue
        if ".git" in relative_path.parts:
            continue
        if relative_path.name in [".gitignore", ".context_ignore"]:
            continue

        depth = len(relative_path.parts) - 1
        indent = "    " * depth

        prefix = "└── " if path.is_dir() else "├── "

        tree_lines.append(f"{indent}{prefix}{path.name}")

    return "\n".join(tree_lines)
