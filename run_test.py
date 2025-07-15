from pathlib import Path
from src.repo_to_text.core import process_repository

input_directory = Path("/tmp/test_repo")
output_text_file = Path("/tmp/context_output.txt")

print("Starting repository processing...")
process_repository(input_directory, output_text_file)
print("Processing complete.")
