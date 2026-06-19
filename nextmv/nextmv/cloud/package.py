"""Module with the logic for packaging an app to Nextmv Cloud."""

import gzip
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

import rich

from nextmv._uv_handler import _find_uv_binary
from nextmv.cache import dep_cache_key, format_bytes, get_cached_dep, store_dep
from nextmv.logger import log
from nextmv.manifest import (MANIFEST_FILE_NAME, Manifest, ManifestBuild,
                             ManifestType, ModelConfiguration, find_files,
                             read_pyproject_dependencies)
from nextmv.model import Model, _cleanup_python_model

_IO_CHUNK_SIZE = 65536
"""
Buffer size in bytes for streaming I/O operations (64 KiB).

Matches the default used by :func:`shutil.copyfileobj` and is a common OS
page-aligned I/O buffer size that balances syscall overhead against memory
pressure for sequential reads and writes.
"""


def package(
    app_dir: str,
    manifest: Manifest,
    model: Model | None = None,
    model_configuration: ModelConfiguration | None = None,
    verbose: bool = False,
    rich_print: bool = False,
    no_cache: bool = False,
) -> tuple[str, str]:
    """
    Package the app into a tarball.

    Parameters
    ----------
    app_dir : str
        The directory of the application to package.
    manifest : Manifest
        The app manifest describing the application type, files, and dependencies.
    model : Model, optional
        The Python model to encode and include in the package.
    model_configuration : ModelConfiguration, optional
        The configuration for encoding the Python model.
    verbose : bool, optional
        Whether to print verbose logs.
    rich_print : bool, optional
        Whether to use rich printing for verbose logs.
    no_cache : bool, default=False
        When working with Python, dependencies are cached to speed up
        subsequent pushes. Setting no_cache to True will skip using the
        cache and force a fresh build of all dependencies. This is useful
        when you want to ensure that you are pushing the most up-to-date
        versions of your dependencies, or if you are encountering issues
        with the cache and want to rule it out as a potential cause.

    Returns
    -------
    tuple of (str, str)
        A tuple containing the path to the resulting ``app.tar.gz`` file and
        the path to the output directory that holds it.  The caller is
        responsible for cleaning up the output directory when it is no longer
        needed.
    """

    with tempfile.TemporaryDirectory(prefix="nextmv-temp-") as temp_dir:
        deps_tar: Path | None = None
        output_dir: str | None = None
        success = False
        try:
            if manifest.type == ManifestType.PYTHON:
                deps_tar = _handle_python(app_dir, manifest, model, model_configuration, verbose, rich_print, no_cache)

            found, missing, files = find_files(app_dir, manifest.files)
            manifest.confirm_mandatory_files(present_files=found)

            if len(missing) > 0:
                raise Exception(f"could not find files listed in manifest: {', '.join(missing)}")

            manifest.to_yaml(temp_dir)
            _copy_manifest_files(files, temp_dir, verbose, rich_print)

            if manifest.type == ManifestType.PYTHON:
                _cleanup_python_model(app_dir, model_configuration, verbose)

            output_dir = tempfile.mkdtemp(prefix="nextmv-build-out-")
            tar_file, _ = _compress_and_report(deps_tar, temp_dir, output_dir, verbose, rich_print)

            success = True
            return tar_file, output_dir
        finally:
            if deps_tar is not None:
                shutil.rmtree(str(deps_tar.parent), ignore_errors=True)
            if not success and output_dir is not None:
                shutil.rmtree(output_dir, ignore_errors=True)


def run_build_command(
    app_dir: str,
    manifest_build: ManifestBuild | None = None,
    verbose: bool = False,
    rich_print: bool = False,
) -> None:
    """
    Run the build command specified in the manifest.

    Parameters
    ----------
    app_dir : str
        The directory of the application, used as the working directory when
        running the build command.
    manifest_build : ManifestBuild, optional
        The build configuration from the manifest.  If ``None`` or if
        ``manifest_build.command`` is empty, this function is a no-op.
    verbose : bool, optional
        Whether to print verbose logs.
    rich_print : bool, optional
        Whether to use rich printing for verbose logs.

    Raises
    ------
    Exception
        If the build command exits with a non-zero return code.
    """

    if manifest_build is None or manifest_build.command is None or manifest_build.command == "":
        return

    elements = manifest_build.command.split(" ")
    command_str = " ".join(elements)

    if verbose:
        if rich_print:
            rich.print(f":construction: Running build command: [magenta]{command_str}[/magenta]", file=sys.stderr)
        else:
            log(f'🚧 Running build command: "{command_str}"')
    try:
        result = subprocess.run(
            elements,
            env={**os.environ, **manifest_build.environment_to_dict()},
            check=True,
            text=True,
            capture_output=True,
            cwd=app_dir,
        )

    except subprocess.CalledProcessError as e:
        raise Exception(f"error running build command: {e.stderr}") from e

    if verbose and result.stdout.strip():
        log(result.stdout.rstrip("\n"))


