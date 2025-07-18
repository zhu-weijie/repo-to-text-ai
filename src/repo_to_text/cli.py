import typer
from pathlib import Path
from repo_to_text.core import process_repository
from typing_extensions import Annotated

app = typer.Typer()


@app.command(name="repo-to-text")
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
):
    try:
        typer.echo(f"Processing repository at: {repo_path}")
        process_repository(repo_path, output_file)
        typer.secho(
            f"Success! Context file created at: {output_file}", fg=typer.colors.GREEN
        )
    except Exception as e:
        typer.secho(f"An error occurred: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
