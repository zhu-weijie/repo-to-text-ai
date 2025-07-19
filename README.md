# Repo-to-Text-AI

**Turn an entire Git repository into a single, organized text file designed for providing context to Large Language Models (LLMs).**

`repo-to-text-ai` is a command-line tool that intelligently traverses a local repository, respecting `.gitignore` rules, and consolidates the code into a clean text file. This is perfect for pasting complete project contexts into AI prompts for analysis, documentation, or feature development.

---

## Features

-   **Single File Output:** Combines all relevant source files into one `.txt` file.
-   **Project Tree Summary:** Automatically generates a directory tree at the beginning of the output for a high-level overview.
-   **Smart Exclusion:**
    -   Excludes the `.git` directory by default.
    -   Automatically respects rules in `.gitignore`.
    -   Allows for a user-defined `.context_ignore` file for additional, AI-specific exclusions.
    -   Skips binary files to keep the output clean.
-   **Progress Bar:** Shows a progress bar for large repositories so you know it's working.
-   **Easy to Use:** A simple and intuitive command-line interface.

## Installation

You can install `repo-to-text-ai` directly from PyPI:

```bash
pip install repo-to-text-ai
```

## Usage

Navigate to the root directory of the Git repository you want to process and run the command:

```bash
repo-to-text-ai .
```

This will create a `context_output.txt` file in the current directory.

### Options

-   **Specify Output File:** Use the `--output` or `-o` flag to specify a different name or location for the output file.

    ```bash
    repo-to-text-ai . -o my_project_context.txt
    ```

-   **Specify Repository Path:** You can run the command from anywhere by providing the path to the repository.

    ```bash
    repo-to-text-ai /path/to/your/project
    ```

### Excluding Additional Files (`.context_ignore`)

Sometimes you want to exclude more files from the AI's context than you have in your standard `.gitignore` (e.g., test files, examples).

You can create a `.context_ignore` file in the root of your repository. It uses the exact same syntax as a `.gitignore` file.

**Example `.context_ignore`:**

```
# Exclude all test files from the AI context
tests/

# Exclude specific large data files
data/large_dataset.csv```

---

## Development

Interested in contributing? We use `pytest` for testing and `ruff`/`black` for formatting.

### Prerequisites

-   Python 3.8+
-   [Docker](https://www.docker.com/get-started') (Optional, for isolated environment)

### Local Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/zhu-weijie/repo-to-text-ai.git
    cd repo-to-text-ai
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install in editable mode with test dependencies:**
    ```bash
    pip install -e ".[test]"
    ```

4.  **Run the tests:**
    ```bash
    pytest
    ```
