"""Cloud instance command tree for the Nextmv CLI.

All commands are built by ``cli.command()`` from pure action functions in
``nextmv.cli.actions.instance``. The ``create``, ``update``, and ``exists``
commands wrap thin actions in CLI workflows under
``nextmv.cli.cloud.instance._workflows``: ``create`` and ``update`` need to
build an ``InstanceConfiguration`` from many individual flags, while
``exists`` needs to print a JSON dict and exit with code 1 when the
instance is missing.
"""

import typer

from nextmv.cli import framework as cli
from nextmv.cli.actions.instance import (
    delete_instance,
    get_instance,
    list_instances,
)
from nextmv.cli.cloud.instance._workflows import (
    run_create_instance,
    run_instance_exists_check,
    run_update_instance,
)

app = typer.Typer()


@app.callback()
def callback() -> None:
    """
    Create and manage Nextmv Cloud application instances.

    An application instance is a representation of a version and optional
    configuration (options/parameters). Instances are the mechanism by which a
    run is made. When you make a new run, the app determines which instance to
    use and then uses the executable code associated to the version for the
    run.
    """
    pass


LIST_EXAMPLES: tuple[cli.Example, ...] = (
    ("List all instances of application [magenta]hare-app[/magenta].",
        "nextmv cloud instance list --app-id hare-app"),
    ("List all instances using the profile named [magenta]hare[/magenta].",
        "nextmv cloud instance list --app-id hare-app --profile hare"),
    ("List all instances and save the information to a [magenta]instances.json[/magenta] file.",
        "nextmv cloud instance list --app-id hare-app --output instances.json"),
)

GET_EXAMPLES: tuple[cli.Example, ...] = (
    ("Get the instance with the ID [magenta]prod[/magenta] from application [magenta]hare-app[/magenta].",
        "nextmv cloud instance get --app-id hare-app --instance-id prod"),
    ("Get the instance with the ID [magenta]prod[/magenta] and save the information to a "
        "[magenta]instance.json[/magenta] file.",
        "nextmv cloud instance get --app-id hare-app --instance-id prod --output instance.json"),
)

CREATE_EXAMPLES: tuple[cli.Example, ...] = (
    ("Create an instance for application [magenta]hare-app[/magenta] version [magenta]v1[/magenta].",
        "nextmv cloud instance create --app-id hare-app --version-id v1 --instance-id prod"),
    ("Create an instance with a specific name.",
        "nextmv cloud instance create --app-id hare-app --version-id v1 \\\n"
        '    --instance-id prod --name "Production Instance"'),
    ("Create an instance with a name and description.",
        "nextmv cloud instance create --app-id hare-app --version-id v1 \\\n"
        '    --instance-id prod --name "Production Instance" \\\n'
        '    --description "Instance for production routing jobs"'),
    ("Create an instance, or get it if it already exists.",
        "nextmv cloud instance create --app-id hare-app --version-id v1 \\\n"
        "    --instance-id prod --exist-ok"),
    ("Create an instance with configuration options.",
        "nextmv cloud instance create --app-id hare-app --version-id v1 \\\n"
        "    --instance-id prod --execution-class 6c9500mb870s --priority 1"),
    ("Create an instance with runtime options.",
        "nextmv cloud instance create --app-id hare-app --version-id v1 \\\n"
        "    --instance-id prod --options max_duration=30 --options timeout=60"),
)

UPDATE_EXAMPLES: tuple[cli.Example, ...] = (
    ("Update an instance's name.",
        'nextmv cloud instance update --app-id hare-app --instance-id prod --name "Production Instance"'),
    ("Update an instance's description.",
        "nextmv cloud instance update --app-id hare-app --instance-id prod \\\n"
        '    --description "Instance for production routing jobs"'),
    ("Update an instance to use a different version.",
        "nextmv cloud instance update --app-id hare-app --instance-id prod --version-id v2"),
    ("Update an instance's name and description at once.",
        "nextmv cloud instance update --app-id hare-app --instance-id prod \\\n"
        '    --name "Production Instance" --description "Instance for production routing jobs"'),
    ("Update an instance and save the updated information to a [magenta]updated_instance.json[/magenta] file.",
        "nextmv cloud instance update --app-id hare-app --instance-id prod \\\n"
        '    --name "Production Instance" --output updated_instance.json'),
    ("Update an instance's execution class and priority.",
        "nextmv cloud instance update --app-id hare-app --instance-id prod \\\n"
        "    --execution-class 6c9500mb870s --priority 1"),
    ("Update an instance's runtime options.",
        "nextmv cloud instance update --app-id hare-app --instance-id prod \\\n"
        "    --options max_duration=30 --options timeout=60"),
)

DELETE_EXAMPLES: tuple[cli.Example, ...] = (
    ("Delete the instance with the ID [magenta]prod[/magenta] from application [magenta]hare-app[/magenta].",
        "nextmv cloud instance delete --app-id hare-app --instance-id prod"),
)

EXISTS_EXAMPLES: tuple[cli.Example, ...] = (
    ("Check if the instance with the ID [magenta]prod[/magenta] exists in application [magenta]hare-app[/magenta].",
        "nextmv cloud instance exists --app-id hare-app --instance-id prod"),
    ("Check if the instance exists using the profile named [magenta]hare[/magenta].",
        "nextmv cloud instance exists --app-id hare-app --instance-id prod --profile hare"),
)


list = cli.command(  # noqa: A001 — shadows the builtin intentionally
    app,
    list_instances,
    name="list",
    progress="Listing instances...",
    output_flag=True,
    saved_noun="Instance list information",
    examples=LIST_EXAMPLES,
)

get = cli.command(
    app,
    get_instance,
    name="get",
    progress="Getting instance...",
    output_flag=True,
    saved_noun="Instance information",
    examples=GET_EXAMPLES,
)

# `create` uses handles_own_output=True because run_create_instance builds
# an InstanceConfiguration from many individual flags before calling the
# thin action and printing the JSON result.
create = cli.command(
    app,
    run_create_instance,
    name="create",
    handles_own_output=True,
    examples=CREATE_EXAMPLES,
)

# `update` uses handles_own_output=True because run_update_instance builds
# an InstanceConfiguration from many individual flags, prints a custom
# success message, and uses --output/-u (the -u short flag avoids the
# collision with --options/-o that --output/-o would cause).
update = cli.command(
    app,
    run_update_instance,
    name="update",
    handles_own_output=True,
    examples=UPDATE_EXAMPLES,
)

delete = cli.command(
    app,
    delete_instance,
    name="delete",
    progress="Deleting instance...",
    delete_confirm=cli.DeleteConfirmation(
        confirm=(
            "Are you sure you want to delete instance "
            "[magenta]{instance_id}[/magenta] from application "
            "[magenta]{app_id}[/magenta]? This action cannot be undone."
        ),
        decline="Instance [magenta]{instance_id}[/magenta] will not be deleted.",
        succeeded=(
            "Instance [magenta]{instance_id}[/magenta] deleted successfully "
            "from application [magenta]{app_id}[/magenta]."
        ),
    ),
    examples=DELETE_EXAMPLES,
)

# `exists` uses handles_own_output=True because it needs to print a JSON
# dict and exit with code 1 when the instance does not exist.
exists = cli.command(
    app,
    run_instance_exists_check,
    name="exists",
    progress="Checking if instance exists...",
    handles_own_output=True,
    examples=EXISTS_EXAMPLES,
)
