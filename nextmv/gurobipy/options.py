"""Defines gurobipy options interoperability."""

import gurobipy as gp

import nextmv
from nextmv.options import Options
from nextmv.options import Parameter as P

# TODO: finish
GUROBIPY_PARAMETERS_TERMINATION = (
    P("bar_iter_limit", int, description="Barrier iteration limit"),
    P("best_bd_stop", float, description="Objective bound to stop optimization"),
    P("best_obj_stop", float, description="Objective value to stop optimization"),
    P("cutoff", float, description="Objective cutoff"),
    P("iteration_limit", float, description="Simplex iteration limit"),
    P("mem_limit", float, description="Memory limit"),
    P("node_limit", float, description="MIP node limit"),
    P("soft_mem_limit", float, description="Soft memory limit"),
    P("solution_limit", int, description="MIP solution limit"),
    P("time_limit", float, description="Time limit"),
    P("work_limit", float, description="Work limit"),
)

GUROBIPY_PARAMETERS_TOLERANCES = (
    P("mip_gap", float, description="Relative MIP optimality gap"),
    #    P("", None, description=""),
)

GUROBIPY_PARAMETERS_SIMPLEX = (
    P("inf_unbd_info", int, description="Additional info for infeasible/unbounded models"),
    #    P("", None, description=""),
)

GUROBIPY_PARAMETERS_BARRIER = (
    P("bar_correctors", int, description="Barrier central corrections"),
    #    P("", None, description=""),
)

GUROBIPY_PARAMETERS_SCALING = (
    P("obj_scale", int, description="Objective scaling"),
    P("scale_flag", int, description="Model scaling"),
)

GUROBIPY_PARAMETERS_MIP = (
    P("branch_dir", int, description="Preferred branch direction"),
    #    P("", None, description=""),
)

GUROBIPY_PARAMETERS_PRESOLVE = (
    P("agg_fill", int, description="Presolve aggregation fill level"),
    #    P("", None, description=""),
)

GUROBIPY_PARAMETERS_TUNING = (
    P("tune_base_settings", str, description="Comma-separated list of base parameter settings"),
    #    P("", None, description=""),
)

GUROBIPY_PARAMETERS_MULTIPLE_SOLUTIONS = (
    P("pool_gap", float, description="Maximum relative gap for stored solutions"),
    #    P("", None, description=""),
)

GUROBIPY_PARAMETERS_MIP_CUTS = (
    P("bqp_cuts", int, description="BQP cut generation"),
    #    P("", None, description=""),
)

GUROBIPY_PARAMETERS_MIP_CUTS = (
    P("bqp_cuts", int, description="BQP cut generation"),
    #    P("", None, description=""),
)

GUROBIPY_PARAMETERS_OTHER = (
    P("output_flag", int, description="Solver output control"),
    #    P("", None, description=""),
)

GUROBIPY_PARAMETERS = (
    GUROBIPY_PARAMETERS_TERMINATION
    + GUROBIPY_PARAMETERS_TOLERANCES
    + GUROBIPY_PARAMETERS_SIMPLEX
    + GUROBIPY_PARAMETERS_BARRIER
    + GUROBIPY_PARAMETERS_SCALING
    + GUROBIPY_PARAMETERS_MIP
    + GUROBIPY_PARAMETERS_PRESOLVE
    + GUROBIPY_PARAMETERS_TUNING
    + GUROBIPY_PARAMETERS_MULTIPLE_SOLUTIONS
    + GUROBIPY_PARAMETERS_MIP_CUTS
    + GUROBIPY_PARAMETERS_OTHER
)


class GurobipyOptions(Options):
    """Default options for gurobipy environments"""

    def __init__(self, *parameters: P):
        """Initializes options for a gurobipy environment."""
        return super().__init__(
            *GUROBIPY_PARAMETERS,
            *parameters,
        )

    def to_dict(self):
        """Converts the gurobipy options to a dict."""
        return {k: v for k, v in super().to_dict().items() if v is not None}

    def to_env(self, logfilename="", params: str = "", redirect_stdout: bool = True):
        """Creates a gurobipy environment."""
        if redirect_stdout:
            nextmv.redirect_stdout()

        e = gp.Env(logfilename=logfilename, empty=True)

        names = {p.name for p in GUROBIPY_PARAMETERS}
        for key, value in self.to_dict().items():
            if key in names and value is not None:
                e.setParam(key, value)

        if params:
            e.readParams(params)

        e.start()
        return e