def run_pre_push_command(
    app_dir: str,
    pre_push_command: str | None = None,
    verbose: bool = False,
    rich_print: bool = False,
) -> None:
    """
    Run the pre-push command specified in the manifest.

    Parameters
    ----------
    app_dir : str
        The directory of the application, used as the working directory when
        running the pre-push command.
    pre_push_command : str, optional
        The shell command to execute before pushing.  If ``None`` or empty,
        this function is a no-op.
    verbose : bool, optional
        Whether to print verbose logs.
    rich_print : bool, optional
        Whether to use rich printing for verbose logs.

    Raises
    ------
    Exception
        If the pre-push command exits with a non-zero return code.
    """

    if pre_push_command is None or pre_push_command == "":
        return

    elements = _get_shell_command_elements(pre_push_command)

    command_str = " ".join(elements)
    if verbose:
        if rich_print:
            rich.print(f":hammer: Running pre-push command: [magenta]{command_str}[/magenta]", file=sys.stderr)
        else:
            log(f'🔨 Running pre-push command: "{command_str}"')
    try:
        result = subprocess.run(
            elements,
            env=os.environ,
            check=True,
            text=True,
            capture_output=True,
            cwd=app_dir,
        )

    except subprocess.CalledProcessError as e:
        raise Exception(f"error running pre-push command: {e.stderr}") from e

    if verbose and result.stdout.strip():
        log(result.stdout.rstrip("\n"))


def _copy_manifest_files(
    files: list[dict],
    temp_dir: str,
    verbose: bool = False,
    rich_print: bool = False,
) -> None:
    """
    Copy files listed in the manifest into the temp directory.

    Parameters
    ----------
    files : list of dict
        A list of file descriptors as returned by :func:`find_files`, each
        containing an ``absolute_path`` and an ``interior_path`` key.
    temp_dir : str
        The temporary directory into which files are copied, preserving the
        relative layout given by ``interior_path``.
    verbose : bool, optional
        Whether to print verbose logs.
    rich_print : bool, optional
        Whether to use rich printing for verbose logs.

    Raises
    ------
    Exception
        If a destination directory cannot be created or a file cannot be
        copied.
    """

    if verbose:
        if rich_print:
            rich.print(
                f":clipboard: Copying files listed in [magenta]{MANIFEST_FILE_NAME}[/magenta] manifest.",
                file=sys.stderr,
            )
        else:
            log(f'📋 Copying files listed in "{MANIFEST_FILE_NAME}" manifest.')

    for file in files:
        target_dir = os.path.dirname(os.path.join(temp_dir, file["interior_path"]))
        try:
            os.makedirs(target_dir, exist_ok=True)
        except OSError as e:
            raise Exception(f"error creating directory for asset file {file['interior_path']}: {e}") from e

        try:
            shutil.copy2(file["absolute_path"], os.path.join(temp_dir, target_dir))
        except OSError as e:
            raise Exception(f"error copying asset files {file['absolute_path']}: {e}") from e


def _compress_and_report(
    deps_tar: Path | None,
    temp_dir: str,
    output_dir: str,
    verbose: bool = False,
    rich_print: bool = False,
) -> tuple[str, int]:
    """
    Compress the app into a tarball and log the result.

    Parameters
    ----------
    deps_tar : Path or None
        Path to a pre-built ``deps.tar.gz`` containing installed Python
        dependencies, or ``None`` when no dependencies need to be bundled.
    temp_dir : str
        Directory containing the app files that have been staged for packaging.
    output_dir : str
        Directory where the resulting ``app.tar.gz`` will be written.
    verbose : bool, optional
        Whether to print verbose logs.
    rich_print : bool, optional
        Whether to use rich printing for verbose logs.

    Returns
    -------
    tuple of (str, int)
        A tuple containing the path to the resulting ``app.tar.gz`` file and
        the number of application files included in the archive.
    """

    if verbose:
        if rich_print:
            rich.print(":floppy_disk: Compressing application into tarball.", file=sys.stderr)
        else:
            log("💾 Compressing application into tarball.")

    if deps_tar is not None:
        tar_file, file_count = _build_from_deps_tar(deps_tar, temp_dir, output_dir, verbose, rich_print)
    else:
        tar_file, file_count = _compress_tar(temp_dir, output_dir, verbose, rich_print)

    if verbose:
        app_file_count_label = "app file" if file_count == 1 else "app files"
        size_label = "with dependencies" if deps_tar is not None else "total"
        try:
            size = _human_friendly_file_size(tar_file)
            if rich_print:
                rich.print(
                    f":package: Packaged application ([magenta]{file_count}[/magenta] {app_file_count_label}, "
                    f"[magenta]{size}[/magenta] {size_label}).",
                    file=sys.stderr,
                )
            else:
                log(f"📦 Packaged application ({file_count} {app_file_count_label}, {size} {size_label}).")
        except Exception:
            if rich_print:
                rich.print(
                    f":package: Packaged application ([magenta]{file_count}[/magenta] {app_file_count_label}).",
                    file=sys.stderr,
                )
            else:
                log(f"📦 Packaged application ({file_count} {app_file_count_label}).")

    return tar_file, file_count


