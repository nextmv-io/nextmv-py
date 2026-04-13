"""
Demand Forecast + Inventory Allocation Flow

A two-stage decision pipeline using Nextpipe's FlowSpec:
  1. forecast_demand   — trains a scikit-learn GradientBoostingRegressor on
                         historical store sales and predicts next-period demand.
  2. run_allocation    — calls the inventory-allocation cloud app with the
                         forecasted demand as a sub-app via the @app decorator.
  3. bundle_results    — combines both outputs into a unified response with
                         Plotly visualizations.
"""

from typing import Any

import numpy as np
import pandas as pd
from nextpipe import FlowSpec, app, needs, step
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import OrdinalEncoder
from visuals import allocation_sankey, forecast_chart

import nextmv


def main() -> None:
    """
    Entry point for the demand-forecast allocation flow.

    Loads the manifest and options, reads the input data, injects the random
    seed option into the payload, runs the ``DemandAllocationFlow``, and writes
    the final ``nextmv.Output`` to the configured output path.
    """
    manifest = nextmv.Manifest.from_yaml(".")
    options = manifest.extract_options()

    loaded_input = nextmv.load(
        input_format=nextmv.ContentFormat.MULTI_FILE,
        options=options,
        path="inputs",
        data_files=[nextmv.json_data_file(name="input", input_data_key="input")],
    )
    data = loaded_input.data["input"]

    # Inject options so forecast_demand can read the random seed.
    data["options"] = {}
    if options.random_seed:
        data["options"]["random_seed"] = options.random_seed

    flow = DemandAllocationFlow("DemandAllocationFlow", data)
    flow.run()
    result = flow.get_result(flow.bundle_results)

    nextmv.write(result, path="outputs")


class DemandAllocationFlow(FlowSpec):
    @step
    def forecast_demand(flow_input: dict[str, Any]) -> dict[str, Any]:
        """
        Train a GradientBoostingRegressor and predict next-period demand.

        Fits the model on historical store sales data, then predicts demand for
        the next period at each store. The returned dict doubles as the input
        payload for the inventory-allocation sub-app (explicit demand/supply
        mode).
        """

        historical = flow_input["historical_sales"]
        stores = flow_input["stores"]
        options = flow_input.get("options", {})

        df = pd.DataFrame(historical)

        # Encode store_id as an ordinal integer feature.
        enc = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
        df["store_enc"] = enc.fit_transform(df[["store_id"]])

        features = ["store_enc", "period", "price", "promotion"]
        X = df[features].values
        y = df["units_sold"].values

        seed = options.get("random_seed") or 42
        model = GradientBoostingRegressor(
            n_estimators=150,
            max_depth=4,
            learning_rate=0.1,
            random_state=seed,
        )
        model.fit(X, y)
        nextmv.log(
            f"Forecast model trained on {len(df)} observations "
            f"({df['store_id'].nunique()} stores, {df['period'].nunique()} periods)"
        )

        next_period = int(df["period"].max()) + 1
        forecasts = []
        demand = []
        for store in stores:
            store_enc = enc.transform([[store["id"]]])[0][0]
            avg_price = df.loc[df["store_id"] == store["id"], "price"].mean()
            X_pred = np.array([[store_enc, next_period, avg_price, 0]])
            predicted = max(0, int(round(model.predict(X_pred)[0])))
            demand.append(predicted)
            forecasts.append(
                {
                    "store_id": store["id"],
                    "store_name": store["name"],
                    "forecasted_demand": predicted,
                    "forecast_period": next_period,
                }
            )
            nextmv.log(f"  {store['name']}: period {next_period} forecast = {predicted} units")

        supply = [w["supply"] for w in flow_input["warehouses"]]
        nextmv.log(f"Total forecasted demand: {sum(demand)}, total supply: {sum(supply)}")

        return {
            # ── Fields consumed by the inventory-allocation sub-app ──────────
            "demand": demand,
            "supply": supply,
            "store_names": [s["name"] for s in stores],
            "warehouse_names": [w["name"] for w in flow_input["warehouses"]],
            # ── Pass-through for bundle_results visualizations ───────────────
            "forecasts": forecasts,
            "historical_sales": historical,
            "stores": stores,
            "warehouses": flow_input["warehouses"],
            "forecast_period": next_period,
        }

    @needs(predecessors=[forecast_demand])
    @app(app_id="inventory-allocation")
    @step
    def run_allocation() -> None:
        """
        Delegate execution to the inventory-allocation cloud app.

        Nextpipe passes the output of ``forecast_demand`` as the sub-app input.
        The ``inventory-allocation`` app reads it in explicit demand/supply mode
        and returns an allocation solution. Actual execution happens inside the
        sub-app; this step body is intentionally empty.
        """
        pass  # Execution happens in the sub-app.

    @needs(predecessors=[forecast_demand, run_allocation])
    @step
    def bundle_results(forecast_output: dict[str, Any], allocation_result: dict[str, Any]) -> nextmv.Output:
        """
        Combine forecast and allocation outputs into a unified response.

        Merges the forecasted demand data and the allocation solution, generates
        Plotly visualizations for both, and returns a ``nextmv.Output`` ready
        to be written by the caller.
        """

        allocation_solution = allocation_result.get("solution", {})
        allocation_metrics = allocation_result.get("metrics", {})

        forecast_vis = forecast_chart(
            forecasts=forecast_output["forecasts"],
            historical_sales=forecast_output["historical_sales"],
            tab_order=1,
        )
        allocation_vis = allocation_sankey(
            allocations=allocation_solution.get("allocations", []),
            tab_order=2,
        )

        return nextmv.Output(
            output_format=nextmv.ContentFormat.MULTI_FILE,
            solution_files=[
                nextmv.json_solution_file(
                    name="solution",
                    data={
                        "forecasts": forecast_output["forecasts"],
                        "allocations": allocation_solution.get("allocations", []),
                        "unmet_demand": allocation_solution.get("unmet_demand", []),
                    },
                )
            ],
            assets=[forecast_vis, allocation_vis],
            metrics=allocation_metrics,
        )


if __name__ == "__main__":
    main()
