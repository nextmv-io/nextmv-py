"""Defines sklearn.dummy options interoperability.

This module provides options for scikit-learn's dummy models. It includes classes
and global variables to help configure and use these models with the Nextmv platform.

Classes
-------
DummyRegressorOptions
    Options for the sklearn.dummy.DummyRegressor.

Global Variables
---------------
DUMMY_REGRESSOR_PARAMETERS : list
    List of parameters for the DummyRegressor class.
"""

import nextmv

DUMMY_REGRESSOR_PARAMETERS = [
    nextmv.Option(
        name="strategy",
        option_type=str,
        choices=["mean", "median", "quantile", "constant"],
        description="Strategy to use to generate predictions.",
    ),
    nextmv.Option(
        name="constant",
        option_type=float,
        description='The explicit constant as predicted by the "constant" strategy.',
    ),
    nextmv.Option(
        name="quantile",
        option_type=float,
        description='The quantile to predict using the "quantile" strategy.',
    ),
]
"""
List of parameters for configuring DummyRegressor.

You can import DUMMY_REGRESSOR_PARAMETERS directly from dummy:

```python
from nextmv_sklearn.dummy import DUMMY_REGRESSOR_PARAMETERS
```

This list contains the options that can be passed to the DummyRegressor model in
scikit-learn. The parameters include:
- strategy: Strategy to use to generate predictions.
- constant: The explicit constant as predicted by the "constant" strategy.
- quantile: The quantile to predict using the "quantile" strategy.

See Also
--------
DummyRegressorOptions : Class that uses these parameters.
sklearn.dummy.DummyRegressor : The scikit-learn class these options configure.
"""


class DummyRegressorOptions:
    """Options for the sklearn.dummy.DummyRegressor.

    You can import the DummyRegressorOptions class directly from dummy:

    ```python
    from nextmv_sklearn.dummy import DummyRegressorOptions
    ```

    This class provides a wrapper for the options used by scikit-learn's
    DummyRegressor. It allows for easier configuration and integration with
    the Nextmv platform.

    Attributes
    ----------
    params : list
        List of Nextmv Option objects for DummyRegressor parameters.

    Examples
    --------
    >>> from nextmv_sklearn.dummy import DummyRegressorOptions
    >>> options = DummyRegressorOptions()
    >>> nextmv_options = options.to_nextmv()
    """

    def __init__(self):
        """Initialize the DummyRegressorOptions.

        Creates a new instance with default parameters for the
        sklearn.dummy.DummyRegressor.
        """
        self.params = DUMMY_REGRESSOR_PARAMETERS

    def to_nextmv(self) -> nextmv.Options:
        """Converts the options to a Nextmv options object.

        Returns
        -------
        nextmv.Options
            A Nextmv options object containing the parameters for the
            sklearn.dummy.DummyRegressor.

        Examples
        --------
        >>> options = DummyRegressorOptions()
        >>> nextmv_options = options.to_nextmv()
        >>> # Use nextmv_options in your Nextmv application
        """

        return nextmv.Options(*self.params)
