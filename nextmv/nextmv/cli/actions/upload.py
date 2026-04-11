"""Core upload URL actions.

Pure functions that wrap SDK calls for creating Nextmv Cloud upload URLs.
"""

from typing import Any

from nextmv.cli.framework.options import AppIdRequiredOption
from nextmv.cloud import Application, Client


def create_upload_url(
    client: Client,
    app_id: AppIdRequiredOption,
) -> dict[str, Any]:
    """Create a new Nextmv Cloud application upload URL.

    Returns an upload URL dict containing the pre-signed ``upload_url``
    and the generated ``upload_id``. The URL is valid for 10 minutes.
    Use the upload URL with ``nextmv cloud data upload`` (or the SDK's
    ``upload_data``) to send the actual data.
    """
    app = Application(client=client, id=app_id)
    return app.upload_url().to_dict()
