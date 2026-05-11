# Nextmv App Development Workflow

## Rules

- **Solver**: Ask the user which solver or modeling library to use (e.g.,
  Pyomo, OR-Tools, HiGHS, SimPy, Gurobi, Xpress, CPLEX, AMPL, Hexaly,
  scikit-learn, Timefold, CVXPY, and others).
- **Metrics**: Every app must report metrics via `nextmv.Output(metrics={...})`.
  - **Optimization apps** (MIP, LP, CP, heuristics): use `status` (`optimal` | `suboptimal` | `infeasible` | `unbounded`) and `result_value` (objective value).
  - **ML classifier apps**: use `accuracy`, `precision`, `recall`, `f1_score`, `roc_auc`, `log_loss`, and confusion matrix counts. Do NOT use `status`/`result_value`.
  - **ML regression / forecasting apps**: use `rmse`, `mae`, `r2`, and domain-relevant metrics. Do NOT use `status`/`result_value`.
  - **Simulation / rules-engine apps**: use domain-specific metrics (throughput, utilization, queue length, etc.).
- **Visualization**: Every app must include at least one Plotly visualization rendered as a `nextmv.Asset`.
- **Configuration**: Every app must expose user-facing options via `app.yaml`. Apps that use a random seed must expose a `random_seed` option (`option_type: int`, not required, no default).

---

## File Structure

```
my-app/
├── app.yaml          # Nextmv manifest (required)
├── main.py           # Entry point
├── visuals.py        # Plotly visualization(s)
├── requirements.txt  # Pinned Python dependencies
├── input.json        # Default sample input
├── inputs/           # 3-5 inputs of varying size/scenario
│   ├── small.json
│   ├── medium.json
│   └── large.json
└── README.md         # Short description and usage
```

---

## Step 1: Create the App Manifest

Use `manifest_init` to scaffold an `app.yaml`:

```
manifest_init(manifest_type="python", content_format="json", dirpath="my-app")
```

Then edit it to add your app's actual options.

---

## Step 2: Write app.yaml

### JSON format (default)

Input is a single JSON file via stdin; output is a single JSON object via stdout.

```yaml
type: python
runtime: ghcr.io/nextmv-io/runtime/python:3.11
python:
  pip-requirements: pyproject.toml # Can be a requirements.txt

files:
  - main.py
  - visuals.py

configuration:
  options:
    strict: false
    items:
      - name: input
        option_type: string
        default: ''
        required: false
        ui:
          control_type: input
          hidden_from:
            - operator
      - name: output
        option_type: string
        default: ''
        required: false
        ui:
          control_type: input
          hidden_from:
            - operator
```

The `input` and `output` options are required so that `nextmv.load(options=options, path=options.input)` works correctly.

### Multi-file format

Input and output are directories of files. Use when the solver writes its own output files or when you need CSV/Excel/text output.

```yaml
type: python
runtime: ghcr.io/nextmv-io/runtime/python:3.11
python:
  pip-requirements: pyproject.toml # Can be a requirements.txt

files:
  - main.py
  - visuals.py

configuration:
  content:
    format: multi-file
    multi-file:
      input:
        path: .
      output:
        solutions: .
        metrics: metrics.json
        assets: assets.json
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

---

## Step 3: Write main.py

### Load manifest and options

```python
import nextmv

manifest = nextmv.Manifest.from_yaml(".")
options = manifest.extract_options()
```

### JSON format — load and write

```python
input = nextmv.load(options=options, path=options.input)
data = input.data

nextmv.redirect_stdout()  # redirect solver logs away from stdout

output = nextmv.Output(
    solution={"assignments": [...]},
    assets=[chart],
    metrics={
        "result_value": objective_value,
        "status": "optimal",
    },
)
nextmv.write(output, path=options.output)
```

### Multi-file format — load and write

Read input files directly; write output files to disk. Do NOT call `nextmv.load`.

```python
import csv, json, os

