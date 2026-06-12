"""
This module defines the local run compare command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from nextmv.cli.configuration.config import build_local_app
from nextmv.cli.message import error, in_progress, print_json, rule, success
from nextmv.cli.options import DebugOption, LocalAppIDOption, LocalAppSrcOption
from nextmv.run import RunComparison

# Set up subcommand application.
app = typer.Typer()
console = Console()


@app.command()
def compare(
    run_ids: Annotated[
        list[str],
        typer.Option(
            "--run-ids",
            "-r",
            help="List of run IDs to compare. Pass multiple run IDs by repeating the flag, or separating with commas.",
            metavar="RUN_IDS",
        ),
    ],
    app_id: LocalAppIDOption = None,
    app_src: LocalAppSrcOption = ".",
    flat: Annotated[
        bool,
        typer.Option(
            "--flat",
            "-f",
            help="Print the comparison result as [magenta]json[/magenta], instead of a table.",
        ),
    ] = False,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the comparison result to this location. Activates the --flat option.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    _: DebugOption = False,
) -> None:
    """
    Compare multiple Nextmv local application runs.

    By default this command prints a human-readable table to
    [magenta]stdout[/magenta]. You may use the --flat option to print the
    comparison result to [magenta]stdout[/magenta] as [magenta]json[/magenta]
    instead. When the --output option is used, the --flat flag is automatically
    activated and the result is saved as [magenta]json[/magenta].

    [bold][underline]Examples[/underline][/bold]

    - Compare two runs belonging to an app with ID [magenta]hare-app[/magenta]
      repeating the --run-ids flag.
        $ [dim]nextmv local run compare --app-id hare-app --run-ids fluff --run-ids white[/dim]

    - Compare three runs belonging to an app with ID [magenta]hare-app[/magenta]
      separating the run IDs with commas.
        $ [dim]nextmv local run compare --app-id hare-app --run-ids fluff,white,thumper[/dim]

    - Compare two runs and print the result as [magenta]json[/magenta].
        $ [dim]nextmv local run compare --app-id hare-app --run-ids fluff,white --flat[/dim]

    - Compare two runs and save the result to a file named [magenta]comparison.json[/magenta].
        $ [dim]nextmv local run compare --app-id hare-app --run-ids fluff,white --output comparison.json[/dim]
    """

    # Parse the run IDs to gather the final list.
    run_id_list = []
    for run_id in run_ids:
        sub_ids = run_id.split(",")
        for sub_id in sub_ids:
            run_id_list.append(sub_id.strip())

    found = set()
    for run_id in run_id_list:
        if run_id in found:
            error(f"Duplicate run ID found: [magenta]{run_id}[/magenta]. Please provide unique run IDs for comparison.")

        found.add(run_id)

    local_app = build_local_app(app_src, app_id)
    in_progress(msg="Comparing runs...")
    comparison = local_app.compare_runs(run_ids=run_id_list)
    comparison_dict = comparison.to_flat_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(comparison_dict, f, indent=2)

        success(msg=f"Run comparison saved to [magenta]{output}[/magenta].")

        return

    if flat:
        print_json(comparison_dict)
        return

    _print_table(comparison)


def _print_table(comparison: RunComparison) -> None:
    """
    Auxiliary function to handle the printing of the comparison result as
    tables. This mostly orchestrates calling tables for different elements of
    the comparison.

    Parameters
    ----------
    comparison: RunComparison
        The object containing the results of the run comparison.
    """

    table_styling_kwargs = {
        "border_style": "cyan",
        "header_style": "cyan",
        "title_style": "magenta bold",
        "title_justify": "left",
    }

    _print_comparison_table(
        title="Information",
        first_column="Field",
        run_ids=comparison.run_ids,
        data=comparison.information,
        table_styling_kwargs=table_styling_kwargs,
        highlight_differences=False,
    )

    _print_comparison_table(
        title="Metadata",
        first_column="Field",
        run_ids=comparison.run_ids,
        data=comparison.metadata,
        table_styling_kwargs=table_styling_kwargs,
    )

    if comparison.metrics:
        _print_comparison_table(
            title="Metrics",
            first_column="Metric",
            run_ids=comparison.run_ids,
            data=comparison.metrics,
            table_styling_kwargs=table_styling_kwargs,
        )

    if comparison.options:
        _print_comparison_table(
            title="Options",
            first_column="Option",
            run_ids=comparison.run_ids,
            data=comparison.options,
            table_styling_kwargs=table_styling_kwargs,
        )


def _print_comparison_table(
    title: str,
    first_column: str,
    run_ids: list[str],
    data: dict,
    table_styling_kwargs: dict,
    highlight_differences: bool = True,
) -> None:
    """
    Auxiliary function to print a specific section of the comparison result as
    a table.

    Parameters
    ----------
    title: str
        The title of the table to be printed.
    first_column: str
        The name of the first column of the table, which contains the name of
        the field/metric/option being compared.
    run_ids: list[str]
        The list of run IDs being compared. This is used to print the values of
        each field/metric/option for each run in the correct order.
    data: dict
        The actual data to be printed in the table. This is a dictionary where
        the keys are the names of the fields/metrics/options being compared,
        and the values are ComparisonValues objects that contain the values for
        each run and whether there are differences across runs.
    table_styling_kwargs: dict
        A dictionary containing styling options for the table, such as border style, header style, title style, etc.
    highlight_differences: bool
        Whether to highlight rows with differences across runs.
    """

    table = Table(first_column, *run_ids, title=title, **table_styling_kwargs)

    for field, comp_values in data.items():
        style_kwargs = {"style": "italic yellow"} if highlight_differences and comp_values.has_differences else {}
        table.add_row(
            field,
            *[str(comp_values.values.get(run_id, "")) for run_id in run_ids],
            **style_kwargs,
        )

    rule()
    console.print(table)