def _get_shell_command_elements(pre_push_command):
    """
    Get the shell command elements based on the operating system.

    Wraps *pre_push_command* in the appropriate shell invocation for the
    current platform so that shell features (pipes, redirects, etc.) work
    correctly.

    Parameters
    ----------
    pre_push_command : str
        The raw shell command string to execute.

    Returns
    -------
    list of str
        A list of arguments suitable for passing directly to
        :func:`subprocess.run`, e.g. ``["bash", "-c", command]``.
    """
    # Check if we're in a Unix-like shell (including MINGW on Windows)
    bash = shutil.which("bash")
    if "SHELL" in os.environ and bash:
        return [bash, "-c", pre_push_command]
    # Default to cmd on Windows
    elif platform.system() == "Windows":
        return ["cmd", "/c", pre_push_command]
    # Default to sh on Unix-like systems (Linux, macOS)
    else:
        return ["sh", "-c", pre_push_command]


def _handle_python(
    app_dir: str,
    manifest: Manifest,
    model: Model | None = None,
    model_configuration: ModelConfiguration | None = None,
    verbose: bool = False,
    rich_print: bool = False,
    no_cache: bool = False,
) -> Path | None:
    """
    Handles the Python-specific packaging logic.

    This includes encoding the Python model (if provided) and bundling Python
    dependencies using `uv pip`.  The dependencies are resolved, installed, and
    cached on a per-package basis to maximize cache hits and efficiency.  The
    final output is a `deps.tar.gz` file containing the installed dependencies,
    which is returned for inclusion in the final app tarball.

    Parameters
    ----------
    app_dir : str
        The directory of the application.
    manifest : Manifest
        The app manifest containing dependency information.
    model : Model, optional
        The Python model to encode and include in the package.
    model_configuration : ModelConfiguration, optional
        The configuration for encoding the Python model.
    verbose : bool, optional
        Whether to print verbose logs.
    rich_print : bool, optional
        Whether to use rich printing for verbose logs.
    no_cache : bool, default=False
        Do not use or populate the dependency cache when resolving and
        installing Python dependencies. This forces a fresh build of all
        dependencies, which can be useful to ensure that the most up-to-date
        versions of dependencies are included or to rule out cache-related
        issues.

    Returns
    -------
    Path or None
        The path to the `deps.tar.gz` file containing the installed dependencies,
        or `None` if no dependencies are specified.
    """

    if model is not None and model_configuration is not None:
        if verbose:
            if rich_print:
                rich.print(":crystal_ball: Encoding Python model.", file=sys.stderr)
            else:
                log("🔮 Encoding Python model.")

        model.save(app_dir, model_configuration)

    if verbose:
        if rich_print:
            suffix = " - caching [italic]disabled[/italic]" if no_cache else ""
            rich.print(f":snake: Bundling Python dependencies{suffix}.", file=sys.stderr)
        else:
            suffix = " - caching disabled" if no_cache else ""
            log(f"🐍 Bundling Python dependencies{suffix}.")

    deps_tar = _install_dependencies(manifest, app_dir, verbose, rich_print, no_cache)

    return deps_tar


