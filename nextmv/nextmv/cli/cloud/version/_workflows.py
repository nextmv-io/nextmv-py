"""CLI-only workflows for the cloud version domain.

These functions wrap thin actions in ``nextmv.cli.actions.version`` with
CLI-specific behavior that shouldn't bleed into the action layer (e.g.
setting a non-zero exit code when a check returns ``False``).
"""

import typer

from nextmv.cli.actions.version import version_exists
from nextmv.cli.framework.options import AppIdRequiredOption, VersionIdOption
from nextmv.cli.message import print_json
from nextmv.cloud.client import Client


def run_version_exists_check(
    client: Client,
    app_id: AppIdRequiredOption,
    version_id: VersionIdOption,
) -> None:
    """Check whether a Nextmv Cloud application version exists.

    Prints ``{"exists": true}`` or ``{"exists": false}`` as JSON. Exits with
    code 1 if the version does not exist, so the command can be used in
    shell scripts:

    .. code-block:: bash

        if nextmv cloud version exists --app-id hare-app --version-id v1; then
            echo "version exists"
        fi
    """
    ok = version_exists(client, app_id=app_id, version_id=version_id)
    print_json({"exists": ok})
    if not ok:
        raise typer.Exit(code=1)
