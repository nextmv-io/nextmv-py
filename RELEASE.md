# Release instructions

## Stable release

Open a PR against the `develop` branch with the following change:

* Update the version in the `__about__.py` file of the packages you want to
  release.

After the PR is merged, the `release.yml` workflow will be triggered and it
will automatically create a release and publish the packages to PyPI.

## Pre-release

Use the manual workflow dispatch in the GitHub Actions UI to trigger the
`release.yml`

Specify the following inputs:

* `VERSION`: The version to release.
* `PACKAGE`: The package to release.

The action will trigger the release workflow for the pre-release. When you are
ready to release, please follow the instructions in the [stable
release](#stable-release) section.

Please note the following:

* When releasing manually, only pre-release versions are allowed.
* Pre-releases can only be created on branches other than `develop`.
