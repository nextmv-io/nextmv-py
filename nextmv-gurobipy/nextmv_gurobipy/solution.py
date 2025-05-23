"""Defines gurobipy solution interoperability.

This module provides functionality for interacting with Gurobi solutions.

Functions
---------
ModelSolution
    Creates a basic solution dictionary from a Gurobi model.
"""

from typing import Any, Optional

import gurobipy as gp


def ModelSolution(model: gp.Model) -> Optional[dict[str, Any]]:
    """
    Creates a basic solution dictionary from a Gurobi model.

    You can import the `ModelSolution` function directly from `nextmv_gurobipy`:

    ```python
    from nextmv_gurobipy import ModelSolution
    ```

    The simple solution dictionary contains the variable name and the value of the
    variable for each variable in the model. If the model has not been solved,
    it will return `None`. Although this method is a good starting point to
    visualize the solution of a Gurobi model, we recommend that you implement
    your own logic to extract the information you need.

    Parameters
    ----------
    model : gp.Model
        The Gurobi model that has been solved.

    Returns
    -------
    dict[str, Any] or None
        A dictionary with variable names as keys and their optimal values as values.
        Returns None if the model has not been solved.

    Examples
    --------
    >>> import gurobipy as gp
    >>> from nextmv_gurobipy import ModelSolution
    >>>
    >>> # Create and solve a simple model
    >>> model = gp.Model("example")
    >>> x = model.addVar(name="x")
    >>> y = model.addVar(name="y")
    >>> model.addConstr(x + y <= 1)
    >>> model.setObjective(x + y, gp.GRB.MAXIMIZE)
    >>> model.optimize()
    >>>
    >>> # Get the solution dictionary
    >>> solution = ModelSolution(model)
    >>> print(solution)
    {'x': 0.5, 'y': 0.5}
    """

    if model.SolCount < 1:
        return None

    return {x.VarName: x.X for x in model.getVars()}
