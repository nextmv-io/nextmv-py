from nextmv.base_model import BaseModel
from nextmv.output import Visual


class RunAsset(BaseModel):
    """
    Represents downloadable information that is part of the `Output`.

    You can import the `Asset` class directly from `nextmv`:

    ```python
    from nextmv import Asset
    ```

    An asset contains content that can be serialized to JSON and optionally
    includes visual information for rendering in the Nextmv Console.

    Parameters
    ----------
    name : str
        Name of the asset.
    content : Any
        Content of the asset. The type must be serializable to JSON.
    content_type : str, optional
        Content type of the asset. Only "json" is currently supported. Default is "json".
    description : str, optional
        Description of the asset. Default is None.
    visual : Visual, optional
        Visual schema of the asset. Default is None.

    Raises
    ------
    ValueError
        If the content_type is not "json".

    Examples
    --------
    >>> from nextmv.output import Asset, Visual, VisualSchema
    >>> visual = Visual(visual_schema=VisualSchema.CHARTJS, label="Solution Progress")
    >>> asset = Asset(
    ...     name="optimization_progress",
    ...     content={"iterations": [1, 2, 3], "values": [10, 8, 7]},
    ...     description="Optimization progress over iterations",
    ...     visual=visual
    ... )
    >>> asset.name
    'optimization_progress'
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

    content_type: str | None = "json"
    """Content type of the asset. Only `json` is allowed"""
    description: str | None = None
    """Description of the asset."""
    visual: Visual | None = None
    """Visual schema of the asset."""
