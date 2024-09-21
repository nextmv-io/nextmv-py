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
    P("time_limit", float, description="Time limit"),
    P("work_limit", float, description="Work limit"),
)

GUROBIPY_PARAMETERS_TOLERANCES = (P("mip_gap", float, description="Relative MIP optimality gap"),)

GUROBIPY_PARAMETERS_OTHER = (P("output_flag", int, description="Solver output control"),)

GUROBIPY_PARAMETERS = GUROBIPY_PARAMETERS_TERMINATION + GUROBIPY_PARAMETERS_TOLERANCES + GUROBIPY_PARAMETERS_OTHER


class GurobipyOptions(Options):
    """Default options for gurobipy environments"""

    def __init__(self, *parameters: p):
        """Initializes options for a gurobipy environment."""
        return super().__init__(*(GUROBIPY_PARAMETERS + parameters))

    def to_env(self, logfilename="", params: str = "", redirect_stdout: bool = True):
        """Creates a gurobipy environment."""
        if redirect_stdout:
            nextmv.redirect_stdout()

        e = gp.Env(logfilename=logfilename, empty=True)

        names = {p.name for p in GUROBIPY_PARAMETERS}
        for key, value in self.to_dict().items():
            if key in names:
                e.setParam(key, value)

        if params:
            e.readParams(params)

        e.start()
        return e
