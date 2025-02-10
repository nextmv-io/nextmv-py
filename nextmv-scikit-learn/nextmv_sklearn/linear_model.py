"""Defines linear regression interoperability classes."""

import nextmv


class LinearRegressionOptions:
    """Options for the sklearn.linear_model.LinearRegression."""

    def __init__(self):
        params: list[nextmv.Parameter] = [
            nextmv.Parameter(
                name="fit_intercept",
                param_Type=bool,
                description="Whether to calculate the intercept for this model.",
            ),
            nextmv.Parameter(
                name="copy_X",
                param_Type=bool,
                description="If True, X will be copied; else, it may be overwritten.",
            ),
            nextmv.Parameter(
                name="n_jobs",
                param_Type=int,
                description="The number of jobs to use for the computation.",
            ),
            nextmv.Parameter(
                name="positive",
                param_Type=bool,
                description="When set to True, forces the coefficients to be positive.",
            ),
        ]

        self.params = params

    def to_nextmv(self) -> nextmv.Options:
        """Converts the options to a Nextmv options object."""

        return nextmv.Options(*self.params)
