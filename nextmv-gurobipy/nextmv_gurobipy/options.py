"""Defines gurobipy options interoperability."""

import builtins

from gurobipy._paramdetails import param_details

import nextmv

PARAM_TYPE_TRANSLATION = {
    "double": "float",
    "string": "str",
    "int": "int",
    "bool": "bool",
}


class ModelOptions:
    """Options for the Gurobi model."""

    def __init__(self):
        params: list[nextmv.Parameter] = []

        for val in param_details.values():
            param_type_string = PARAM_TYPE_TRANSLATION[val["values"]["type"]]
            param_type = getattr(builtins, param_type_string)

            description = val["description"]
            if "%" in description:
                description = description.replace("%", "%%")

            p = nextmv.Parameter(
                name=val["name"],
                param_type=param_type,
                default=val["values"]["default"],
                description=description,
                required=False,
            )
            params.append(p)

        self.params = params

    def to_nextmv(self) -> nextmv.Options:
        """Converts the options to a Nextmv options object."""

        return nextmv.Options(*self.params)
