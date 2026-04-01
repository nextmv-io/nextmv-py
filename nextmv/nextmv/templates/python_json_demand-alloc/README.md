# Python Demand Forecast + Inventory Allocation

This folder contains two Nextmv applications that together implement a
demand-forecast and inventory-allocation pipeline.

* `allocation/`: Runs the inventory-allocation optimization model. Takes
  warehouse, store, and demand data as input and solves the allocation problem
  using a MIP solver. Read the `README.md` here first for instructions on how
  to push the allocation app to Nextmv Cloud, which is a dependency for the
  workflow app. This is a `json` app.
* `workflow/`: Orchestrates the full two-stage pipeline. Runs the
  demand-forecast stage followed by the allocation stage using Nextpipe. Read
  the `README.md` here after reading the allocation README for instructions on
  how to run the workflow app. This is a `json` app.
