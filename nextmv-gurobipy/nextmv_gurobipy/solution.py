"""Defines gurobipy solution interoperability."""

import gurobipy as gp


def Solution(model: gp.Model) -> dict[str, any] | None:
    """
    Creates a basic solution dictionary from a Gurobi model. The simple
    solution dictionary contains the variable name and the value of the
    variable for each variable in the model. If the model has not been solved,
    it will return `None`. Although this method is a good starting point to
    visualize the solution of a Gurobi model, we recommend that you implement
    your own logic to extract the information you need.

    Parameters:
    ----------
    model: gp.Model
        The Gurobi model.

    Returns:
    ----------
    dict[str, any] | None
        The solution dictionary.
    """

    if model.SolCount < 1:
        return None

    return {x.VarName: x.X for x in model.getVars()}
