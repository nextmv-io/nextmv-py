# Python Demand Forecast + Inventory Allocation Template

This is a template for a Nextmv application that runs a two-stage
demand-forecast and inventory-allocation pipeline using Nextpipe. It has the
following characteristics:

* Type: Python
* Content format: `multi-file`. Read/write one or more files from/to disk (a directory).

This is the basic structure:

```text
├── app.yaml
├── main.py
├── README.md
├── requirements.txt
└── visuals.py
```

* `app.yaml`: App manifest, containing the configuration to run the app with Nextmv.
* `main.py`: Entrypoint for the app. Loads input data, runs the
  demand-forecast and inventory-allocation flow, and writes the output.
* `README.md`: Description of the app.
* `requirements.txt`: Python dependencies for the app.
* `visuals.py`: Generates Plotly visual assets from the solution.

A sample input file is also provided as `inputs/input.json`. It contains historical
store sales data, stores, and warehouses.

1. Install packages.

    ```bash
    pip install -r requirements.txt
    ```

2. Run the app. Options can be omitted and will default to the values specified
   in `app.yaml`.

    ```bash
    python main.py \
        --solver highs \
        --penalty_unmet_demand 100 \
        --time_limit 30
    ```

3. Create the application as a workflow application in Nextmv Cloud.

    ```bash
    nextmv cloud app create --app-id demand-forecast-allocation --is-workflow
    ```

4. Create a secrets collection using your Nextmv API key.

    ```bash
    nextmv cloud secrets create --app-id demand-allocation-workflow \
        --secrets '{"type": "env", "location": "NEXTMV_API_KEY", "value": "<YOUR_NEXTMV_API_KEY>"}'
    ```

5. Push the application to Nextmv Cloud.

    ```bash
    nextmv cloud app push --app-id demand-forecast-allocation
    ```

6. Run the workflow application in Nextmv Cloud, using the secrets collection.

    ```bash
    nextmv cloud run create --app-id demand-forecast-allocation --input inputs \
        --secret-collection-id "<YOUR_SECRET_COLLECTION_ID>"
    ```
