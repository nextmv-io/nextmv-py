"""
GeoJSON visualization handler module.

This module provides functionality to handle GeoJSON visualizations by converting
them to interactive HTML maps using Folium. It supports various GeoJSON formats
and automatically calculates optimal map positioning and zoom levels.

Functions
---------
handle_geojson_visual
    Handle and write GeoJSON visuals to HTML files.
extract_coordinates
    Recursively extract coordinates from nested coordinate structures.
calculate_map_center_and_zoom
    Calculate the optimal center and zoom level for a GeoJSON map.
extract_geojson_fields
    Extract available fields for tooltip and popup from GeoJSON data.
create_geojson_map
    Create a folium map with GeoJSON data.
"""

import json
import os

import folium

from nextmv.logger import log
from nextmv.output import Asset


def handle_geojson_visual(asset: Asset, visuals_dir: str) -> None:
    """
    Handle and write GeoJSON visuals to HTML files.

    This function processes GeoJSON visualization assets and converts them to
    interactive HTML maps using Folium. It handles multiple content formats
    including dictionaries, lists, and JSON strings. Each visualization is
    converted to a map with appropriate positioning and saved as an HTML file.

    Parameters
    ----------
    asset : Asset
        The asset containing the GeoJSON visualization data. The content can be
        a dictionary (single GeoJSON), a list (multiple GeoJSONs), or a JSON
        string representation.
    visuals_dir : str
        The directory path where the HTML files will be written.

    Notes
    -----
    - For list content, each GeoJSON is saved with an index suffix
      (e.g., "map_0.html", "map_1.html")
    - For dict content, the GeoJSON is saved with the asset label
      (e.g., "map.html")
    - String content is parsed as JSON before processing
    - Invalid JSON strings or unsupported content types are ignored with
      appropriate logging
    """
    if isinstance(asset.content, list):
        for ix, content in enumerate(asset.content):
            if isinstance(content, dict):
                layer_name = f"{asset.visual.label} Layer {ix + 1}"
                m = create_geojson_map(content, layer_name)
                m.save(os.path.join(visuals_dir, f"{asset.visual.label}_{ix}.html"))
        return

    if isinstance(asset.content, dict):
        layer_name = f"{asset.visual.label} Layer"
        m = create_geojson_map(asset.content, layer_name)
        m.save(os.path.join(visuals_dir, f"{asset.visual.label}.html"))
        return

    if isinstance(asset.content, str):
        try:
            geojson_data = json.loads(asset.content)
            layer_name = f"{asset.visual.label} Layer"
            m = create_geojson_map(geojson_data, layer_name)
            m.save(os.path.join(visuals_dir, f"{asset.visual.label}.html"))
        except json.JSONDecodeError:
            log(f"Warning: Could not parse GeoJSON string content for {asset.visual.label}")
        return

    # If there is a different content type for geojson visuals, we ignore it for now


def extract_coordinates(coords, all_coords) -> None:
    """
    Recursively extract coordinates from nested coordinate structures.

    This function traverses nested coordinate structures commonly found in
    GeoJSON geometries and extracts all coordinate pairs. It handles various
    geometry types by recursively processing nested arrays until it finds
    coordinate pairs in [longitude, latitude] format.

    Parameters
    ----------
    coords : list or tuple
        The coordinate structure to extract from. Can be a nested list/tuple
        containing coordinate pairs or other nested structures.
    all_coords : list
        A list to accumulate all extracted coordinate pairs. This list is
        modified in-place to store [longitude, latitude] pairs.

    Notes
    -----
    - Coordinate pairs are identified as lists/tuples with exactly 2 numeric
      elements
    - The function expects coordinates in [longitude, latitude] format as per
      GeoJSON specification
    - Nested structures are recursively processed to handle complex geometries
      like Polygons and MultiPolygons
    """
    if isinstance(coords, list):
        if len(coords) == 2 and isinstance(coords[0], (int, float)) and isinstance(coords[1], (int, float)):
            # This is a coordinate pair [lon, lat]
            all_coords.append(coords)
        else:
            # This is a nested structure, recurse
            for coord in coords:
                extract_coordinates(coord, all_coords)


def calculate_map_center_and_zoom(geojson_data: dict) -> tuple[float, float, int]:
    """
    Calculate the optimal center and zoom level for a GeoJSON map.

    This function analyzes the geographic extent of GeoJSON features to
    determine the best map center point and zoom level for visualization.
    It extracts all coordinates from the features, calculates the centroid,
    and determines an appropriate zoom level based on the data's geographic
    spread.

    Parameters
    ----------
    geojson_data : dict
        A GeoJSON object containing features with geometric data. Should
        follow the GeoJSON specification with a "features" key containing
        an array of feature objects.

    Returns
    -------
    tuple[float, float, int]
        A tuple containing (center_latitude, center_longitude, zoom_level).
        - center_latitude : float
            The latitude coordinate for the map center
        - center_longitude : float
            The longitude coordinate for the map center
        - zoom_level : int
            The recommended zoom level (typically 4-12)

    Notes
    -----
    - Default center is New York City (40.7128, -74.0060) with zoom level 12
    - Zoom levels are calculated based on coordinate range:
      - Range > 10 degrees: zoom level 4 (continental view)
      - Range > 1 degree: zoom level 8 (regional view)
      - Range > 0.1 degree: zoom level 10 (city view)
      - Smaller ranges: zoom level 12 (neighborhood view)
    - Falls back to defaults if no valid coordinates are found or errors occur
    """
    default_lat, default_lon, default_zoom = 40.7128, -74.0060, 12

    try:
        if "features" not in geojson_data or not geojson_data["features"]:
            return default_lat, default_lon, default_zoom

        # Calculate bounds from all features
        all_coords = []
        for feature in geojson_data["features"]:
            if feature.get("geometry", {}).get("coordinates"):
                coords = feature["geometry"]["coordinates"]
                extract_coordinates(coords, all_coords)

        if not all_coords:
            return default_lat, default_lon, default_zoom

        lats = [coord[1] for coord in all_coords]
        lons = [coord[0] for coord in all_coords]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)

        # Adjust zoom based on coordinate spread
        lat_range = max(lats) - min(lats)
        lon_range = max(lons) - min(lons)
        max_range = max(lat_range, lon_range)

        if max_range > 10:
            zoom_level = 4
        elif max_range > 1:
            zoom_level = 8
        elif max_range > 0.1:
            zoom_level = 10
        else:
            zoom_level = default_zoom

        return center_lat, center_lon, zoom_level

    except (KeyError, TypeError, ValueError, IndexError) as e:
        log(f"Warning: Error calculating map center and zoom from GeoJSON data: {e}")
        return default_lat, default_lon, default_zoom
    except Exception as e:
        log(f"Warning: Unexpected error calculating map center and zoom: {e}")
        return default_lat, default_lon, default_zoom