def _install_dependencies(
    manifest: Manifest,
    app_dir: str,
    verbose: bool = False,
    rich_print: bool = False,
    no_cache: bool = False,
) -> Path | None:
    """
    Install dependencies for the Python app.

    Parameters
    ----------
    manifest : Manifest
        The app manifest containing dependency information.
    app_dir : str
        The directory of the application.
    verbose : bool, optional
        Whether to print verbose logs.
    rich_print : bool, optional
        Whether to use rich printing for verbose logs.
    no_cache : bool, default=False
        Do not use or populate the dependency cache when resolving and
        installing Python dependencies. This forces a fresh build of all
        dependencies, which can be useful to ensure that the most up-to-date
        versions of dependencies are included or to rule out cache-related
        issues.

    Returns
    -------
    Path or None
        Path to the `deps.tar.gz` file containing the installed dependencies,
        or `None` if no dependencies are specified.
    """

    if manifest.python is None:
        return None

    pip_requirements = manifest.python.pip_requirements

    # If no pip requirements are specified, we do not install any dependencies.
    if pip_requirements is None or pip_requirements == "":
        return None

    pip_requirements, is_temp_file = _resolve_pip_requirements_file(pip_requirements, app_dir)
    try:
        python_version = "3.11"
        if manifest.python.version:
            _confirm_python_bundling_version(manifest.python.version)
            python_version = manifest.python.version

        if not manifest.python.arch or manifest.python.arch == "arm64":
            uv_platform = "aarch64-manylinux_2_34"
        elif manifest.python.arch == "amd64":
            uv_platform = "x86_64-manylinux_2_34"
        else:
            raise Exception(f"unknown architecture '{manifest.python.arch}' specified in manifest")

        uv_bin = _find_uv_binary()
        deps_tar = _resolve_and_install_deps(
            uv_bin,
            pip_requirements,
            python_version,
            uv_platform,
            app_dir,
            verbose,
            rich_print,
            no_cache,
        )

        return deps_tar
    finally:
        if is_temp_file:
            try:
                os.unlink(pip_requirements)
            except OSError:
                pass


def _resolve_pip_requirements_file(pip_requirements: list[str] | str, app_dir: str) -> tuple[str, bool]:
    """
    Resolve pip_requirements to a path to a requirements .txt file.

    - A list of requirement strings is written to a temporary file.
    - A string path to a pyproject.toml is converted by extracting
      [project.dependencies] into a temporary file.
    - Any other string path is resolved to an absolute path.

    Parameters
    ----------
    pip_requirements : list[str] or str
        Either a list of pip requirement strings or a string path to a requirements file.
    app_dir : str
        The directory of the application.

    Returns
    -------
    tuple[str, bool]
        A tuple containing the path to the requirements file and a boolean indicating
        whether the file is temporary and should be deleted by the caller.
    """

    if isinstance(pip_requirements, list):
        # If pip_requirements is a list, we write it to a temporary file so that we can
        # pass it to pip.
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", prefix="nextmv-reqs-", delete=False) as f:
            for requirement in pip_requirements:
                f.write(requirement + "\n")

            return f.name, True

    # pip_requirements is a string path.
    pip_requirements = pip_requirements.strip()
    if not os.path.isfile(os.path.join(app_dir, pip_requirements)):
        raise FileNotFoundError(f"pip requirements file '{pip_requirements}' not found in '{app_dir}'")

    if os.path.basename(pip_requirements) == "pyproject.toml":
        # If the requirements file is a pyproject.toml, read
        # [project].dependencies and write them to a temporary requirements.txt
        # file for pip.
        deps = read_pyproject_dependencies(os.path.join(app_dir, pip_requirements))
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", prefix="nextmv-reqs-", delete=False) as f:
            for dep in deps:
                f.write(dep + "\n")

            return f.name, True

    # Otherwise, we assume it's a path to a requirements.txt file and return
    # the absolute path.
    return os.path.abspath(os.path.join(app_dir, pip_requirements)), False


