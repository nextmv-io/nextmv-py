import typer
from rich import print

from nextmv.__about__ import __version__

app = typer.Typer()


@app.command()
def version() -> str:
    """
    Show the current version of the Nextmv CLI.
    """
    print(__version__)
