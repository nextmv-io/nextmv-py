"""Defines gurobipy model interoperability."""

import os
from typing import Optional

import gurobipy as gp
from gurobipy._paramdetails import param_details

import nextmv


def Model(options: nextmv.Options, license_path: Optional[str] = "") -> gp.Model:
    """
    Creates a Gurobi model, using Nextmv options. The returned type is a
    `gurobipy.Model` class. This means that once the Gurobi model is created,
    it can be used as any other Gurobi model. This loader will look for the
    `gurobi.lic` file in the provided `license_path`. If the file is not found,
    it will not be read. This means that by default, you will be working with
    Gurobi’s community license.

    Only the parameters that are available in the Gurobi API are set. If a
    parameter is not available, it will be skipped.

    This function has some side effects that you should be aware of:
    - It redirects the solver chatter to stderr.
    - It sets the provider to "gurobi" in the options.

    Parameters:
    ----------
    options: nextmv.Options
        The options for the Gurobi model.

    Returns:
    ----------
    gp.Model
        The Gurobi model.
    """

    # Solver chatter is logged to stderr.
    nextmv.redirect_stdout()

    env = gp.Env(empty=True)

    file_path = os.path.join(license_path, "gurobi.lic")
    if os.path.isfile(file_path):
        env.readParams(file_path)

    env.start()
    model = gp.Model(env=env)

    gp_names = [val["name"] for val in param_details.values()]
    for parameter in options.parameters:
        name = parameter.name
        if name not in gp_names:
            continue

        model.setParam(name, getattr(options, name))

    options.provider = "gurobi"

    return model
