"""Defines sklearn.dummy options interoperability."""

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


class DummyRegressorOptions:
    """Options for the sklearn.dummy.DummyRegressor."""

    def __init__(self):
        self.params = DUMMY_REGRESSOR_PARAMETERS

    def to_nextmv(self) -> nextmv.Options:
        """Converts the options to a Nextmv options object."""

        return nextmv.Options(*self.params)
