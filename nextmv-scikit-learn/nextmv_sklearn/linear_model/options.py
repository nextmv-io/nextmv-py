"""Defines sklearn.linear_model options interoperability."""

import nextmv

LINEAR_REGRESSION_PARAMETERS = [
    nextmv.Parameter(
        name="fit_intercept",
        param_type=bool,
        description="Whether to calculate the intercept for this model.",
    ),
    nextmv.Parameter(
        name="copy_X",
        param_type=bool,
        description="If True, X will be copied; else, it may be overwritten.",
    ),
    nextmv.Parameter(
        name="n_jobs",
        param_type=int,
        description="The number of jobs to use for the computation.",
    ),
    nextmv.Parameter(
        name="positive",
        param_type=bool,
        description="When set to True, forces the coefficients to be positive.",
    ),
]


class LinearRegressionOptions:
    """Options for the sklearn.linear_model.LinearRegression."""

    def __init__(self):
        self.params = LINEAR_REGRESSION_PARAMETERS

    def to_nextmv(self) -> nextmv.Options:
        """Converts the options to a Nextmv options object."""

        return nextmv.Options(*self.params)