def _resolve_and_install_deps(
    uv_bin: str,
    pip_requirements: str,
    python_version: str,
    uv_platform: str,
    app_dir: str,
    verbose: bool = False,
    rich_print: bool = False,
    no_cache: bool = False,
) -> Path | None:
    """
    Compile the lockfile, fetch missing packages, and assemble deps.tar.gz.

    For each package in the lockfile:
    - If a cached per-package `installed.tar.gz` exists, use it directly.
    - Otherwise download the wheel, install it, compress it, and store it in
      the cache for future runs.

    The final `deps.tar.gz` is assembled by concatenating the per-package
    gzip streams (valid per RFC 1952 — no decompression or recompression
    needed).

    Parameters
    ----------
    uv_bin : str
        Path to the `uv` binary.
    pip_requirements : str
        Path to the pip requirements file.
    python_version : str
        The Python version to target, e.g. "3.11".
    uv_platform : str
        The `uv` platform string to target, e.g. "x86_64-manylinux_2_34".
    app_dir : str
        The application directory to use as the working directory for `uv pip`
        commands.
    verbose : bool, optional
        Whether to print verbose logs.
    rich_print : bool, optional
        Whether to use rich printing for verbose logs.
    no_cache : bool, default=False
        Do not use or populate the dependency cache when resolving and
        installing Python dependencies. This forces a fresh build of all
        dependencies, which can be useful to ensure that the most up-to-date
        versions of dependencies are included or to rule out cache-related
        issues.

    Returns
    -------
    Path or None
        The path to the assembled `deps.tar.gz` file containing the installed
        dependencies, or `None` if no dependencies are specified.
    """

    lockfile_content = _compile_lockfile(uv_bin, pip_requirements, python_version, uv_platform, app_dir)
    packages = _parse_lockfile(lockfile_content)

    with tempfile.TemporaryDirectory(prefix="nextmv-pkg-tars-") as tars_tmp:
        if no_cache:
            cached_tars: list[Path] = []
            missing_packages = packages
        else:
            cached_tars, missing_packages = _collect_cached_package_tars(packages, python_version, uv_platform)

        _log_pkg_cache_status(verbose, rich_print, len(cached_tars), len(packages), len(missing_packages))

        new_pkg_tars: list[dict[str, Path]] = []
        if missing_packages:
            new_pkg_tars = _fetch_missing_package_tars(
                uv_bin=uv_bin,
                missing_packages=missing_packages,
                python_version=python_version,
                uv_platform=uv_platform,
                app_dir=app_dir,
                out_dir=tars_tmp,
            )
            if not no_cache:
                _store_new_package_tars(pkg_tars=new_pkg_tars, python_version=python_version, uv_platform=uv_platform)

        all_tars = cached_tars + [pkg["tar_path"] for pkg in new_pkg_tars]
        _, deps_tar = _concat_package_tars(tars=all_tars, out_dir=tars_tmp)

        # Move the assembled tar out of the temp dir before it is cleaned up.
        deps_out_dir = tempfile.mkdtemp(prefix="nextmv-deps-out-")
        try:
            final_tar = Path(deps_out_dir) / "deps.tar.gz"
            shutil.move(str(deps_tar), str(final_tar))
        except Exception:
            shutil.rmtree(deps_out_dir, ignore_errors=True)
            raise

    return final_tar


def _collect_cached_package_tars(
    packages: list[dict[str, str]],
    python_version: str,
    uv_platform: str,
) -> tuple[list[Path], list[dict[str, str]]]:
    """
    Check the cache for each package and collect paths to cached tars,
    returning any missing packages.

    Parameters
    ----------
    packages : list of dict
        A list of dictionaries, each containing the `name` and `version` of a
        package in the lockfile.
    python_version : str
        The Python version to target, e.g. "3.11".
    uv_platform : str
        The `uv` platform string to target, e.g. "x86_64-manylinux_2_34".

    Returns
    -------
    tuple of (list of Path, list of dict)
        A tuple containing two lists:
        - The first list contains the paths to the cached tar files for each package.
        - The second list contains dictionaries for the packages that are
        missing from the cache, each containing the `name` and `version`.
    """

    cached_tars: list[Path] = []
    missing_packages: list[dict[str, str]] = []

    for package in packages:
        name, version = package["name"], package["version"]
        pkg_key = dep_cache_key(name, version, python_version, uv_platform)
        cached_tar = get_cached_dep(pkg_key)
        if cached_tar is not None:
            cached_tars.append(cached_tar)
        else:
            missing_packages.append({"name": name, "version": version})

    return cached_tars, missing_packages


def _fetch_missing_package_tars(
    uv_bin: str,
    missing_packages: list[dict[str, str]],
    python_version: str,
    uv_platform: str,
    app_dir: str,
    out_dir: str,
) -> list[dict[str, Path]]:
    """
    Download, install, and compress each missing package into *out_dir*.

    Downloading is done in a single batch call for efficiency.  Installation
    and compression are then done per-package so each gets its own
    `installed.tar.gz` suitable for caching and gzip concatenation.

    Parameters
    ----------
    uv_bin : str
        Path to the `uv` binary.
    missing_packages : list of dict
        A list of dictionaries for the packages that are missing from the cache,
        each containing the `name` and `version`.
    python_version : str
        The Python version to target, e.g. "3.11".
    uv_platform : str
        The `uv` platform string to target, e.g. "x86_64-manylinux_2_34".
    app_dir : str
        The application directory to use as the working directory for `uv pip`
        commands.
    out_dir : str
        The directory to write the per-package `installed.tar.gz` files to.
        This should be a temporary directory that is cleaned up by the caller.

    Returns
    -------
    list of dict
        A list of dictionaries, each containing the `pkg_key` and `tar_path` for
        a missing package that was fetched, installed, and compressed.
    """

    results: list[dict[str, Path]] = []
    for package in missing_packages:
        name, version = package["name"], package["version"]
        pkg_key = dep_cache_key(name, version, python_version, uv_platform)
        tar_path = _install_and_compress_package(
            uv_bin=uv_bin,
            name=name,
            version=version,
            python_version=python_version,
            uv_platform=uv_platform,
            app_dir=app_dir,
            out_dir=out_dir,
        )
        results.append(
            {
                "pkg_key": pkg_key,
                "tar_path": tar_path,
                "name": name,
                "version": version,
            }
        )

    return results


