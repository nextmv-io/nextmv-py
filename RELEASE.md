# Release

A reusable workflow is used to release the package. Nextmv team members: please
go to the corresponding repository for more information.

## Stable release

Open a PR against the `develop` branch with the following change:

* Update the version in the `__about__.py` file of the packages you want to
  release.

After the PR is merged, the `release.yml` workflow will be triggered and it
will automatically create a release and publish the packages to PyPI.

## Pre-release

Update the version in the `__about__.py` file of the packages you want to
release to a dev tag. When a commit is pushed, the `release.yml` workflow will
be triggered and it will automatically create a release and publish the packages
to PyPI.

Delete this.

Also delete this.
