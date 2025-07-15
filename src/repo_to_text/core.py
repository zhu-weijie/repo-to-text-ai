from pathlib import Path


def process_repository(repo_path: Path, output_file: Path):
    all_content = []
    for file_path in repo_path.rglob('*'):
        if file_path.is_file():
            try:
                relative_path = file_path.relative_to(repo_path)
                file_content = file_path.read_text(encoding='utf-8')
                file_block = (
                    f"--- START OF {relative_path} ---\n"
                    f"{file_content}\n"
                    f"--- END OF {relative_path} ---\n\n"
                )
                all_content.append(file_block)
            except UnicodeDecodeError:
                all_content.append(
                    f"--- SKIPPED BINARY FILE: {file_path.relative_to(repo_path)} ---\n\n"
                )
            except Exception as e:
                all_content.append(
                    f"--- ERROR READING FILE: {file_path.relative_to(repo_path)}: {e} ---\n\n"
                )
    output_file.write_text("".join(all_content), encoding='utf-8')
    print(f"Successfully processed repository. Output written to {output_file}")
