"""Defines gurobipy statistics interoperability."""

import time
from typing import Optional

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


def ModelStatistics(model: gp.Model, run_duration_start: Optional[float] = None) -> nextmv.Statistics:
    """
    Creates a Nextmv statistics object from a Gurobi model, once it has been
    optimized. The statistics returned are quite basic, and should be extended
    according to the custom metrics that the user wants to track. The optional
    `run_duration_start` parameter can be used to set the start time of the
    whole run. This is useful to separate the run time from the solve time.

    Example:
    ----------
    >>> model = Model(options, ".")
    >>> ...
    >>> model.optimize()
    >>> stats = Statistics(model)
    >>> ... # Add information to the statistics object.

    Parameters:
    ----------
    model: gp.Model
        The Gurobi model.
    run_duration_start: float | None
        The start time of the run.

    Returns:
    ----------
    nextmv.Statistics
        The Nextmv statistics object.
    """

    run = nextmv.RunStatistics()
    if run_duration_start is not None:
        run.duration = time.time() - run_duration_start

    return nextmv.Statistics(
        run=run,
        result=nextmv.ResultStatistics(
            duration=model.Runtime,
            value=model.ObjVal,
            custom={
                "status": STATUS.get(model.Status, "UNKNOWN"),
                "variables": model.NumVars,
                "constraints": model.NumConstrs,
            },
        ),
        series_data=nextmv.SeriesData(),
    )