with open("orders.csv", newline="") as f:
    rows = list(csv.DictReader(f))

# ... solver ...

os.makedirs("output", exist_ok=True)
with open("output/results.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[...])
    writer.writeheader()
    writer.writerows(results)

with open("metrics.json", "w") as f:
    json.dump({"result_value": obj, "status": "optimal"}, f)

# assets.json — top level MUST be {"assets": [...]}
# Inside each asset: visual.schema and visual.type (NOT visual_schema/visual_type)
# content stays as a list (do not unwrap with [0])
# Do NOT use asset.model_dump() — it breaks the schema field
with open("assets.json", "w") as f:
    json.dump({"assets": [
        {
            "name": a.name,
            "content_type": a.content_type,
            "visual": {
                "schema": a.visual.visual_schema.value,
                "type": a.visual.visual_type,
                "label": a.visual.label,
            },
            "content": a.content,
        }
        for a in charts
    ]}, f)
```

### Logging

Use `nextmv.log(...)` (writes to stderr) for progress messages.

---

## Step 4: Write visuals.py

```python
import json
import nextmv
import plotly.graph_objects as go


def build_chart(solution, input_data, label="Solution", tab_order=1):
    fig = go.Figure()
    fig.add_trace(go.Scatter(...))
    fig.update_layout(title=label)

    return nextmv.Asset(
        name=label,
        content_type="json",
        visual=nextmv.Visual(
            visual_schema=nextmv.VisualSchema(value="plotly"),
            visual_type="custom-tab",
            label=label,
            tab_order=tab_order,
        ),
        content=[json.loads(fig.to_json())],
    )
```

Use `tab_order=1` for the first chart, incrementing for each additional.

---

## Step 5: Write requirements.txt

Pin all dependencies. Always include `nextmv` and `plotly`.

---

## Step 6: Create Input Files

Include `input.json` (default) plus an `inputs/` directory with 3-5 files varying problem size, constraint tightness, or scenario type.

---

## Step 7: Local Testing

### Run locally

**JSON format:**

```
local_run(app_dir=".", input=<parsed input.json>)
local_run(app_dir=".", input=<parsed inputs/large.json>, run_options={"solve.duration": "30s"})
```

**Multi-file format:**

```
local_run(app_dir=".", input_dir_path="input", content_format="multi-file")
```

### Inspect runs

```
local_list_runs(app_dir=".")
local_run_logs(app_dir=".", run_id="<run-id>")
local_run_result(app_dir=".", run_id="<run-id>")
```

### Sync to Cloud

```
local_sync(app_dir=".", cloud_app_id="<app-id>")
```

---

## Step 8: Write README.md

Include these sections: App Name (one-sentence description), Approach, Configuration Options (table), Input Format, Output (solution, metrics, visualizations), Running Locally (tool calls), Syncing to Cloud.

---

## Step 9: Deploy to Nextmv Cloud

### 1. Create the Cloud app (first time)

```
cloud_create_app(name="My App", app_id="my-app", description="...")
```

### 2. Push and create a version

```
cloud_push_app(app_id="<app-id>", app_dir=".")
cloud_create_version(app_id="<app-id>", name="v1.0")
```

### 3. Create runs from all inputs

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

- [ ] `app.yaml` has user-facing configuration options
- [ ] `main.py` loads manifest and options via `nextmv.Manifest.from_yaml`
- [ ] Metrics reported via `nextmv.Output(metrics={...})`
- [ ] At least one Plotly visualization as `nextmv.Asset`
- [ ] Dependencies are Apache 2.0 / MIT / BSD licensed
- [ ] `input.json` and `inputs/` directory with 3-5 varied inputs
- [ ] `requirements.txt` with pinned versions
- [ ] Local runs succeed with expected metrics
- [ ] At least one non-default option tested
- [ ] Synced to Cloud, pushed version, created instances
- [ ] Acceptance test comparing staging vs production reviewed
- [ ] **User confirmed** before promoting to production
