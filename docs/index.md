# The Nextmv Python SDKs

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