def extract_geojson_fields(geojson_data: dict) -> tuple[list[str], list[str]]:
    """
    Extract available fields for tooltip and popup from GeoJSON data.

    This function analyzes the properties of GeoJSON features to identify
    suitable fields for displaying in map tooltips and popups. It prioritizes
    common field names and limits the number of fields to maintain usability.

    Parameters
    ----------
    geojson_data : dict
        A GeoJSON object containing features with properties. Should follow
        the GeoJSON specification with features containing properties objects.

    Returns
    -------
    tuple[list[str], list[str]]
        A tuple containing (tooltip_fields, popup_fields).
        - tooltip_fields : list[str]
            List of field names suitable for tooltips (max 3 fields)
        - popup_fields : list[str]
            List of field names suitable for popups (max 5 fields)

    Notes
    -----
    - Prioritizes common field names: "name", "title", "label", "id",
      "popupContent", "description"
    - Tooltip fields are limited to 3 to prevent overcrowding
    - Popup fields are limited to 5 to maintain readability
    - Returns empty lists if no features or properties are found
    - Gracefully handles malformed GeoJSON data by returning empty lists
    """
    tooltip_fields = []
    popup_fields = []

    try:
        if "features" not in geojson_data or not geojson_data["features"]:
            return tooltip_fields, popup_fields

        # Get fields from the first feature's properties
        first_feature = geojson_data["features"][0]
        if "properties" not in first_feature or not first_feature["properties"]:
            return tooltip_fields, popup_fields

        available_fields = list(first_feature["properties"].keys())
        # Prioritize common field names for tooltip/popup
        priority_fields = ["name", "title", "label", "id", "popupContent", "description"]

        for field in priority_fields:
            if field in available_fields:
                tooltip_fields.append(field)
                popup_fields.append(field)

        # Add remaining fields up to a reasonable limit
        for field in available_fields:
            if field not in tooltip_fields and len(tooltip_fields) < 3:
                tooltip_fields.append(field)
            if field not in popup_fields and len(popup_fields) < 5:
                popup_fields.append(field)

    except (KeyError, TypeError, IndexError) as e:
        log(f"Warning: Error extracting GeoJSON fields: {e}")
    except Exception as e:
        log(f"Warning: Unexpected error extracting GeoJSON fields: {e}")

    return tooltip_fields, popup_fields


def create_geojson_map(geojson_data: dict, layer_name: str = "GeoJSON Layer") -> folium.Map:
    """
    Create a folium map with GeoJSON data.

    This function creates an interactive map using Folium with the provided
    GeoJSON data. It automatically calculates the optimal center point and
    zoom level, extracts relevant fields for tooltips and popups, and
    configures the map with appropriate interactive features.

    Parameters
    ----------
    geojson_data : dict
        A GeoJSON object containing the geographic data to display. Should
        follow the GeoJSON specification with features and geometries.
    layer_name : str, optional
        The name to assign to the GeoJSON layer in the map, by default
        "GeoJSON Layer". This name appears in the layer control widget.

    Returns
    -------
    folium.Map
        A configured Folium map object with the GeoJSON data added as a layer.
        The map includes tooltips, popups, and layer controls when applicable.

    Notes
    -----
    - Map center and zoom are automatically calculated based on the data extent
    - Tooltips are added if suitable fields are found in feature properties
    - Popups are added if suitable fields are found in feature properties
    - Layer control is always added to allow toggling of the GeoJSON layer
    - The map uses default Folium styling and can be further customized
    """
    center_lat, center_lon, zoom_level = calculate_map_center_and_zoom(geojson_data)
    tooltip_fields, popup_fields = extract_geojson_fields(geojson_data)

    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level)

    # Create GeoJson layer with dynamic tooltip and popup configuration
    geojson_kwargs = {"name": layer_name}

    if tooltip_fields:
        geojson_kwargs["tooltip"] = folium.GeoJsonTooltip(fields=tooltip_fields)

    if popup_fields:
        geojson_kwargs["popup"] = folium.GeoJsonPopup(fields=popup_fields)

    folium.GeoJson(geojson_data, **geojson_kwargs).add_to(m)
    folium.LayerControl().add_to(m)

    return m
