"""Core data upload actions.

Pure functions that wrap SDK calls for uploading data payloads to a
pre-signed Nextmv Cloud upload URL. The CLI path also supports stdin
piping and tar-file packaging; those are CLI-frontend concerns and live
in ``nextmv/cli/cloud/data/_workflows.py``.
"""

from typing import Any

from nextmv.cli.framework.options import AppIdRequiredOption
from nextmv.cloud import Application, Client


def upload_data(
    client: Client,
    app_id: AppIdRequiredOption,
    upload_url: str,
    data: Any | None = None,
    tar_file: str | None = None,
) -> None:
    """Upload data to a pre-signed Nextmv Cloud upload URL.

    Provide exactly one of ``data`` (a text/JSON payload) or ``tar_file``
    (a path to a ``.tar.gz`` containing multi-file input). The upload
    URL must be obtained first via ``create_upload_url``.
    """
    app = Application(client=client, id=app_id)
    if tar_file is not None:
        app.upload_data(upload_url=upload_url, tar_file=tar_file)
        return
    app.upload_data(upload_url=upload_url, data=data)
