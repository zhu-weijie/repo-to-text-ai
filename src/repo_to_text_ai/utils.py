from pathlib import Path


def is_binary(file_path: Path) -> bool:
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            return b"\x00" in chunk
    except Exception:
        return True


def generate_tree_from_files(file_paths: list[Path], repo_root: Path) -> str:
    tree = {}
    for path in file_paths:
        parts = path.relative_to(repo_root).parts
        node = tree
        for part in parts:
            node = node.setdefault(part, {})

    def build_tree_lines(node, prefix=""):
        lines = []
        items = sorted(node.items())
        for i, (name, sub_node) in enumerate(items):
            connector = "└── " if i == len(items) - 1 else "├── "
            lines.append(f"{prefix}{connector}{name}")
            if sub_node:
                extension = "    " if i == len(items) - 1 else "│   "
                lines.extend(build_tree_lines(sub_node, prefix + extension))
        return lines

    return "\n".join(build_tree_lines(tree))


def get_files_from_context(repo_path: Path) -> set[Path] | None:
    context_file = repo_path / ".context"
    if not context_file.is_file():
        return None

    included_files = set()
    with open(context_file, "r") as f:
        for line in f:
            line_content = line.split("#", 1)[0]
            line = line_content.strip()
            if not line:
                continue

            target_path = repo_path / line

            if not target_path.exists():
                continue

            if target_path.is_file():
                included_files.add(target_path.resolve())
            elif target_path.is_dir():
                for file_in_dir in target_path.rglob("*"):
                    if file_in_dir.is_file():
                        included_files.add(file_in_dir.resolve())

    return included_files
