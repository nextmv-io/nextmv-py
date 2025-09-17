"""
Plotly visualization handler module.

This module provides functionality to handle Plotly visualizations by converting
them to HTML files for local run processing.

Functions
---------
handle_plotly_visual
    Handle and write Plotly visuals to HTML files.
"""

import json
import os

import plotly.io as pio

from nextmv.output import Asset


def handle_plotly_visual(asset: Asset, visuals_dir: str) -> None:
    """
    Handle and write Plotly visuals to HTML files.

    This function processes Plotly visualization assets and converts them to
    HTML files. It handles both single visualizations (dict content) and
    multiple visualizations (list content). Each visualization is converted
    from JSON format to a Plotly figure and then saved as an HTML file.

    Parameters
    ----------
    asset : Asset
        The asset containing the Plotly visualization data. The content can be
        either a dictionary (single visualization) or a list (multiple
        visualizations).
    visuals_dir : str
        The directory path where the HTML files will be written.

    Notes
    -----
    - For list content, each visualization is saved with an index suffix
      (e.g., "chart_0.html", "chart_1.html")
    - For dict content, the visualization is saved with the asset label
      (e.g., "chart.html")
    - Content types other than dict or list are currently ignored
    """
    if isinstance(asset.content, list):
        for ix, content in enumerate(asset.content):
            fig = pio.from_json(json.dumps(content))
            fig.write_html(os.path.join(visuals_dir, f"{asset.visual.label}_{ix}.html"))

        return

    if isinstance(asset.content, dict):
        fig = pio.from_json(json.dumps(asset.content))
        fig.write_html(os.path.join(visuals_dir, f"{asset.visual.label}.html"))

        return

    # If there is a different content type for plotly visuals, we ignore it for
    # now.
