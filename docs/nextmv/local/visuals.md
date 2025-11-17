# Run visuals

If your local app produces visual assets as part of its output, you can view
them using the [`Application.run_visuals`][app-run-visuals] method.

```python
from nextmv import local

app = local.Application(src="<YOUR_APP_SRC>") # Path to your local app, where the app.yaml manifest is located.
app.run_visuals(run_id="<YOUR_RUN_ID>") # The ID of the run you want to visualize.
```

This will open a web browser tab with the visual assets produced by the run. If
your app does not produce any visual assets, this method will do nothing.

The visual assets are typically `.html` files stored under the
`.nextmv/runs/<RUN_ID>/visuals` directory of your local app. One browser tab
will be opened for each visual asset produced in that run.

These run visuals are similar to the ones produced by the Nextmv Console, so
you can use this method to preview the visuals locally before pushing your app
to Nextmv Cloud.

## Requirements for creating visual assets

To enable the `run_visuals` method to render your visualizations, you must
create assets that conform to the supported visualization schemas. Local runs
currently support **two visualization libraries**:

1. **Plotly** - for interactive charts and graphs
2. **Folium** (via GeoJSON) - for interactive maps

!!! important "Required dependencies"

    The `folium` and `plotly` packages are required for local run visualization.
    Install them with:

    ```bash
    pip install nextmv[all]
    ```

### Supported visualization schemas

Visual assets are defined using the `VisualSchema` enum, which specifies how
the asset content should be rendered:

* **`VisualSchema.PLOTLY`** - Renders content using Plotly's JSON format
* **`VisualSchema.GEOJSON`** - Renders content as GeoJSON on an interactive map
* **`VisualSchema.CHARTJS`** - Not supported for local runs (only available in
  Nextmv Console)

### Creating Plotly visualizations

To create a Plotly visualization, your asset must contain JSON-serializable
content that represents a valid Plotly figure. Here's how to structure your
assets:

```python
import json
import plotly.graph_objects as go
import nextmv

# Create a Plotly figure
fig = go.Figure()
fig.add_trace(go.Bar(x=["A", "B", "C"], y=[10, 20, 15]))
fig.update_layout(title="Example Chart")

# Convert to JSON format
fig_json = fig.to_json()

# Create the asset with PLOTLY schema
asset = nextmv.Asset(
    name="example_chart",
    content=[json.loads(fig_json)],  # Content must be a list of dicts or a single dict
    content_type="json",
    visual=nextmv.Visual(
        visual_schema=nextmv.VisualSchema.PLOTLY,
        label="My Chart",
        visual_type="custom-tab"
    )
)
```

**Key requirements for Plotly assets:**

* The `content` field must contain JSON-serializable data representing a Plotly
  figure
* Content can be:
  * A **dictionary** (single visualization)
  * A **list of dictionaries** (multiple visualizations)
* Each content item should be the JSON representation of a Plotly figure
  (typically obtained via `fig.to_json()` followed by `json.loads()`)
* Set `visual_schema` to `VisualSchema.PLOTLY`

### Creating GeoJSON (map) visualizations

To create a map visualization, your asset must contain valid GeoJSON data. The
system uses Folium to render interactive maps:

```python
import nextmv

# Create GeoJSON data
geojson_data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [-122.4194, 37.7749]  # [longitude, latitude]
            },
            "properties": {
                "name": "San Francisco",
                "description": "City location"
            }
        }
    ]
}

# Create the asset with GEOJSON schema
asset = nextmv.Asset(
    name="location_map",
    content=geojson_data,  # Can be dict, list of dicts, or JSON string
    content_type="json",
    visual=nextmv.Visual(
        visual_schema=nextmv.VisualSchema.GEOJSON,
        label="Route Map",
        visual_type="custom-tab"
    )
)
```

**Key requirements for GeoJSON assets:**

* The `content` field must contain valid GeoJSON data conforming to the
  [GeoJSON specification][geojson-spec]
* Content can be:
  * A **dictionary** (single GeoJSON object)
  * A **list of dictionaries** (multiple GeoJSON objects)
  * A **JSON string** (will be parsed automatically)
* GeoJSON should follow the standard structure with `type` and `features` or
  geometry objects
* Set `visual_schema` to `VisualSchema.GEOJSON`
* Maps automatically calculate optimal center and zoom level
* Feature properties can be used for tooltips and popups (common fields like
  `name`, `title`, `description` are prioritized)

### Including assets in your output

Once you've created your assets, include them in your output:

```python
import nextmv

# Create your visual assets
assets = [plotly_asset, geojson_asset]  # List of Asset objects

# Include in output
output = nextmv.Output(
    solution={"result": "your solution"},
    statistics=nextmv.Statistics(
        result=nextmv.ResultStatistics(value=1.0)
    ),
    assets=assets  # Add your visual assets here
)

nextmv.write(output)
```

### How visuals are processed

When you run `app.run_visuals(run_id)`, the system:

1. Reads the `assets.json` file from `.nextmv/runs/<RUN_ID>/outputs/assets/`
2. Filters for assets with a `visual` schema defined
3. For each visual asset:
    * **Plotly assets**: Converts the JSON content to a Plotly figure and saves
      as HTML
    * **GeoJSON assets**: Creates an interactive Folium map and saves as HTML
4. Opens each generated HTML file in a new browser tab

All HTML files are stored in `.nextmv/runs/<RUN_ID>/visuals/` and are named
based on the asset's `label` property.

### Complete example

For a complete working example of creating visual assets, see the
[Get started with a new model][get-started-new-model] tutorial. The tutorial
walks you through creating a sample application that includes a `src/visuals.py`
file, which demonstrates creating a Plotly bar chart visualization.

[app-run-visuals]: ./reference/application.md#nextmv.nextmv.local.application.Application.run_visuals
[geojson-spec]: https://datatracker.ietf.org/doc/html/rfc7946
[get-started-new-model]: ./get-started-new-model.md
