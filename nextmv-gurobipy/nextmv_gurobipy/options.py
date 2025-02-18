"""Defines gurobipy options interoperability."""

import builtins

from gurobipy._paramdetails import param_details

import nextmv

SKIP_PARAMETERS = [
    # Depends on the sense, so hard to set "generally" beforehand.
    # https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html#cutoff
    "Cutoff",
    # CLI only, so not applicable to the SDK.
    "InputFile",
    "ConcurrentSettings",
    "MultiObjSettings",
    "TuneBaseSettings",
    "TuneParams",
    "TuneUseFilename",
]
"""Parameters that are not applicable to the SDK."""

# Translation of Gurobi parameter types to Python types.
PARAM_TYPE_TRANSLATION = {
    "double": "float",
    "string": "str",
    "int": "int",
    "bool": "bool",
}


class ModelOptions:
    """
    Options for the Gurobi model. Use the `to_nextmv` method to convert the
    options to a Nextmv options object.

    The complete list of Gurobi parameters is loaded. The reference can be
    found at:
    https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html#parameter-reference.

    Some parameters are skipped, as they are not applicable to the SDK (they
    might be Gurobi CLI only, for example). The `SKIP_PARAMETERS` list contains
    the names of the parameters that are not loaded as part of this class.

    Attributes:
    ----------
    parameters: list[nextmv.Parameter]
        The list of parameters for the Gurobi model

    Methods:
    ----------
    to_nextmv:
        Converts the options to a Nextmv options object.
    """

    def __init__(self):
        parameters: list[nextmv.Parameter] = []

        for val in param_details.values():
            name = val["name"]
            if name in SKIP_PARAMETERS:
                continue

            param_type_string = PARAM_TYPE_TRANSLATION[val["values"]["type"]]
            param_type = getattr(builtins, param_type_string)

            description = val["description"]
            if "%" in description:
                description = description.replace("%", "%%")

            p = nextmv.Parameter(
                name=name,
                param_type=param_type,
                default=val["values"]["default"],
                description=description,
                required=False,
            )
            parameters.append(p)

        self.params = parameters

    def to_nextmv(self) -> nextmv.Options:
        """Converts the options to a Nextmv options object."""

        return nextmv.Options(*self.params)
