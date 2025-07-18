from pathlib import Path


def is_binary(file_path: Path) -> bool:
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            return b"\x00" in chunk
    except Exception:
        return True


def process_repository(repo_path: Path, output_file: Path):
    all_content = []

    for file_path in repo_path.rglob("*"):
        if not file_path.is_file():
            continue

        if ".git" in file_path.parts:
            continue

        if is_binary(file_path):
            print(f"Skipping binary file: {file_path.relative_to(repo_path)}")
            continue

        try:
            relative_path = file_path.relative_to(repo_path)

            file_content = file_path.read_text(encoding="utf-8")

            file_block = (
                f"--- START OF {relative_path} ---\n"
                f"{file_content}\n"
                f"--- END OF {relative_path} ---\n\n"
            )
            all_content.append(file_block)

        except UnicodeDecodeError:
            print(
                f"Skipping file due to UnicodeDecodeError: {file_path.relative_to(repo_path)}"
            )
            continue
        except Exception as e:
            print(f"Error reading file {file_path.relative_to(repo_path)}: {e}")
            continue

    output_file.write_text("".join(all_content), encoding="utf-8")
