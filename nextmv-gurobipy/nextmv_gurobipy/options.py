"""Defines gurobipy options interoperability.

This module provides tools for converting Gurobi optimization parameters to
Nextmv options. It includes functions and classes for handling Gurobi parameter
configurations and translating them to the Nextmv options format.

Classes
-------
ModelOptions
    Options for the Gurobi model that can be converted to Nextmv options.

Constants
---------
SKIP_PARAMETERS : list
    Parameters that are not applicable to the SDK.
OPTION_TYPE_TRANSLATION : dict
    Translation of Gurobi parameter types to Python types.
"""

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
"""Parameters that are not applicable to the SDK.

You can import the `SKIP_PARAMETERS` list directly from `nextmv_gurobipy`:

```python
from nextmv_gurobipy import SKIP_PARAMETERS
```

This list contains Gurobi parameters that are not compatible with or not needed
by the Nextmv SDK. Parameters are excluded for various reasons:

- Some depend on the optimization sense (like "Cutoff")
- Some are CLI-only parameters not applicable to SDK usage
- Some are related to cluster management
"""

OPTION_TYPE_TRANSLATION = {
    "double": "float",
    "string": "str",
    "int": "int",
    "bool": "bool",
}
"""Translation of Gurobi parameter types to Python types.

You can import the `OPTION_TYPE_TRANSLATION` dictionary directly from `nextmv_gurobipy`:

```python
from nextmv_gurobipy import OPTION_TYPE_TRANSLATION
```

This dictionary maps Gurobi parameter type strings to their corresponding
Python type names, which are used to convert Gurobi parameters to Nextmv
options.

Notes
-----
The mapping is used during options initialization to ensure proper type conversion
between Gurobi's parameter system and Python's native types.
"""


class ModelOptions:
    """Options for the Gurobi model with conversion to Nextmv options format.

    You can import the `ModelOptions` class directly from `nextmv_gurobipy`:

    ```python
    from nextmv_gurobipy import ModelOptions
    ```

    This class loads and encapsulates all applicable Gurobi parameters, making them
    available as Nextmv options. It automatically excludes parameters that are not
    applicable to the SDK environment, as defined in the `SKIP_PARAMETERS` list.

    The complete list of Gurobi parameters is loaded from the Gurobi parameter details.
    The reference documentation for these parameters can be found at:
    https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html#parameter-reference.

    Attributes
    ----------
    options : list[nextmv.Option]
        List of Nextmv options created from Gurobi parameters.

    Methods
    -------
    to_nextmv()
        Converts the options to a Nextmv options object.

    Examples
    --------
    >>> from nextmv_gurobipy import ModelOptions
    >>> options = ModelOptions()
    >>> nextmv_options = options.to_nextmv()
    >>> # These options can now be used with a Nextmv model
    """

    def __init__(self):
        """Initialize ModelOptions with all supported Gurobi parameters.

        This constructor creates Nextmv options from all Gurobi parameters
        that are applicable to the SDK (excluding those in SKIP_PARAMETERS).
        It handles type conversion and description formatting for each parameter.

        Returns
        -------
        None
        """
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
        """Converts the options to a Nextmv options object.

        This method creates a Nextmv Options object from the list of Option
        objects stored in this ModelOptions instance. The resulting object can
        be used with Nextmv models and functions.

        Returns
        -------
        nextmv.Options
            A Nextmv options object containing all the Gurobi parameters.

        Examples
        --------
        >>> from nextmv_gurobipy import ModelOptions
        >>> options = ModelOptions()
        >>> nextmv_options = options.to_nextmv()
        >>> # The returned object can be used with Nextmv models
        """

        return nextmv.Options(*self.options)
