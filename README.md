# Repo-to-Text-AI

**Turn an entire Git repository into a single, organized text file designed for providing context to Large Language Models (LLMs).**

`repo-to-text-ai` is a versatile command-line tool that intelligently scans a local repository and consolidates all relevant files into one output file. It's designed to be the perfect first step for pasting a complete project context into an AI prompt for code analysis, documentation generation, refactoring, or feature development.

The tool is smart, respecting `.gitignore` rules, and highly customizable, allowing you to fine-tune the included context to be as precise as you need.

---

## Key Features

-   **Single File Output:** Combines all relevant source files into one `.txt` file, ready for copy-pasting.
-   **Project Tree Summary:** Automatically generates a directory tree at the beginning of the output for a high-level overview of the repository structure.
-   **Intelligent File Filtering:**
    -   Automatically respects rules in all `.gitignore` files, including those in subdirectories.
    -   Skips binary files, the `.git` directory, and other meta-files.
-   **Highly Customizable Context:**
    -   **Blacklist (`.context_ignore`):** Use a `.context_ignore` file to exclude additional files or directories from the output without modifying your main `.gitignore`.
    -   **Whitelist (`.context`):** For maximum precision, use a `.context` file to specify *exactly* which files and directories should be included.
-   **User-Friendly CLI:** A simple and intuitive command-line interface with a progress bar for large repositories.

## Installation

You can install `repo-to-text-ai` directly from the Python Package Index (PyPI):

```bash
pip install repo-to-text-ai
```

## Usage

### Basic Usage

Navigate to the root directory of the Git repository you want to process and run the command:

```bash
repo-to-text-ai .
```

This will create a `context_output.txt` file in the current directory containing the consolidated context.

### Command-Line Options

| Option                | Short | Description                                       |
| --------------------- | ----- | ------------------------------------------------- |
| `--output <file>`     | `-o`  | Specify a path for the output file.               |
| `--verbose`           | `-v`  | Enable detailed debug logging.                    |
| `--version`           |       | Display the installed version of the tool.        |

**Example with options:**

```bash
# Run on a different project and save the output to a specific file
repo-to-text-ai /path/to/your/project -o my_project.txt
```

---

## Customizing the Context

You have two powerful methods to control exactly what content goes into the output file.

### 1. The Blacklist Method: `.context_ignore`

This is the best method for excluding a few extra files or directories that are not in your main `.gitignore`.

Create a file named `.context_ignore` in the root of your repository. It uses the exact same syntax as a `.gitignore` file.

**Use Case:** You want to exclude test files or examples from the AI's context without adding them to your project's primary `.gitignore`.

**Example `.context_ignore`:**

```gitignore
# Exclude all test files from the AI context
tests/
examples/

# Exclude specific large data files
data/large_dataset.csv
```

### 2. The Whitelist Method: `.context`

This is the most precise method. If a `.context` file is found in the root of your repository, **only the files and directories listed in it will be included**. All other files will be ignored.

Create a file named `.context` in the root of your repository. List the paths you want to include, one per line.

**Use Case:** You are working on a specific feature and only want to provide the AI with context from two directories and one configuration file.

**Example `.context`:**

```
# This is a comment, it will be ignored

# Include the main application file and the entire 'utils' directory
src/app.py
src/utils/

# Also include the main configuration file
config/settings.yml
```
**Note:** Even when using a `.context` whitelist, the exclusion rules from your `.gitignore` and `.context_ignore` files are **still respected**. For example, if `src/utils/` contains a `temp.log` file and your `.gitignore` excludes `*.log`, that file will not be included in the output.

---

## Development

Interested in contributing? We use `pytest` for testing and `ruff`/`black` for formatting and linting.

### Prerequisites

-   Python 3.8+
-   [Docker](https://www.docker.com/get-started) (Recommended for a consistent, isolated environment)

### Local Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/repo-to-text-ai.git
    cd repo-to-text-ai
    ```

2.  **Create and activate a virtual environment:**
    ```bash
sh
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install in editable mode with test dependencies:**
    This command links the package to your source files and installs development tools like `pytest`.
    ```bash
    pip install -e ".[test]"
    ```

4.  **Run the tests:**
    ```bash
    pytest
    ```
