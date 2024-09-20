import gurobipy as gp
from gurobipy import GRB

from nextmv import output

GUROBIPY_STATUS_CODES = {
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


# TODO: version? provider?


class GurobipyResultStatistics(output.ResultStatistics):
    """Statistics about a specific gurobipy result."""

    @classmethod
    def from_model(cls, model: gp.Model, *args, **kwds):
        custom = {
            "status": GUROBIPY_STATUS_CODES.get(model.Status, "UNKNOWN"),
            "variables": model.NumVars,
            "constraints": model.NumConstrs,
        }
        custom.update(kwds.get("custom", {}))
        kwds.update(
            {
                "custom": custom,
                "duration": model.RunTime,
                "value": model.ObjVal,
            }
        )
        return cls(*args, **kwds)
