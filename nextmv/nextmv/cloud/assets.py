from nextmv.base_model import BaseModel
from nextmv.output import Visual


class RunAsset(BaseModel):
    """
    Represents an asset associated with a Nextmv Cloud run.

    You can import the `RunAsset` class from `nextmv.cloud`:

    ```python
    from nextmv.cloud import RunAsset
    ```

    A run asset represents metadata about an asset associated with a Nextmv Cloud run.

    Parameters
    ----------
    id : str
        Unique identifier of the asset.
    run_id : str
        Identifier of the run associated with the asset.
    name : str
        Name of the asset.
    created_at : str
        Timestamp of when the asset was created.
    size : int
        Size of the asset content in bytes.
    content_type : str
        Content type of the asset. Only `json` is allowed at the moment.
    visual : Visual | None, optional
        Visual schema of the asset, by default None.
    """

    id: str
    """Unique identifier of the asset."""
    run_id: str
    """Identifier of the run associated with the asset."""
    name: str
    """Name of the asset."""
    created_at: str
    """Timestamp of when the asset was created."""
    size: int
    """Size of the asset content in bytes."""
    content_type: str
    """Content type of the asset. Only `json` is allowed at the moment."""
    visual: Visual | None = None
    """Visual schema of the asset."""
