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
    # Cluster manager only
    "Username",
]
"""Parameters that are not applicable to the SDK."""

# Translation of Gurobi parameter types to Python types.
OPTION_TYPE_TRANSLATION = {
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

    Methods:
    ----------
    to_nextmv:
        Converts the options to a Nextmv options object.
    """

    def __init__(self):
        options: list[nextmv.Option] = []

        for val in param_details.values():
            name = val["name"]
            if name in SKIP_PARAMETERS:
                continue

            option_type_string = OPTION_TYPE_TRANSLATION[val["values"]["type"]]
            option_type = getattr(builtins, option_type_string)

            description = val["description"]
            if "%" in description:
                description = description.replace("%", "%%")

            o = nextmv.Option(
                name=name,
                option_type=option_type,
                default=val["values"]["default"],
                description=description,
                required=False,
            )
            options.append(o)

        self.options = options

    def to_nextmv(self) -> nextmv.Options:
        """Converts the options to a Nextmv options object."""

        return nextmv.Options(*self.options)
