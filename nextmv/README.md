# Nextmv Python SDK

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

Welcome to `nextmv`, the general Python SDK for the Nextmv Platform.

📖 To learn more about `nextmv`, visit the [docs][docs].

## Installation

Requires Python `>=3.10`. Install using the Python package manager of your
choice:

- `pip`

    ```bash
    pip install nextmv
    ```

- `pipx`

    ```bash
    pipx install nextmv
    ```

- `uv`

    ```bash
    uv tool install nextmv
    ```

Install all optional dependencies (recommended) by specifying `"nextmv[all]"`
instead of just `"nextmv"`.

## CLI

The Nextmv CLI is installed automatically with the SDK. To verify installation,
run:

```bash
nextmv --help
```

If you are contributing to the CLI, please make sure you read the [CLI
Contributing Guide][cli-contributing].

[docs]: https://nextmv-py.docs.nextmv.io/en/latest/nextmv/
[cli-contributing]: nextmv/cli/CONTRIBUTING.md
