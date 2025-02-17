"""Defines gurobipy statistics interoperability."""

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


def Statistics(model: gp.Model) -> nextmv.Statistics:
    """
    Creates a Nextmv statistics object from a Gurobi model, once it has been
    optimized. The statistics returned are quite basic, and should be extended
    according to the custom metrics that the user wants to track.

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

    Returns:
    ----------
    nextmv.Statistics
        The Nextmv statistics object.
    """

    return nextmv.Statistics(
        run=nextmv.RunStatistics(),
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
