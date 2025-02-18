"""Defines sklearn.dummy options interoperability."""

import nextmv

DUMMY_REGRESSOR_PARAMETERS = [
    nextmv.Parameter(
        name="strategy",
        param_type=str,
        choices=["mean", "median", "quantile", "constant"],
        description="Strategy to use to generate predictions.",
    ),
    nextmv.Parameter(
        name="constant",
        param_type=float,
        description='The explicit constant as predicted by the "constant" strategy.',
    ),
    nextmv.Parameter(
        name="quantile",
        param_type=float,
        description='The quantile to predict using the "quantile" strategy.',
    ),
]


class DummyRegressorOptions:
    """Options for the sklearn.dummy.DummyRegressor."""

    def __init__(self):
        self.params = DUMMY_REGRESSOR_PARAMETERS

    def to_nextmv(self) -> nextmv.Options:
        """Converts the options to a Nextmv options object."""

        return nextmv.Options(*self.params)
