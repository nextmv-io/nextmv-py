import rich
import typer


def error(msg: str) -> None:
    """
    Pretty-print an error message and exit with code 1. Your message should end
    with a period.

    Parameters
    ----------
    msg : str
        The error message to display.

    Raises
    ------
    typer.Exit
        Exits the program with code 1.
    """

    rich.print(f"[red]Error:[/red] {msg}")
    raise typer.Exit(code=1)
