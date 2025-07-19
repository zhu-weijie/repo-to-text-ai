import typer
import logging
from pathlib import Path
from repo_to_text_ai.core import process_repository
from typing_extensions import Annotated
from repo_to_text_ai import __version__

app = typer.Typer()

logger = logging.getLogger("repo_to_text")


def version_callback(value: bool):
    """Prints the version of the application and exits."""
    if value:
        typer.echo(f"repo-to-text-ai version: {__version__}")
        raise typer.Exit()


def setup_logging(verbose: bool):
    log = logging.getLogger("repo_to_text")

    log.setLevel(logging.DEBUG if verbose else logging.INFO)

    if not log.handlers:
        handler = logging.StreamHandler()
        log.addHandler(handler)


@app.command()
def main(
    repo_path: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
            resolve_path=True,
            help="The path to the Git repository to process.",
        ),
    ],
    output_file: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            help="The path to the output text file.",
            resolve_path=True,
        ),
    ] = Path("context_output.txt"),
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose logging for debugging."),
    ] = False,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show the application's version and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = False,
):
    setup_logging(verbose)

    if not (repo_path / ".git").is_dir():
        typer.secho(
            f"Error: The specified path '{repo_path}' is not a valid Git repository.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    try:
        process_repository(repo_path, output_file)

        print(f"\nSuccess! Context file created at: {output_file}")

    except Exception as e:
        typer.secho(f"An unexpected error occurred: {e}", fg=typer.colors.RED, err=True)
        logger.debug("Traceback:", exc_info=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
