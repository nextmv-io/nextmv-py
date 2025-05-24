"""Defines sklearn.linear_model options interoperability.

This module provides options for scikit-learn linear models to be used with Nextmv.

Classes
-------
LinearRegressionOptions
    Options for the sklearn.linear_model.LinearRegression.

Variables
---------
LINEAR_REGRESSION_PARAMETERS : list
    List of parameters for LinearRegression.
"""

import nextmv

LINEAR_REGRESSION_PARAMETERS = [
    nextmv.Option(
        name="fit_intercept",
        option_type=bool,
        description="Whether to calculate the intercept for this model.",
    ),
    nextmv.Option(
        name="copy_X",
        option_type=bool,
        description="If True, X will be copied; else, it may be overwritten.",
    ),
    nextmv.Option(
        name="n_jobs",
        option_type=int,
        description="The number of jobs to use for the computation.",
    ),
    nextmv.Option(
        name="positive",
        option_type=bool,
        description="When set to True, forces the coefficients to be positive.",
    ),
]
"""List of parameters for scikit-learn's LinearRegression model.

You can import LINEAR_REGRESSION_PARAMETERS directly from linear_model:

```python
from nextmv_sklearn.linear_model import LINEAR_REGRESSION_PARAMETERS
```

This list contains all the parameters that can be configured for a scikit-learn
LinearRegression model when using it through Nextmv.

Parameters
----------
fit_intercept : bool
    Whether to calculate the intercept for this model.
copy_X : bool
    If True, X will be copied; else, it may be overwritten.
n_jobs : int
    The number of jobs to use for the computation.
positive : bool
    When set to True, forces the coefficients to be positive.

See Also
--------
LinearRegressionOptions : Class that provides options for LinearRegression.
"""


class LinearRegressionOptions:
    """Options for the sklearn.linear_model.LinearRegression.

    You can import the LinearRegressionOptions class directly from linear_model:

    ```python
    from nextmv_sklearn.linear_model import LinearRegressionOptions
    ```

    This class provides an interface for configuring scikit-learn's
    LinearRegression model to work with Nextmv.

    Attributes
    ----------
    params : list
        List of LinearRegression parameters.

    Examples
    --------
    >>> from nextmv_sklearn.linear_model import LinearRegressionOptions
    >>> options = LinearRegressionOptions()
    >>> nextmv_options = options.to_nextmv()
    """

    def __init__(self):
        self.params = LINEAR_REGRESSION_PARAMETERS

    def to_nextmv(self) -> nextmv.Options:
        """Converts the options to a Nextmv options object.

        Returns
        -------
        nextmv.Options
            A Nextmv options object containing the LinearRegression parameters.

        Examples
        --------
        >>> options = LinearRegressionOptions()
        >>> nextmv_options = options.to_nextmv()
        """

        return nextmv.Options(*self.params)
