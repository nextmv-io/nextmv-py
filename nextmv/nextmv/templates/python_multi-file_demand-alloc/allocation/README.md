# Python Inventory Allocation Template

This is a template for a Nextmv application that solves an inventory-allocation
problem. It has the following characteristics:

* Type: Python
* Content format: `json`, utf-8 encoded. JSON is read from stdin
  and written to stdout.

This is the basic structure:

```text
├── app.yaml
├── main.py
├── README.md
├── requirements.txt
└── visuals.py
```

* `app.yaml`: App manifest, containing the configuration to run the app with Nextmv.
* `main.py`: Entrypoint for the app. Loads input data, builds and solves the
  optimization model, and writes the output.
* `README.md`: Description of the app.
* `requirements.txt`: Python dependencies for the app.
* `visuals.py`: Generates Plotly visual assets from the solution.

1. Install packages.

    ```bash
    pip install -r requirements.txt
    ```

2. Run the app. Options can be omitted and will default to the values specified
   in `app.yaml`.

    ```bash
    cat input.json | python main.py \
        --solver highs \
        --penalty_unmet_demand 100 \
        --supply_utilization_min 0 \
        --cost_threshold 0 \
        --time_limit 30
    ```

3. Push the application with the ID `inventory-allocation` to make it available
   in Nextmv Cloud for the workflow app to use.

    ```bash
    nextmv cloud app push --app-id inventory-allocation
    ```
