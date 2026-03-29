import json

import plotly.graph_objects as go

import nextmv


def allocation_chart(
    allocations: list[dict],
    num_warehouses: int,
    num_stores: int,
    warehouse_labels: list[str] | None = None,
    store_labels: list[str] | None = None,
    tab_order: int = 1,
) -> nextmv.Asset:
    """
    Create a Sankey diagram showing unit flow from warehouses to stores.

    Parameters
    ----------
    allocations : list[dict]
        List of allocation records, each containing keys ``"warehouse"``
        (int index), ``"store"`` (int index), and ``"units"`` (numeric).
    num_warehouses : int
        Total number of warehouses (used to offset store node indices).
    num_stores : int
        Total number of stores.
    warehouse_labels : list[str], optional
        Display labels for warehouses. Defaults to
        ``["Warehouse 0", "Warehouse 1", ...]``.
    store_labels : list[str], optional
        Display labels for stores. Defaults to
        ``["Store 0", "Store 1", ...]``.
    tab_order : int, optional
        Tab order for the visual asset in the UI. Defaults to ``1``.

    Returns
    -------
    nextmv.Asset
        A Nextmv asset containing the Plotly Sankey figure as a custom-tab
        visual.
    """
    W = num_warehouses
    if warehouse_labels is None:
        warehouse_labels = [f"Warehouse {w}" for w in range(W)]
    if store_labels is None:
        store_labels = [f"Store {s}" for s in range(num_stores)]

    labels = list(warehouse_labels) + list(store_labels)

    sources = [a["warehouse"] for a in allocations]
    targets = [W + a["store"] for a in allocations]
    units = [a["units"] for a in allocations]

    fig = go.Figure(
        go.Sankey(
            node={
                "pad": 15,
                "thickness": 20,
                "line": {"color": "black", "width": 0.5},
                "label": labels,
                "color": ["#4e79a7"] * W + ["#f28e2b"] * num_stores,
            },
            link={
                "source": sources,
                "target": targets,
                "value": units,
            },
        )
    )

    fig.update_layout(
        title="Inventory Allocation: Warehouses to Stores",
        font_size=12,
        width=900,
        height=600,
    )

    return nextmv.Asset(
        name="Allocation Flow",
        content_type="json",
        visual=nextmv.Visual(
            visual_schema=nextmv.VisualSchema(value="plotly"),
            visual_type="custom-tab",
            label="Allocation Flow",
            tab_order=tab_order,
        ),
        content=[json.loads(fig.to_json())],
    )