def _install_and_compress_package(
    uv_bin: str,
    name: str,
    version: str,
    python_version: str,
    uv_platform: str,
    app_dir: str,
    out_dir: str,
) -> Path:
    """Install a single package from the package index and compress its installed tree.

    Uses `--no-deps` because the lockfile already encodes the complete
    dependency graph — each package is handled independently.

    Parameters
    ----------
    uv_bin : str
        Path to the `uv` binary.
    name : str
        The package name as it appears in the lockfile or wheel filename.
    version : str
        The pinned version string (e.g. `"2.23.4"`).
    python_version : str
        The target Python version string (e.g. `"3.11"`).
    uv_platform : str
        The target platform string (e.g. `"aarch64-manylinux_2_34"`).
    app_dir : str
        The application directory to use as the working directory for `uv pip`
        commands.
    out_dir : str
        The directory to write the per-package `installed.tar.gz` files to.
        This should be a temporary directory that is cleaned up by the caller.

    Returns
    -------
    Path
        The path to the `installed.tar.gz` file for the installed package.
    """

    with tempfile.TemporaryDirectory(prefix="nextmv-pkg-install-") as install_tmp:
        install_dir = os.path.join(install_tmp, "pkg")
        os.makedirs(install_dir)

        result = subprocess.run(
            [
                uv_bin,
                "pip",
                "install",
                f"{name}=={version}",
                "--no-deps",
                "--only-binary=:all:",
                "--target",
                install_dir,
                "--quiet",
                f"--python-platform={uv_platform}",
                f"--python-version={python_version}",
            ],
            cwd=app_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if result.returncode != 0:
            raise Exception(f"error installing {name}=={version}: {os.linesep}{result.stdout}")

        safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", f"{name}-{version}")
        tar_path = Path(out_dir) / f"{safe_name}.tar.gz"
        dep_arcname = os.path.join(".nextmv", "python", "deps")

        # Write tar entries to a temp .tar file, capture the byte offset
        # where tarfile will write the EOF marker, then gzip-compress only
        # the entries (no EOF block).  Omitting the EOF block lets these
        # per-package gzip streams be raw-concatenated without causing tar
        # to stop at the first end-of-archive marker.
        tmp_tar_path = os.path.join(install_tmp, "pkg.tar")

        with tarfile.open(tmp_tar_path, mode="w") as tar_obj:
            tar_obj.add(install_dir, arcname=dep_arcname)
            # Byte offset where EOF marker begins; captured before close()
            # appends EOF blocks.
            entry_end = tar_obj.offset

        with open(tmp_tar_path, "rb") as raw_f:
            with gzip.open(str(tar_path), "wb") as gz:
                remaining = entry_end
                while remaining > 0:
                    chunk = raw_f.read(min(_IO_CHUNK_SIZE, remaining))
                    if not chunk:
                        break

                    gz.write(chunk)
                    remaining -= len(chunk)

    return tar_path


def _store_new_package_tars(
    pkg_tars: list[dict[str, Path]],
    python_version: str,
    uv_platform: str,
) -> None:
    """
    Store newly built per-package tarballs into the cache.

    Parameters
    ----------
    pkg_tars : list of dict
        A list of dictionaries, each containing the `pkg_key` and `tar_path` for
        a missing package that was fetched, installed, and compressed.
    python_version : str
        The Python version to target, e.g. "3.11".
    uv_platform : str
        The `uv` platform string to target, e.g. "x86_64-linux-gnu".
    """

    for pkg in pkg_tars:
        pkg_key, tar_path = pkg["pkg_key"], pkg["tar_path"]
        name, version = pkg["name"], pkg["version"]
        if get_cached_dep(pkg_key) is None:
            store_dep(
                pkg_key=pkg_key,
                tar_path=tar_path,
                name=name,
                version=version,
                python_version=python_version,
                platform=uv_platform,
            )


def _concat_package_tars(tars: list[Path], out_dir: str) -> tuple[int, Path]:
    """
    Concatenate per-package gzip streams into a single `deps.tar.gz`.

    The gzip format (RFC 1952) explicitly supports concatenated member streams,
    and tar decompressors handle them correctly.  This means no decompression
    or recompression is needed — assembly is pure sequential I/O.

    Parameters
    ----------
    tars : list of Path
        A list of paths to the per-package `installed.tar.gz` files to
        concatenate.
    out_dir : str
        The directory to write the concatenated `deps.tar.gz` file to.  This
        should be a temporary directory that is cleaned up by the caller.

    Returns
    -------
    tuple of (int, Path)
        A tuple containing the total number of files across all packages and the
        path to the assembled `deps.tar.gz` file.
    """

    out_path = Path(out_dir) / "deps.tar.gz"

    # Each per-package .tar.gz is a gzip stream of tar entries with no
    # end-of-archive block.  Concatenate raw bytes — zero decompression needed.
    # The tar EOF block is written later by _build_from_deps_tar as part of
    # the final app.tar.gz gzip member.
    with open(str(out_path), "wb") as out_f:
        for tar_path in tars:
            with open(str(tar_path), "rb") as in_f:
                shutil.copyfileobj(in_f, out_f)

    return 0, out_path


def _log_pkg_cache_status(
    verbose: bool,
    rich_print: bool,
    cached_count: int,
    total: int,
    missing_count: int,
) -> None:
    """
    Emit a verbose message about the per-package tarball cache hit/miss ratio.

    Parameters
    ----------
    verbose : bool
        Whether to print verbose logs.
    rich_print : bool
        Whether to use rich printing for verbose logs.
    cached_count : int
        The number of packages found in the cache.
    total : int
        The total number of packages in the lockfile.
    missing_count : int
        The number of packages missing from the cache (i.e. `total -
        cached_count`).
    """

    if not verbose:
        return

    if cached_count > 0:
        total_word = "dependency" if total == 1 else "dependencies"
        if rich_print:
            rich.print(
                f"    :fast_up_button: [magenta]{cached_count}/{total}[/magenta] compressed {total_word} "
                "found in cache.",
                file=sys.stderr,
            )
        else:
            log(f"    ⏫ {cached_count}/{total} compressed {total_word} found in cache.")

    if missing_count > 0:
        missing_word = "dependency" if missing_count == 1 else "dependencies"
        if rich_print:
            rich.print(
                f"    :rabbit2: Downloading and compressing [magenta]{missing_count}[/magenta] {missing_word} "
                "from package index.",
                file=sys.stderr,
            )
        else:
            log(f"    🐇 Downloading and compressing {missing_count} {missing_word} from package index.")


def _parse_lockfile(lockfile_content: str) -> list[dict[str, str]]:
    """
    Parse a `uv pip compile` lockfile and return `(name, version)` pairs.

    Only top-level package lines are matched — lines that start with a package
    name followed by `==`.  Comment lines (`#`) and indented annotation
    lines (`    # via ...`) are skipped.

    The returned `(name, version)` pairs are used to check the cache and fetch
    missing packages.

    Parameters
    ----------
    lockfile_content : str
        The content of the lockfile produced by `uv pip compile`.

    Returns
    -------
    list of dict
        A list of dictionaries, each containing the `name` and `version` of a
        top-level package in the lockfile.
    """

    _re_pkg = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==([^\s;#\[]+)")
    packages = []
    for line in lockfile_content.splitlines():
        if not line or line[0] in (" ", "\t", "#"):
            continue

        m = _re_pkg.match(line)
        if m:
            packages.append({"name": m.group(1), "version": m.group(2)})

    return packages


def _compile_lockfile(
    uv_bin: str,
    pip_requirements: str,
    python_version: str,
    uv_platform: str,
    app_dir: str,
) -> str:
    """
    Resolve requirements to a fully-pinned lockfile via `uv pip compile`.

    Pinning makes the cache key deterministic: the same requirements always
    produce the same key regardless of when the build runs.

    Parameters
    ----------
    uv_bin : str
        Path to the `uv` binary.
    pip_requirements : str
        Path to the pip requirements file.
    python_version : str
        The Python version to target, e.g. "3.11".
    uv_platform : str
        The `uv` platform string to target, e.g. "x86_64-manylinux_2_34".
    app_dir : str
        The application directory to use as the working directory for `uv pip`
        commands.

    Returns
    -------
    str
        The content of the compiled lockfile, which is a fully-pinned list of
        packages and versions.
    """

    result = subprocess.run(
        [
            uv_bin,
            "pip",
            "compile",
            pip_requirements,
            "--quiet",
            f"--python-platform={uv_platform}",
            f"--python-version={python_version}",
        ],
        cwd=app_dir,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise Exception(f"error resolving dependencies: {os.linesep}{result.stderr}")

    return result.stdout


def _confirm_python_bundling_version(version: str) -> None:
    """
    Validate that *version* is suitable for dependency bundling.

    Raises an exception if the version is not in ``major.minor`` form or is
    below Python 3.10, which is the minimum required for bundling.

    Parameters
    ----------
    version : str
        The Python version string to validate, e.g. ``"3.11"``.

    Raises
    ------
    Exception
        If the version is not in ``major.minor`` form or is below 3.10.
    """

    # Only accept versions in the form "major.minor" where both are integers
    re_version = re.compile(r"^(\d+)\.(\d+)$")
    match = re_version.fullmatch(version)
    if match:
        major, minor = int(match.group(1)), int(match.group(2))
        if major == 3 and minor >= 10:
            return

    raise Exception(f"python version 3.10 or higher is required for bundling, got {version}")


def _build_from_deps_tar(
    deps_tar: Path,
    files_dir: str,
    output_dir: str,
    verbose: bool = False,
    rich_print: bool = False,
) -> tuple[str, int]:
    """
    Build the final tarball by concatenating the cached deps.tar.gz with a
    freshly-compressed tarball of the app files.

    The gzip format (RFC 1952) explicitly supports concatenated streams, and
    tar decompressors handle them correctly.  This avoids decompressing and
    recompressing the (large) deps archive — only the small set of app files
    needs to be compressed from scratch.

    Parameters
    ----------
    deps_tar : Path
        The path to the `deps.tar.gz` file containing the installed dependencies.
    files_dir : str
        The directory containing the app files to be included in the final tarball.
    output_dir : str
        The directory to write the final `app.tar.gz` file to.  This should be
        a temporary directory that is cleaned up by the caller.
    verbose : bool, optional
        Whether to print verbose logs.
    rich_print : bool, optional
        Whether to use rich printing for verbose logs.
    """

    if verbose:
        if rich_print:
            rich.print("    :hammer_and_wrench:  Appending application files.", file=sys.stderr)
        else:
            log("    🛠️  Appending application files.")

    output_file = os.path.join(output_dir, "app.tar.gz")
    num_files = 0

    # Raw-copy all per-package gzip streams (no decompression).
    with open(output_file, "wb") as out_f:
        with open(str(deps_tar), "rb") as df:
            shutil.copyfileobj(df, out_f)

    # Append app files + tar EOF as the final gzip member.  gzip.open in
    # append-binary mode starts a new gzip member in the same file, so the
    # complete app.tar.gz is a valid multi-member gzip that any modern tar
    # decompressor handles correctly.
    with gzip.open(output_file, "ab") as gz_out:
        with tarfile.open(fileobj=gz_out, mode="w|") as app_tar:
            for root, _, files in os.walk(files_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=files_dir)
                    app_tar.add(file_path, arcname=arcname)
                    num_files += 1

    return output_file, num_files


def _compress_tar(source: str, target: str, verbose: bool = False, rich_print: bool = False) -> tuple[str, int]:
    """
    Compress the source directory into a tar.gz file in the target.

    This is used when there are no dependencies to bundle and we can simply
    compress the app files directly without needing to concatenate with a deps
    tarball.

    Parameters
    ----------
    source : str
        The directory containing the files to be compressed into the tarball.
    target : str
        The directory where the resulting tar.gz file should be saved.
    verbose : bool, optional
        Whether to print verbose logs.
    rich_print : bool, optional
        Whether to use rich printing for verbose logs.

    Returns
    -------
    tuple of (str, int)
        A tuple containing the path to the resulting tar.gz file and the number
        of files included in the tarball.
    """

    if verbose:
        if rich_print:
            rich.print("    :hammer_and_wrench:  Compressing tarball from scratch.", file=sys.stderr)
        else:
            log("    🛠️  Compressing tarball from scratch.")

    return_file_name = "app.tar.gz"
    target = os.path.join(target, return_file_name)
    num_files = 0

    with tarfile.open(target, "w:gz") as tar:
        for root, _, files in os.walk(source):
            for file in files:
                if file == return_file_name:
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=source)
                tar.add(file_path, arcname=arcname)
                num_files += 1

    return target, num_files


def _human_friendly_file_size(path: str) -> str:
    """
    Return a human-friendly string representation of the file size.

    Parameters
    ----------
    path : str
        The path to the file whose size is to be determined.

    Returns
    -------
    str
        A human-friendly string representation of the file size, using
        appropriate units (B, KiB, MiB, GiB) and rounded to two decimal places
        for larger units.
    """

    try:
        size = os.path.getsize(path)
    except OSError as e:
        raise Exception(f"error getting file size: {e}") from e

    pretty_size = format_bytes(size)
    return pretty_size
