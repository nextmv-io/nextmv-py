"""Defines gurobipy statistics interoperability.

This module provides utilities to convert Gurobi optimization results into
Nextmv statistics objects for consistency across the Nextmv platform.

Functions
---------
ModelStatistics
    Creates a Nextmv statistics object from a Gurobi model.

Variables
---------
STATUS
    Mapping between Gurobi status codes and their string representations.
"""

import time
from typing import Any, Optional

import gurobipy as gp
from gurobipy import GRB

import nextmv

STATUS = {
    GRB.LOADED: "LOADED",
    GRB.OPTIMAL: "OPTIMAL",
    GRB.INFEASIBLE: "INFEASIBLE",
    GRB.INF_OR_UNBD: "INF_OR_UNBD",
    GRB.UNBOUNDED: "UNBOUNDED",
    GRB.CUTOFF: "CUTOFF",
    GRB.ITERATION_LIMIT: "ITERATION_LIMIT",
    GRB.NODE_LIMIT: "NODE_LIMIT",
    GRB.TIME_LIMIT: "TIME_LIMIT",
    GRB.SOLUTION_LIMIT: "SOLUTION_LIMIT",
    GRB.INTERRUPTED: "INTERRUPTED",
    GRB.NUMERIC: "NUMERIC",
    GRB.SUBOPTIMAL: "SUBOPTIMAL",
    GRB.INPROGRESS: "INPROGRESS",
    GRB.USER_OBJ_LIMIT: "USER_OBJ_LIMIT",
    GRB.WORK_LIMIT: "WORK_LIMIT",
    GRB.MEM_LIMIT: "MEM_LIMIT",
}
"""
dict: Mapping between Gurobi status codes and their string representations.

You can import the `STATUS` dictionary directly from `nextmv_gurobipy`:

```python
from nextmv_gurobipy import STATUS
```

This dictionary converts numerical Gurobi status codes to human-readable
string representations for use in statistics reporting. The status codes
indicate the outcome of the optimization process (e.g., whether an optimal
solution was found, or the solver hit a limit).

Examples
--------
>>> from nextmv_gurobipy import STATUS
>>> from gurobipy import GRB
>>> print(STATUS[GRB.OPTIMAL])
'OPTIMAL'
>>> print(STATUS[GRB.TIME_LIMIT])
'TIME_LIMIT'
"""


def ModelStatistics(model: gp.Model, run_duration_start: Optional[float] = None) -> nextmv.Statistics:
    """
    Creates a Nextmv statistics object from a Gurobi model, once it has been optimized.

    You can import the `ModelStatistics` function directly from `nextmv_gurobipy`:

    ```python
    from nextmv_gurobipy import ModelStatistics
    ```

    The statistics returned are quite basic, and should be extended
    according to the custom metrics that the user wants to track. The optional
    `run_duration_start` parameter can be used to set the start time of the
    whole run. This is useful to separate the run time from the solve time.

    Parameters
    ----------
    model : gp.Model
        The Gurobi model after optimization.
    run_duration_start : float, optional
        The start time of the run in seconds since the epoch, as returned by `time.time()`.
        If provided, the total run duration will be calculated.

    Returns
    -------
    nextmv.Statistics
        The Nextmv statistics object containing run information, result statistics,
        and series data.

    Examples
    --------
    >>> import time
    >>> from nextmv_gurobipy import Model, Options, ModelStatistics
    >>>
    >>> start_time = time.time()
    >>> options = Options()
    >>> model = Model(options, ".")
    >>> # Create and configure your model
    >>> model.optimize()
    >>> stats = ModelStatistics(model, start_time)
    >>> # Add additional information to the statistics object if needed
    """

    run = nextmv.RunStatistics()
    if run_duration_start is not None:
        run.duration = time.time() - run_duration_start

    def safe_get(attr_name: str) -> Optional[Any]:
        """
        Safely get an attribute from the model by returning None if it does not exist.

        Parameters
        ----------
        attr_name : str
            Name of the attribute to retrieve from the model.

        Returns
        -------
        Any or None
            The value of the attribute if it exists, None otherwise.
        """
        return getattr(model, attr_name, None)

    return nextmv.Statistics(
        run=run,
        result=nextmv.ResultStatistics(
            duration=safe_get("Runtime"),
            value=safe_get("ObjVal"),
            custom={
                "status": STATUS.get(safe_get("Status"), "UNKNOWN"),
                "variables": safe_get("NumVars"),
                "constraints": safe_get("NumConstrs"),
            },
        ),
        series_data=nextmv.SeriesData(),
    )
