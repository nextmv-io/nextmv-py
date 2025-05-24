# Overview

<!-- markdownlint-disable MD033 MD013 -->

<p align="center">
  <a href="https://nextmv.io"><img src="https://cdn.prod.website-files.com/60dee0fad10d14c8ab66dd74/674628a824bc14307c1727aa_blog-prototype-p-2000.png" alt="Nextmv" width="45%"></a>
</p>
<p align="center">
    <em>Nextmv: The home for all your optimization work</em>
</p>
<p align="center">
<a href="https://pypi.org/project/nextmv" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/nextmv.svg?color=%2334D058" alt="Supported Python versions">
</a>
<a href="https://pypi.org/project/nextmv" target="_blank">
    <img src="https://img.shields.io/pypi/v/nextmv?color=%2334D058&label=nextmv" alt="Package version">
</a>
</p>

<!-- markdownlint-enable MD033 MD013 -->

The [Nextmv Python SDK][nextmv], `nextmv`, is a package to interact
programmatically with the Nextmv Platform from Python. A great way to get
started is to check out the [community apps][community-apps-get-started]. The
following apps are a non-exhaustive list of concrete examples for using this
SDK:

* [`python-ampl-facilitylocation`][python-ampl-facilitylocation],
  [`python-ampl-knapsack`][python-ampl-knapsack],
  [`python-ampl-priceoptimization`][python-ampl-priceoptimization]
* [`python-gurobi-knapsack`][python-gurobi-knapsack]
* [`python-hello-world`][python-hello-world]
* [`python-hexaly-knapsack`][python-hexaly-knapsack]
* [`python-highs-knapsack`][python-highs-knapsack]
* [`python-nextroute`][python-nextroute]
* [`python-ortools-costflow`][python-ortools-costflow],
  [`python-ortools-demandforecasting`][python-ortools-demandforecasting],
  [`python-ortools-knapsack-multicsv`][python-ortools-knapsack-multicsv],
  [`python-ortools-knapsack`][python-ortools-knapsack],
  [`python-ortools-routing`][python-ortools-routing],
  [`python-ortools-shiftassignment`][python-ortools-shiftassignment],
  [`python-ortools-shiftplanning`][python-ortools-shiftplanning]
* [`python-pyomo-knapsack`][python-pyomo-knapsack],
  [`python-pyomo-shiftassignment`][python-pyomo-shiftassignment],
  [`python-pyomo-shiftplanning`][python-pyomo-shiftplanning]
* [`python-pyoptinterface-knapsack`][python-pyoptinterface-knapsack]
* [`python-pyvroom-routing`][python-pyvroom-routing]
* [`python-xpress-knapsack`][python-xpress-knapsack]

## Installation

The package is hosted on [PyPI][nextmv-pypi]. Python `>=3.9` is required.

Install via `pip`:

```bash
pip install nextmv
```

Install all optional dependencies (recommended):

```bash
pip install "nextmv[all]"
```

[nextmv-pypi]: https://pypi.org/project/nextmv/
[nextmv]: https://github.com/nextmv-io/nextmv-py/tree/develop/nextmv
[community-apps-get-started]: https://docs.nextmv.io/docs/use-cases/community-apps/get-started

[python-ampl-facilitylocation]: https://github.com/nextmv-io/community-apps/blob/develop/python-ampl-facilitylocation
[python-ampl-knapsack]: https://github.com/nextmv-io/community-apps/blob/develop/python-ampl-knapsack
[python-ampl-priceoptimization]: https://github.com/nextmv-io/community-apps/blob/develop/python-ampl-priceoptimization
[python-gurobi-knapsack]: https://github.com/nextmv-io/community-apps/blob/develop/python-gurobi-knapsack
[python-hello-world]: https://github.com/nextmv-io/community-apps/blob/develop/python-hello-world
[python-hexaly-knapsack]: https://github.com/nextmv-io/community-apps/blob/develop/python-hexaly-knapsack
[python-highs-knapsack]: https://github.com/nextmv-io/community-apps/blob/develop/python-highs-knapsack
[python-nextroute]: https://github.com/nextmv-io/community-apps/blob/develop/python-nextroute
[python-ortools-costflow]: https://github.com/nextmv-io/community-apps/blob/develop/python-ortools-costflow
[python-ortools-demandforecasting]: https://github.com/nextmv-io/community-apps/blob/develop/python-ortools-demandforecasting
[python-ortools-knapsack-multicsv]: https://github.com/nextmv-io/community-apps/blob/develop/python-ortools-knapsack-multicsv
[python-ortools-knapsack]: https://github.com/nextmv-io/community-apps/blob/develop/python-ortools-knapsack
[python-ortools-routing]: https://github.com/nextmv-io/community-apps/blob/develop/python-ortools-routing
[python-ortools-shiftassignment]: https://github.com/nextmv-io/community-apps/blob/develop/python-ortools-shiftassignment
[python-ortools-shiftplanning]: https://github.com/nextmv-io/community-apps/blob/develop/python-ortools-shiftplanning
[python-pyomo-knapsack]: https://github.com/nextmv-io/community-apps/blob/develop/python-pyomo-knapsack
[python-pyomo-shiftassignment]: https://github.com/nextmv-io/community-apps/blob/develop/python-pyomo-shiftassignment
[python-pyomo-shiftplanning]: https://github.com/nextmv-io/community-apps/blob/develop/python-pyomo-shiftplanning
[python-pyoptinterface-knapsack]: https://github.com/nextmv-io/community-apps/blob/develop/python-pyoptinterface-knapsack
[python-pyvroom-routing]: https://github.com/nextmv-io/community-apps/blob/develop/python-pyvroom-routing
[python-xpress-knapsack]: https://github.com/nextmv-io/community-apps/blob/develop/python-xpress-knapsack
