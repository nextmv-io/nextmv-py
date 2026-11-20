# FICO Platform DecisionOps App Development Workflow

## Rules

- **Existing models — manifest first**: When the user asks to connect their own
  existing model to Nextmv / FICO Platform DecisionOps, **minimize code
  changes**. Adapt `app.yaml` to the model before touching the model code, and
  only change code when the manifest cannot cover the gap. **Translate only what
  the model already produces** — existing plots become assets, existing summary
  statistics become metrics, existing parameters become options. Do not invent
  real ones; for anything missing, expose a clearly labeled **placeholder**
  (placeholder slider, placeholder metric, placeholder asset) that does not
  change how the model runs. See
  [Connecting an Existing Model](#connecting-an-existing-model). The rest of this
  guide (Steps 1-9) describes building a **new** app; the "every app must"
  rules for metrics, visualization, and configuration below apply to new apps
  only.
- **Language**: Python and Java apps are supported. For a new app, ask the user
  which language to use. For an existing model, use the model's language.
- **Solver**: Ask the user which solver or modeling library to use (e.g.,
  Pyomo, OR-Tools, HiGHS, SimPy, Gurobi, Xpress, CPLEX, AMPL, Hexaly,
  scikit-learn, Timefold, CVXPY, and others).
- **Content format**: Ask the user whether the app should use the
  **multi-file** format or the **JSON** format. Do not pick one for them.
  - **multi-file**: input is a directory of CSV files; output is files written
    to disk (solutions, `metrics.json`, `assets.json`), wired up in `app.yaml`.
  - **JSON**: input is a single JSON document read from stdin; output is a
    single JSON document written to stdout.
- **Keep the model platform-agnostic**: The model code should be plain code that
  reads files / stdin and writes files / stdout. Everything platform-specific
  (content format, input/output locations, metrics/assets files, options,
  build command) belongs in `app.yaml`.
  - **Python**: the **only** use of the `nextmv` SDK in model code is loading
    options from the manifest
    (`nextmv.Manifest.from_yaml(...).extract_options()`). Visualization code
    (`visuals.py`) may also use the SDK to build assets (`nextmv.Asset`). JSON
    apps may use `nextmv.redirect_stdout()` / `nextmv.reset_stdout()` and
    `nextmv.log` to keep logs off stdout.
  - **Java**: there is no SDK dependency. Options arrive as command-line
    arguments (see [Options at runtime](#options-at-runtime)); everything else
    is plain Java (e.g. Gson / Jackson for JSON).
- **Do NOT** use `nextmv.load`, `nextmv.write`, `nextmv.Output`, or any other
  SDK input/output helpers.
- **Do NOT** add `input` / `output` options to `app.yaml`.
- **Metrics**: Every new app must write metrics. For multi-file apps, write them to
  `metrics.json` at the path declared in `app.yaml` as flat key-value pairs
  (no `metrics` wrapper); for JSON apps, put them under the `metrics` key of
  the stdout output.
  - **Optimization apps** (MIP, LP, CP, heuristics): use `status` (`optimal` | `suboptimal` | `infeasible` | `unbounded`) and `result_value` (objective value).
  - **ML classifier apps**: use `accuracy`, `precision`, `recall`, `f1_score`, `roc_auc`, `log_loss`, and confusion matrix counts. Do NOT use `status`/`result_value`.
  - **ML regression / forecasting apps**: use `rmse`, `mae`, `r2`, and domain-relevant metrics. Do NOT use `status`/`result_value`.
  - **Simulation / rules-engine apps**: use domain-specific metrics (throughput, utilization, queue length, etc.).
- **Visualization**: Every new app must include at least one visualization written
  as an asset (`nextmv.Asset` in Python; the equivalent JSON structure in Java —
  see Step 4). Use Plotly for charts.
- **Maps**: For anything geographic (locations, routes, regions), use a
  **GeoJSON** asset (`schema: geojson`), NOT a Plotly map. Plotly map traces
  (`scattergeo`, `scattermap`, `scattermapbox`, `choropleth`, `choroplethmap`,
  `choroplethmapbox`, `densitymap`, `densitymapbox`) fetch basemaps / topojson
  from external servers, which the Console's Content Security Policy blocks
  ("Failed to fetch ... violates the document's Content Security Policy").
- **Configuration**: Every new app must expose user-facing options via `app.yaml`. Apps that use a random seed must expose a `random_seed` option (`option_type: int`, not required, no default).

---

## Connecting an Existing Model

When the user already has a model and wants to run it on Nextmv / FICO Platform
DecisionOps, the goal is to **fit the manifest to the code, not the code to the
manifest**. Work through these steps in order and stop as soon as the model
runs.

1. **Read the model first.** Find out how it gets input (stdin, a directory, file
   names), where it writes output (files, stdout), how it takes parameters
   (CLI flags, config file, constants), what it prints and where, and — for
   Java — how it is built (Maven / Gradle) and what jar the build produces.
2. **Pick the content format that matches what the model already does**, then
   confirm with the user:
   - Reads/writes files on disk → `multi-file`.
   - Reads JSON from stdin and writes JSON to stdout → `json`.
3. **Adapt `app.yaml` to the existing layout — no code changes:**
   - `type` / `runtime`: `python` + `ghcr.io/nextmv-io/runtime/python:3.11`, or
     `java` + `ghcr.io/nextmv-io/runtime/java:latest`.
   - `files`: list the model's existing files/directories (globs are supported).
     For Java, list the built jar (e.g. `main.jar` or
     `target/my-model-1.0-jar-with-dependencies.jar`).
   - `execution.entrypoint`: point at the existing entry point instead of
     renaming it — e.g. `./src/solve.py` (Python) or the jar the build already
     produces (Java, run with `java -jar`). Defaults are `./main.py` and
     `./main.jar`.
   - `execution.cwd`: set the working directory if the model uses paths
     relative to a sub-directory.
   - Python: `python.pip-requirements` — point at the existing
     `requirements.txt` / `pyproject.toml`.
   - Java: `pre-push` — use the project's existing build command (e.g.
     `mvn package`, `./gradlew shadowJar`). It runs before `cloud_push_app`.
   - `configuration.content.multi-file.input.path`: set to the directory the
     model already reads from.
   - `configuration.content.multi-file.output.solutions` / `metrics` / `assets`:
     set to the paths the model already writes to.
   - `configuration.options.items`: declare **only** the parameters the model
     already takes (CLI flags, config values it reads), using the **same
     names** (see [Options at runtime](#options-at-runtime)). A model that
     already parses those flags needs no code change. Do not turn hard-coded
     constants into options.
4. **Make only the code changes needed to run** for what the manifest cannot
   cover, e.g.:
   - Java: making the argument parser accept both `-name value` and
     `-name=value` if it only handles one form.
   - JSON apps: keeping logs off stdout — `nextmv.redirect_stdout()` /
     `nextmv.reset_stdout()` (Python) or `System.err` / `System.setOut(System.err)`
     (Java).
   - Java: if the build does not produce a runnable fat jar, add the
     `maven-assembly-plugin` (`jar-with-dependencies`, with `mainClass` set) or
     Gradle Shadow plugin — a build-config change, not a model change.
   Keep the solver logic and data handling untouched. Do not restructure the
   project, rename files, or convert I/O formats unless the user asks.
5. **Translate what the model already produces — nothing more:**
   - **Summary statistics → metrics.** If the model already computes or prints
     summary values (objective, status, KPIs, counts), write those same values
     to `metrics.json` (multi-file, flat key-value pairs) or the `metrics` key
     (JSON). If it emits a deprecated `statistics` block, add `metrics`
     alongside it rather than restructuring. Do not compute new statistics.
   - **Plots → assets.** If the model already makes plots (matplotlib, Plotly,
     etc.), recreate those same plots from the same data as Plotly assets
     (GeoJSON for maps). Leave the model's existing plot output in place. Do not
     design new charts.
   - **If the model has none of these, do not invent real ones.** Expose a
     placeholder instead (see below).
6. **Expose placeholders** for any options, metrics, or visuals the model does
   not have, so the user sees them in the Console and knows where to add their
   own. Every placeholder must be **visibly labeled as a placeholder** and must
   **not change how the model runs** (no changes to solver logic, inputs, or
   real outputs). See [Placeholders](#placeholders-for-existing-models).
7. **Tell the user** what went into `app.yaml`, what (if any) required code or
   build edits and why, what was translated from existing output, and which
   placeholders were added and how to replace them.

### Placeholders for existing models

Add only the placeholders for what is missing — e.g. if the model already has
real metrics, add a placeholder asset but no placeholder metric. Use the names
below so placeholders are obvious in the Console.

| Placeholder | Name / label | What the user sees |
| --- | --- | --- |
| Option | `placeholder_slider`, display name "Placeholder slider" | A slider in the run options |
| Metric | `placeholder_metric` | A metric on the run |
| Asset | label "Placeholder asset" | A custom tab with a labeled placeholder chart |

**Placeholder option (`app.yaml`)** — declare it, but the model does not read
it:

```yaml
  options:
    items:
      - name: placeholder_slider
        option_type: int
        default: 5
        required: false
        description: Placeholder - not used by the model. Replace with a real parameter.
        additional_attributes:
          min: 0
          max: 10
          step: 1
        ui:
          control_type: slider
          display_name: Placeholder slider
```

Sliders require `min`, `max`, and `step`. If a user changes the placeholder on
a run, it is passed to the model as `-placeholder_slider <value>`. Check how the
model parses arguments: if it rejects unknown flags (e.g. Python `argparse`
`parse_args()`, or a Java parser that exits on unknown arguments), tell the user
that changing the placeholder will fail the run until they wire it up.

**Placeholder metric and asset — multi-file (no code changes).** Ship static
placeholder files with the app and point the manifest's output paths at them:

```
placeholders/
├── metrics.json
└── assets.json
```

`placeholders/metrics.json`:

```json
{"placeholder_metric": 0}
```

`placeholders/assets.json`:

```json
{
  "assets": [
    {
      "name": "Placeholder asset",
      "content_type": "json",
      "visual": {"schema": "plotly", "type": "custom-tab", "label": "Placeholder asset"},
      "content": [
        {
          "data": [{"type": "bar", "x": ["placeholder"], "y": [1]}],
          "layout": {
            "title": {"text": "Placeholder asset - replace with your model's visuals"}
          }
        }
      ]
    }
  ]
}
```

`app.yaml`:

```yaml
files:
  - src/              # the model's existing files
  - placeholders/     # placeholder metrics / assets
configuration:
  content:
    format: multi-file
    multi-file:
      input:
        path: data/in
      output:
        solutions: data/out
        metrics: placeholders/metrics.json  # Placeholder - point at the model's metrics file once it writes one.
        assets: placeholders/assets.json    # Placeholder - point at the model's assets file once it writes one.
```

If the model already writes real metrics (or assets), point that path at the
model's file and only use the placeholder file for the missing one.

**Placeholder metric and asset — JSON format.** JSON apps report metrics and
assets on stdout, so add them to the output document where it is built — an
additive change that does not touch the solve:

```python
output["metrics"] = {"placeholder_metric": 0}  # Placeholder - replace with real KPIs.
output["assets"] = [placeholder_asset]          # Placeholder - same structure as placeholders/assets.json.
```

```java
output.put("metrics", Map.of("placeholder_metric", 0)); // Placeholder - replace with real KPIs.
output.put("assets", List.of(placeholderAsset));          // Placeholder - same structure as above.
```

---

## File Structure

### Python

```
my-app/
├── app.yaml          # App manifest (required)
├── main.py           # Entry point
├── visuals.py        # Plotly visualization(s)
├── requirements.txt  # Pinned Python dependencies
├── <inputs>          # See "Input layout" below
└── README.md         # Short description and usage
```

### Java

```
my-app/
├── app.yaml          # App manifest (required)
├── pom.xml           # Maven build; produces ./main.jar
├── src/main/java/com/example/
│   ├── Main.java     # Entry point
│   └── Visuals.java  # Plotly visualization(s)
├── <inputs>          # See "Input layout" below
└── README.md         # Short description and usage
```

### Input layout

- **Multi-file format**:

  ```
  inputs/             # Default sample input (CSV files)
  ├── orders.csv
  └── vehicles.csv
  scenarios/          # 3-5 input directories of varying size/scenario
  ├── small/
  ├── medium/
  └── large/
  ```

- **JSON format**:

  ```
  input.json          # Default sample input
  inputs/             # 3-5 inputs of varying size/scenario
  ├── small.json
  ├── medium.json
  └── large.json
  ```

---

## Step 1: Create the App Manifest

Use `manifest_init` to scaffold an `app.yaml`, passing the language
(`"python"` or `"java"`) and the content format the user chose
(`"multi-file"` or `"json"`):

```
manifest_init(manifest_type="python", content_format="multi-file", dirpath="my-app")
manifest_init(manifest_type="java", content_format="json", dirpath="my-app")
```

Then edit it to add your app's actual options.

---

## Step 2: Write app.yaml

`app.yaml` is where everything platform-specific lives: the language/runtime,
the build, the content format, where input is read from, where solutions /
metrics / assets are written to, and the options the app exposes.

### Language header

**Python:**

```yaml
type: python
runtime: ghcr.io/nextmv-io/runtime/python:3.11
python:
  pip-requirements: pyproject.toml # Can be a requirements.txt

files:
  - main.py
  - visuals.py
```

**Java:**

```yaml
type: java
runtime: ghcr.io/nextmv-io/runtime/java:latest

# Build the jar before pushing. Runs on cloud_push_app only, not on local runs.
pre-push: mvn package

files:
  - main.jar
```

### Multi-file format

Input is a directory of CSV files; output is files written to disk. The
`output` block wires up the files the model writes so that FICO Platform
DecisionOps picks them up.

```yaml
configuration:
  content:
    format: multi-file
    multi-file:
      input:
        path: inputs                    # Directory the model reads CSVs from
      output:
        solutions: outputs/solutions    # Directory the model writes solution files to
        metrics: outputs/metrics.json   # File the model writes metrics to
        assets: outputs/assets.json     # File the model writes visual assets to
  options:
    strict: true
    validation:
      enforce: all
    items:
      - name: my_option
        option_type: int
        default: 10
        required: true
        ui:
          control_type: slider
          display_name: My Option
```

The paths in the model code must match the paths declared here.

### JSON format

Input is a single JSON document via stdin; output is a single JSON document via
stdout. Do NOT add `input` / `output` options.

```yaml
configuration:
  content:
    format: json
  options:
    strict: false
    items:
      - name: my_option
        option_type: int
        default: 10
        required: false
        ui:
          control_type: slider
          display_name: My Option
```

### Random seed option

```yaml
- name: random_seed
  option_type: int
  required: false
  ui:
    control_type: input
    display_name: Random Seed (optional, for reproducibility)
```

### Option types

| `option_type` | Valid `control_type` values | Notes |
| --- | --- | --- |
| `string` | `input`, `select`, `multiselect` | Use `additional_attributes.values` for select |
| `int` | `input`, `slider` | Use `additional_attributes` for min/max/step |
| `float` | `input`, `slider` | Same as int |
| `bool` | `toggle` | No additional attributes needed |

### Options at runtime

Option values set on a run are passed to the entrypoint as command-line
arguments named after the option. Depending on where the app runs they arrive
as `-my_option 20` or `-my_option=20`, so parsers must accept **both** forms
(and `--my_option` for good measure).

- **Python**: `nextmv.Manifest.from_yaml(".").extract_options()` handles this
  and applies the manifest defaults.
- **Java**: parse `args` yourself (see Step 3). Only options set on the run are
  passed — manifest defaults are **not** — so the code's fallback defaults must
  match the `default` values in `app.yaml`.

---

## Step 3: Write the Entry Point

### Python — load options from the manifest

This is the only SDK call the model code makes.

```python
import nextmv

manifest = nextmv.Manifest.from_yaml(".")
options = manifest.extract_options()
```

Pass plain values (e.g. `options.my_option`) into the solver code so the model
itself does not depend on the SDK.

### Python — multi-file format

Read CSVs from the input directory and write output files to the paths declared
in `app.yaml`. Use plain `print(...)` for logs — stdout is captured as run logs
for multi-file apps, so `nextmv.log` is not needed.

```python
import csv
import json
import os

import nextmv

from visuals import build_chart

# Must match configuration.content.multi-file in app.yaml.
INPUT_DIR = "inputs"
SOLUTIONS_DIR = os.path.join("outputs", "solutions")
METRICS_FILE = os.path.join("outputs", "metrics.json")
ASSETS_FILE = os.path.join("outputs", "assets.json")


def main():
    options = nextmv.Manifest.from_yaml(".").extract_options()

    with open(os.path.join(INPUT_DIR, "orders.csv"), newline="") as f:
        orders = list(csv.DictReader(f))

    print(f"Loaded {len(orders)} orders")

    results, objective, status = solve(orders, my_option=options.my_option)

    # Solution files.
    os.makedirs(SOLUTIONS_DIR, exist_ok=True)
    with open(os.path.join(SOLUTIONS_DIR, "results.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[...])
        writer.writeheader()
        writer.writerows(results)

    # Metrics — flat key-value pairs, no wrapper.
    with open(METRICS_FILE, "w") as f:
        json.dump({"result_value": objective, "status": status}, f, indent=2)

    # Assets — top level MUST be {"assets": [...]}.
    # Use asset.to_dict() (NOT asset.model_dump(), which breaks the schema/type fields).
    charts = [build_chart(results, orders)]
    with open(ASSETS_FILE, "w") as f:
        json.dump({"assets": [a.to_dict() for a in charts]}, f)


if __name__ == "__main__":
    main()
```

### Python — JSON format

Read the input from stdin and write a single JSON document to stdout with
`solution`, `metrics`, and `assets` keys. stdout is reserved for the output, so
all logs must go to stderr: call `nextmv.redirect_stdout()` up front so any
`print` / solver chatter goes to stderr, use `nextmv.log(...)` for progress
messages, and call `nextmv.reset_stdout()` right before writing the output.

```python
import json
import sys

import nextmv

from visuals import build_chart


def main():
    nextmv.redirect_stdout()  # send prints / solver logs to stderr
    options = nextmv.Manifest.from_yaml(".").extract_options()

    data = json.load(sys.stdin)
    nextmv.log(f"Loaded {len(data['orders'])} orders")

    solution, objective, status = solve(data, my_option=options.my_option)
    charts = [build_chart(solution, data)]

    output = {
        "solution": solution,
        "metrics": {"result_value": objective, "status": status},
        "assets": [a.to_dict() for a in charts],
    }
    nextmv.reset_stdout()  # restore stdout for the output document
    json.dump(output, sys.stdout)


if __name__ == "__main__":
    main()
```

### Java — parse options

There is no SDK in Java; read options from `args`. Keep fallback defaults in
sync with `app.yaml`.

```java
// Accepts -name value, -name=value, --name value, --name=value.
static Map<String, String> parseOptions(String[] args) {
  Map<String, String> opts = new HashMap<>();
  for (int i = 0; i < args.length; i++) {
    if (!args[i].startsWith("-")) continue;
    String key = args[i].replaceFirst("^-{1,2}", "");
    int eq = key.indexOf('=');
    if (eq >= 0) {
      opts.put(key.substring(0, eq), key.substring(eq + 1));
    } else if (i + 1 < args.length) {
      opts.put(key, args[++i]);
    }
  }
  return opts;
}

// In main():
Map<String, String> opts = parseOptions(args);
int myOption = Integer.parseInt(opts.getOrDefault("my_option", "10")); // default must match app.yaml
```

### Java — multi-file format

Read CSVs from the input directory and write output files to the paths declared
in `app.yaml`. Plain `System.out.println` is fine for logs — stdout is captured
as run logs for multi-file apps. For CSV parsing with quoted fields, use a
permissively licensed library such as Apache Commons CSV or OpenCSV.

```java
package com.example;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class Main {
  // Must match configuration.content.multi-file in app.yaml.
  static final Path INPUT_DIR = Paths.get("inputs");
  static final Path SOLUTIONS_DIR = Paths.get("outputs", "solutions");
  static final Path METRICS_FILE = Paths.get("outputs", "metrics.json");
  static final Path ASSETS_FILE = Paths.get("outputs", "assets.json");

  public static void main(String[] args) throws IOException {
    Map<String, String> opts = parseOptions(args);
    int myOption = Integer.parseInt(opts.getOrDefault("my_option", "10"));

    List<Map<String, String>> orders = readCsv(INPUT_DIR.resolve("orders.csv"));
    System.out.println("Loaded " + orders.size() + " orders");

    Result result = solve(orders, myOption);

    // Solution files.
    Files.createDirectories(SOLUTIONS_DIR);
    writeCsv(SOLUTIONS_DIR.resolve("results.csv"), result.rows());

    Gson gson = new GsonBuilder().setPrettyPrinting().create();

    // Metrics — flat key-value pairs, no wrapper.
    Map<String, Object> metrics = new LinkedHashMap<>();
    metrics.put("result_value", result.objective());
    metrics.put("status", result.status());
    Files.writeString(METRICS_FILE, gson.toJson(metrics));

    // Assets — top level MUST be {"assets": [...]}.
    Files.writeString(ASSETS_FILE, gson.toJson(Map.of("assets", List.of(Visuals.buildChart(result, "Solution")))));
  }
}
```

### Java — JSON format

Read the input from stdin and write a single JSON document to stdout with
`solution`, `metrics`, and `assets` keys. stdout is reserved for the output, so
all logs go to `System.err`. If the solver library prints to stdout, swap
`System.out` for `System.err` during the solve and restore it before writing
the output (the Java equivalent of `nextmv.redirect_stdout()`).

```java
public static void main(String[] args) {
  PrintStream stdout = System.out;
  System.setOut(System.err); // send prints / solver logs to stderr

  Map<String, String> opts = parseOptions(args);
  int myOption = Integer.parseInt(opts.getOrDefault("my_option", "10"));

  Gson gson = new Gson();
  Input input = gson.fromJson(new InputStreamReader(System.in, StandardCharsets.UTF_8), Input.class);
  System.err.println("Loaded " + input.orders.size() + " orders");

  Result result = solve(input, myOption);

  Map<String, Object> output = new LinkedHashMap<>();
  output.put("solution", result.solution());
  output.put("metrics", Map.of("result_value", result.objective(), "status", result.status()));
  output.put("assets", List.of(Visuals.buildChart(result, "Solution")));

  System.setOut(stdout); // restore stdout for the output document
  System.out.println(gson.toJson(output));
}
```

---

## Step 4: Write the Visualization

### Python — visuals.py

Visualization code may use the SDK to build assets.

```python
import json

import nextmv
import plotly.graph_objects as go


def build_chart(solution, input_data, label="Solution"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(...))
    fig.update_layout(title=label)

    return nextmv.Asset(
        name=label,
        content_type="json",
        visual=nextmv.Visual(
            visual_schema=nextmv.VisualSchema.PLOTLY,
            visual_type="custom-tab",
            label=label,
        ),
        content=[json.loads(fig.to_json())],
    )
```

### Java — Visuals.java

Build the Plotly figure (`data` + `layout`) as plain maps and wrap it in the
asset structure. The keys must be exactly `name`, `content_type`,
`visual.schema`, `visual.type`, `visual.label`, and `content` (a list).

```java
static Map<String, Object> buildChart(Result result, String label) {
  Map<String, Object> trace = new LinkedHashMap<>();
  trace.put("type", "bar");
  trace.put("x", result.labels());
  trace.put("y", result.values());

  Map<String, Object> figure = new LinkedHashMap<>();
  figure.put("data", List.of(trace));
  figure.put("layout", Map.of("title", Map.of("text", label)));

  Map<String, Object> visual = new LinkedHashMap<>();
  visual.put("schema", "plotly");
  visual.put("type", "custom-tab");
  visual.put("label", label);

  Map<String, Object> asset = new LinkedHashMap<>();
  asset.put("name", label);
  asset.put("content_type", "json");
  asset.put("visual", visual);
  asset.put("content", List.of(figure));
  return asset;
}
```

### Maps — GeoJSON asset

Do NOT use Plotly map traces (`scattergeo`, `scattermap`, `scattermapbox`,
`choropleth*`, `densitymap*`) — they load basemaps from external servers and are
blocked by the Console's Content Security Policy. Render maps as a GeoJSON
`FeatureCollection` instead; the Console draws it on its own basemap.

- Coordinates are **`[longitude, latitude]`** (GeoJSON order — not lat/lon).
- Geometries: `Point` (locations), `LineString` (routes), `Polygon` (regions).
- `properties.style` sets the look (`color`, `fillColor`, `fillOpacity`,
  `weight`, `opacity`).
- `properties.metadata` is a list of `{"key", "value"}` pairs shown when the
  feature is clicked.
- `content` is the FeatureCollection itself (a dict, not wrapped in a list).

**Python:**

```python
import nextmv


def build_map(routes, label="Routes"):
    features = [
        {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [[stop["lon"], stop["lat"]] for stop in route["stops"]],
            },
            "properties": {
                "name": route["id"],
                "style": {"color": route["color"], "weight": 3, "opacity": 0.9},
                "metadata": [
                    {"key": "Vehicle", "value": route["id"]},
                    {"key": "Stops", "value": len(route["stops"])},
                ],
            },
        }
        for route in routes
    ]

    return nextmv.Asset(
        name=label,
        content_type="json",
        visual=nextmv.Visual(
            visual_schema=nextmv.VisualSchema.GEOJSON,
            visual_type="custom-tab",
            label=label,
        ),
        content={"type": "FeatureCollection", "features": features},
    )
```

**Java:** build the same structure with maps — `visual.schema` is `"geojson"`
and `content` is the `FeatureCollection` map:

```java
Map<String, Object> asset = new LinkedHashMap<>();
asset.put("name", label);
asset.put("content_type", "json");
asset.put("visual", Map.of("schema", "geojson", "type", "custom-tab", "label", label));
asset.put("content", Map.of("type", "FeatureCollection", "features", features));
```

---

## Step 5: Declare Dependencies

- **Python** — `requirements.txt`: pin all dependencies. Always include
  `nextmv` and `plotly`.
- **Java** — `pom.xml`: pin all dependency versions (solver, Gson/Jackson, CSV
  library). Use the `maven-assembly-plugin` with `jar-with-dependencies`,
  `mainClass` set to your entry class, `outputDirectory` `.`, `finalName`
  `main`, and `appendAssemblyId` `false` so `mvn package` produces `./main.jar`
  (see the [java-ortools-knapsack](https://github.com/nextmv-io/community-apps/tree/develop/java-ortools-knapsack)
  community app for a working `pom.xml`).

---

## Step 6: Create Input Files

- **Multi-file format**: inputs are **CSV files**. Put the default sample input
  in `inputs/` (the directory declared in `app.yaml`) and add a `scenarios/`
  directory with 3-5 sub-directories of CSVs varying problem size, constraint
  tightness, or scenario type.
- **JSON format**: inputs are **JSON files**. Include `input.json` (default) plus
  an `inputs/` directory with 3-5 JSON files varying problem size, constraint
  tightness, or scenario type.

---

## Step 7: Local Testing

### Build (Java only)

`pre-push` only runs on `cloud_push_app`, so build the jar before every local
run (e.g. `mvn package`). Local runs execute `java -jar <entrypoint>` and
require a local JDK.

### Run locally

**Multi-file format:**

```
local_run(app_dir=".", input_dir_path="inputs", content_format="multi-file")
local_run(app_dir=".", input_dir_path="scenarios/large", content_format="multi-file", run_options={"my_option": "20"})
```

**JSON format:**

```
local_run(app_dir=".", input=<parsed input.json>)
local_run(app_dir=".", input=<parsed inputs/large.json>, run_options={"my_option": "20"})
```

### Inspect runs

```
local_list_runs(app_dir=".")
local_run_logs(app_dir=".", run_id="<run-id>")
local_run_result(app_dir=".", run_id="<run-id>")
```

Confirm that metrics and assets show up in the run result. For multi-file apps,
if they are missing, check that the paths in the model code match the
`multi-file.output` paths in `app.yaml`. If a run with `run_options` fails with
an argument error, check that the parser accepts `-name value`.

### Sync to FICO Platform DecisionOps

```
local_sync(app_dir=".", cloud_app_id="<app-id>")
```

---

## Step 8: Write README.md

Include these sections: App Name (one-sentence description), Approach, Configuration Options (table), Input Format, Output (solution, metrics, visualizations), Building (Java), Running Locally (tool calls), Syncing to FICO Platform DecisionOps.

---

## Step 9: Deploy to FICO Platform DecisionOps

### 1. Create the app (first time)

```
cloud_create_app(name="My App", app_id="my-app", description="...")
```

### 2. Push and create a version

`cloud_push_app` runs the manifest's `pre-push` command (e.g. `mvn package`)
before uploading.

```
cloud_push_app(app_id="<app-id>", app_dir=".")
cloud_create_version(app_id="<app-id>", name="v1.0")
```

### 3. Create runs from all inputs

**Multi-file format:**

```
cloud_run(app_id="<app-id>", instance_id="latest", input_dir_path="scenarios/small", content_format="multi-file")
```

**JSON format:**

```
cloud_run(app_id="<app-id>", instance_id="latest", input=<parsed input>)
```

### 4. Create production and staging instances

```
cloud_create_instance(app_id="<app-id>", version_id="<ver>", instance_id="production", name="Production")
cloud_create_instance(app_id="<app-id>", version_id="<ver>", instance_id="staging", name="Staging")
```

### 5. Create an input set

```
cloud_create_input_set(app_id="<app-id>", name="Test inputs", instance_id="latest", maximum_runs=10)
```

### 6. Run a scenario test

```
cloud_create_scenario_test(app_id="<app-id>", name="Smoke test", scenarios=[{"instance_id": "staging", "scenario_input": {"input_set_id": "<input-set-id>"}}])
```

### 7. Run an acceptance test

```
cloud_create_acceptance_test(app_id="<app-id>", candidate_instance_id="staging", baseline_instance_id="production", input_set_id="<input-set-id>", metrics=[{"field": "result_value", "metric_type": "direct-comparison", "statistic": "mean", "params": {"operator": "le"}}])
```

### 8. Promote (only with user confirmation)

**Always ask the user before promoting staging to production.**

```
cloud_update_instance(app_id="<app-id>", instance_id="production", version_id="<new-ver>")
```

---

## Checklist

- [ ] User chose the language (Python or Java) and content format (multi-file or JSON)
- [ ] Existing model: changes made in `app.yaml` first; code changes kept to a minimum
- [ ] Existing model: only existing plots / summary stats / parameters translated to assets / metrics / options
- [ ] Existing model: anything missing exposed as a labeled placeholder (`placeholder_slider`, `placeholder_metric`, "Placeholder asset") that does not change how the model runs; user told about any argument-parsing risk
- [ ] `app.yaml` has user-facing configuration options and no `input` / `output` options
- [ ] Multi-file: `app.yaml` wires up input dir, solutions dir, `metrics.json`, and `assets.json`
- [ ] Python: model code uses the SDK only to load options via `nextmv.Manifest.from_yaml(...).extract_options()` (plus `redirect_stdout` / `reset_stdout` / `log` for JSON)
- [ ] Java: options parsed from `args` (both `-name value` and `-name=value`), defaults match `app.yaml`; `pre-push` builds the jar listed in `files`
- [ ] No `nextmv.load`, `nextmv.write`, or `nextmv.Output`
- [ ] Metrics written to `metrics.json` as flat key-value pairs (multi-file) or under the `metrics` key of stdout output (JSON)
- [ ] At least one visualization asset (`nextmv.Asset` + `to_dict()` in Python; equivalent JSON in Java)
- [ ] Maps use a GeoJSON asset (`[lon, lat]`), never Plotly map traces
- [ ] Logging: stdout is fine for multi-file; stderr only for JSON
- [ ] Dependencies are Apache 2.0 / MIT / BSD licensed
- [ ] Sample inputs: CSVs in `inputs/` + `scenarios/` (multi-file) or `input.json` + `inputs/` (JSON), 3-5 varied
- [ ] Dependencies pinned (`requirements.txt` / `pom.xml`)
- [ ] Local runs succeed with expected metrics and assets (Java: jar rebuilt first)
- [ ] At least one non-default option tested
- [ ] Synced to FICO Platform DecisionOps, pushed version, created instances
- [ ] Acceptance test comparing staging vs production reviewed
- [ ] **User confirmed** before promoting to production
