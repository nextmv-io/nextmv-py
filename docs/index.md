# The Nextmv Python SDKs

<!-- markdownlint-disable MD033 MD013 -->

<p align="center">
  <a href="https://nextmv.io"><img src="https://cdn.prod.website-files.com/60ca04db4f6f99b4bc1e050f/6509052c3f0767faf754ce3b_illustration-rabbits-decision-stacks-routing-scheduling-tier-3.svg" alt="Nextmv"></a>
</p>
<p align="center">
    <em>Nextmv Python SDKs: The home for all your optimization work</em>
</p>
<p align="center">
<a href="https://github.com/nextmv-io/nextmv-py/actions/workflows/python-test.yml" target="_blank">
    <img src="https://github.com/nextmv-io/nextmv-py/actions/workflows/python-test.yml/badge.svg?event=push&branch=develop" alt="Test">
</a>
<a href="https://github.com/nextmv-io/nextmv-py/actions/workflows/python-lint.yml" target="_blank">
    <img src="https://github.com/nextmv-io/nextmv-py/actions/workflows/python-lint.yml/badge.svg?event=push&branch=develop" alt="Test">
</a>
<a href="https://pypi.org/project/nextmv-scikit-learn" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/nextmv-scikit-learn.svg?color=%2334D058" alt="Supported Python versions">
</a>
</p>
<p align="center">
<a href="https://pypi.org/project/nextmv" target="_blank">
    <img src="https://img.shields.io/pypi/v/nextmv?color=%2334D058&label=nextmv" alt="Package version">
</a>
<a href="https://pypi.org/project/nextmv-gurobipy" target="_blank">
    <img src="https://img.shields.io/pypi/v/nextmv-gurobipy?color=%2334D058&label=nextmv-gurobipy" alt="Package version">
</a>
<a href="https://pypi.org/project/nextmv-scikit-learn" target="_blank">
    <img src="https://img.shields.io/pypi/v/nextmv-scikit-learn?color=%2334D058&label=nextmv-scikit-learn" alt="Package version">
</a>
</p>

<!-- markdownlint-enable MD033 MD013 -->

Nextmv offers several Python SDKs to help you work with decision models and the
Nextmv Cloud API:

* [`nextmv`][nextmv]: The general-purpose Python SDK for working with decision
      models and the Nextmv Cloud API.
* [`nextmv-gurobipy`][nextmv-gurobipy]: A Python SDK providing convenience
      functions for working with Gurobi (`gurobipy`) models in the Nextmv
      platform.
* [`nextmv-scikit-learn`][nextmv-scikit-learn]: A Python SDK providing
      convenience functions for working with `scikit-learn` models in the
      Nextmv platform.

These packages can be found in the [`nextmv-py`][nextmv-py] repository.

!!! warning

    Please review the license of each package, as they may not all have the same
    license. For example, `nextmv` is licensed under the Apache 2.0 license, while
    `nextmv-gurobipy` is licensed as BSL-1.1.

The best place to start with the Nextmv Python SDKs is to check out the
[community apps][community-apps-get-started]. These are fully-functional apps
that run both locally and on Nextmv Cloud. Please direct your attention to the
`python-*` apps.

There are two ways in which you can use community apps:

* Go to the [`community-apps` GitHub repository][community-apps-gh]. You can
  clone the repo, or view the apps directly in the GitHub UI.
* Use the [Nextmv CLI][cli] to first list the available apps and clone them
  locally. Check out the guide [here][community-apps-get-started].

[nextmv-py]: https://github.com/nextmv-io/nextmv-py
[nextmv]: ./nextmv/index.md
[nextmv-gurobipy]: ./nextmv-gurobipy/index.md
[nextmv-scikit-learn]: ./nextmv-scikit-learn/index.md
[community-apps-gh]: https://github.com/nextmv-io/community-apps
[cli]: https://docs.nextmv.io/docs/using-nextmv/reference/cli
[community-apps-get-started]: https://docs.nextmv.io/docs/use-cases/community-apps/get-started
