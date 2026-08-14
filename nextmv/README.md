# Nextmv Python SDK

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

Welcome to `nextmv`, the general Python SDK for the Nextmv Platform.

📖 To learn more visit the [Python SDK docs][python-sdk-docs].

If you are contributing, please make sure you read the [Contributing Guide][contributing].

## Installation

Requires Python `>=3.10`. Install using the Python package manager of your
choice:

- `uv`

    ```bash
    uv add nextmv
    ```

- `pip`

    ```bash
    pip install nextmv
    ```

- `pipx`

    ```bash
    pipx install nextmv
    ```

## CLI

The Nextmv CLI is built on top of the Python SDK.

📖 To learn more visit the [CLI docs][cli-docs].

### CLI Installation

When using `pip` or `pipx`, use the same command as for installing the SDK.
When using `uv`, install the CLI with the following command:

```bash
uv tool install nextmv
```

To verify installation, run:

```bash
nextmv --help
```

For a quick start, run:

```bash
nextmv init
```

[python-sdk-docs]: https://docs.nextmv.io/python-sdk
[cli-docs]: https://docs.nextmv.io/cli
[contributing]: ./CONTRIBUTING.md
