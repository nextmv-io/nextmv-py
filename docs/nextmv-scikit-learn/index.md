# Overview

<!-- markdownlint-disable MD033 MD013 -->

<p align="center">
  <a href="https://nextmv.io"><img src="https://cdn.prod.website-files.com/60dee0fad10d14c8ab66dd74/670960c61b28262959d81d39_blog-banner-plan-doors-optimization-models-nextmv-v2-p-2000.jpg" alt="Nextmv" width="45%"></a>
</p>
<p align="center">
    <em>Nextmv: The home for all your optimization work</em>
</p>
<p align="center">
<a href="https://pypi.org/project/nextmv-scikit-learn" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/nextmv-scikit-learn.svg?color=%2334D058" alt="Supported Python versions">
</a>
<a href="https://pypi.org/project/nextmv-scikit-learn" target="_blank">
    <img src="https://img.shields.io/pypi/v/nextmv-scikit-learn?color=%2334D058&label=nextmv-scikit-learn" alt="Package version">
</a>
</p>

<!-- markdownlint-enable MD033 MD013 -->

The [Nextmv & scikit-learn Python SDK][nextmv-scikit-learn],
`nextmv-scikit-learn`, is a package to interact programmatically with Nextmv
and the scikit-learn machine library, from Python. A great way to get started
is to check out the [community apps][community-apps-get-started]. The following
apps are a non-exhaustive list of concrete examples for using this SDK:

* [`python-nextmv-scikit-learn-diabetes`][python-nextmv-scikit-learn-diabetes]

!!! warning

    Please note that `nextmv-scikit-learn` is provided as _source-available_
    software (not _open-source_). For further information, please refer to the
    [LICENSE](https://github.com/nextmv-io/nextmv-py/blob/develop/nextmv-scikit-learn/LICENSE) file.

The `nextmv-scikit-learn` package is a wrapper around the `scikit-learn`
library to make it easy to use with Nextmv. It provides support for these
models:

* `dummy`:
  * [`DummyRegressor`][dummy-regressor]
* `ensemble`:
  * [`GradientBoostingRegressor`][gradient-boosting-regressor]
  * [`RandomForestRegressor`][random-forest-regressor]
* `linear_model`:
  * [`LinearRegression`][linear-regression]
* `neural_network`:
  * [`MLPRegressor`][mlp-regressor]
* `tree`:
  * [`DecisionTreeRegressor`][decision-tree-regressor]

## Installation

The package is hosted on [PyPI][nextmv-scikit-learn-pypi]. Python `>=3.9` is
required.

Install via `pip`:

```bash
pip install nextmv-scikit-learn
```

!!! tip

    Note that `nextmv-scikit-learn` installs the `nextmv_sklearn` package, which 
    is the importable name for the SDK.

[nextmv-scikit-learn-pypi]: https://pypi.org/project/nextmv-scikit-learn/
[nextmv-scikit-learn]: https://github.com/nextmv-io/nextmv-py/tree/develop/nextmv-scikit-learn
[community-apps-get-started]: https://docs.nextmv.io/docs/use-cases/community-apps/get-started
[python-nextmv-scikit-learn-diabetes]: https://github.com/nextmv-io/community-apps/blob/develop/python-nextmv-scikit-learn-diabetes
[dummy-regressor]: https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyRegressor.html
[linear-regression]: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html
[gradient-boosting-regressor]: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.GradientBoostingRegressor.html
[random-forest-regressor]: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html
[mlp-regressor]: https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPRegressor.html
[decision-tree-regressor]: https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeRegressor.html
