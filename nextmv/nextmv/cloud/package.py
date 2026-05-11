"""Module with the logic for pushing an app to Nextmv Cloud."""

import json
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

from nextmv.cache import cache_key, get_cached_deps, store_deps
from nextmv.logger import log
from nextmv.manifest import (
    MANIFEST_FILE_NAME,
    Manifest,
    ManifestBuild,
    ManifestType,
    ModelConfiguration,
    find_files,
    read_pyproject_dependencies,
)
from nextmv.model import Model, _cleanup_python_model
from nextmv.uv_handler import _find_uv_binary

_MANDATORY_FILES_PER_TYPE = {
    ManifestType.PYTHON: ["main.py"],
    ManifestType.GO: ["main"],
    ManifestType.BINARY: ["main"],
    ManifestType.JAVA: ["main.jar"],
}


def _package(  # noqa: C901 # complexity attributed to printing.
    app_dir: str,
    manifest: Manifest,
    model: Model | None = None,
    model_configuration: ModelConfiguration | None = None,
    verbose: bool = False,
    rich_print: bool = False,
) -> tuple[str, str]:
    """Package the app into a tarball."""

    with tempfile.TemporaryDirectory(prefix="nextmv-temp-") as temp_dir:
        deps_tar: Path | None = None
        if manifest.type == ManifestType.PYTHON:
            deps_tar = __handle_python(app_dir, manifest, model, model_configuration, verbose, rich_print)

        found, missing, files = find_files(app_dir, manifest.files)
        manifest.confirm_mandatory_files(found)

        if len(missing) > 0:
            raise Exception(f"could not find files listed in manifest: {', '.join(missing)}")

        manifest.to_yaml(temp_dir)

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
            except subprocess.CalledProcessError as e:
                raise Exception(f"error copying asset files {file['absolute_path']}: {e}") from e

        if manifest.type == ManifestType.PYTHON:
            _cleanup_python_model(app_dir, model_configuration, verbose)

        if verbose:
            if rich_print:
                rich.print(":floppy_disk: Compressing application into tarball.", file=sys.stderr)
            else:
                log("💾 Compressing application into tarball.")

        output_dir = tempfile.mkdtemp(prefix="nextmv-build-out-")
        if deps_tar is not None:
            tar_file, file_count = __build_from_deps_tar(deps_tar, temp_dir, output_dir, verbose, rich_print)
        else:
            tar_file, file_count = __compress_tar(temp_dir, output_dir, verbose, rich_print)

        file_count_msg = f"{file_count} file" if file_count == 1 else f"{file_count} files"

        if verbose:
            try:
                size = __human_friendly_file_size(tar_file)
                if rich_print:
                    rich.print(
                        ":package: Packaged application "
                        f"([magenta]{file_count_msg}[/magenta], [magenta]{size}[/magenta]).",
                        file=sys.stderr,
                    )
                else:
                    log(f"📦 Packaged application ({file_count_msg}, {size}).")
            except Exception:
                if rich_print:
                    rich.print(
                        f":package: Packaged application ([magenta]{file_count_msg}[/magenta]).",
                        file=sys.stderr,
                    )
                else:
                    log(f"📦 Packaged application ({file_count_msg}).")

        return tar_file, output_dir


def _run_build_command(
    app_dir: str,
    manifest_build: ManifestBuild | None = None,
    verbose: bool = False,
    rich_print: bool = False,
) -> None:
    """Run the build command specified in the manifest."""

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


def _get_shell_command_elements(pre_push_command):
    """Get the shell command elements based on the operating system."""
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


def _run_pre_push_command(
    app_dir: str,
    pre_push_command: str | None = None,
    verbose: bool = False,
    rich_print: bool = False,
) -> None:
    """Run the pre-push command specified in the manifest."""

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


def __handle_python(
    app_dir: str,
    manifest: Manifest,
    model: Model | None = None,
    model_configuration: ModelConfiguration | None = None,
    verbose: bool = False,
    rich_print: bool = False,
) -> Path | None:
    """Handles the Python-specific packaging logic."""

    if model is not None and model_configuration is not None:
        if verbose:
            if rich_print:
                rich.print(":crystal_ball: Encoding Python model.", file=sys.stderr)
            else:
                log("🔮 Encoding Python model.")

        model.save(app_dir, model_configuration)

    if verbose:
        if rich_print:
            rich.print(":snake: Bundling Python dependencies.", file=sys.stderr)
        else:
            log("🐍 Bundling Python dependencies.")

    return __install_dependencies(manifest, app_dir, verbose, rich_print)


def __install_dependencies(  # noqa: C901 # complexity
    manifest: Manifest,
    app_dir: str,
    verbose: bool = False,
    rich_print: bool = False,
) -> Path | None:
    """Install dependencies for the Python app."""

    if manifest.python is None:
        return None

    pip_requirements = manifest.python.pip_requirements

    if pip_requirements is None or pip_requirements == "":
        # If no pip requirements are specified, we do not install any dependencies.
        return None

    if isinstance(pip_requirements, list):
        # If pip_requirements is a list, we write it to a temporary file so that we can
        # pass it to pip.
        pip_requirements_file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            prefix="nextmv-reqs-",
            delete=False,
        )
        try:
            for requirement in pip_requirements:
                pip_requirements_file.write(requirement + "\n")

            pip_requirements_file.flush()
            pip_requirements = pip_requirements_file.name

        finally:
            pip_requirements_file.close()
    elif isinstance(pip_requirements, str):
        # If pip_requirements is a string, we expect it to be a file path to a
        # requirements file.
        pip_requirements = pip_requirements.strip()
        if not os.path.isfile(os.path.join(app_dir, pip_requirements)):
            raise FileNotFoundError(f"pip requirements file '{pip_requirements}' not found in '{app_dir}'")

        if pip_requirements.endswith(".toml"):
            # If the requirements file is a pyproject.toml, read [project.dependencies]
            # and write them to a temporary requirements.txt file for pip.
            deps = read_pyproject_dependencies(os.path.join(app_dir, pip_requirements))
            pip_requirements_file = tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", prefix="nextmv-reqs-", delete=False
            )
            try:
                for dep in deps:
                    pip_requirements_file.write(dep + "\n")

                pip_requirements_file.flush()
                pip_requirements = pip_requirements_file.name
            finally:
                pip_requirements_file.close()
        else:
            pip_requirements = os.path.abspath(os.path.join(app_dir, pip_requirements))

    python_version = "3.11"
    if manifest.python.version:
        __confirm_python_bundling_version(manifest.python.version)
        python_version = manifest.python.version

    if not manifest.python.arch or manifest.python.arch == "arm64":
        uv_platform = "aarch64-unknown-linux-gnu"
    elif manifest.python.arch == "amd64":
        uv_platform = "x86_64-unknown-linux-gnu"
    else:
        raise Exception(f"unknown architecture '{manifest.python.arch}' specified in manifest")

    uv_bin = _find_uv_binary()
    return __resolve_and_install_deps(
        uv_bin,
        pip_requirements,
        python_version,
        uv_platform,
        app_dir,
        verbose,
        rich_print,
    )


def __resolve_and_install_deps(
    uv_bin: str,
    pip_requirements: str,
    python_version: str,
    uv_platform: str,
    app_dir: str,
    verbose: bool = False,
    rich_print: bool = False,
) -> Path | None:
    """Orchestrate the compile -> cache-check -> install -> cache-store flow."""
    lockfile_content = __compile_lockfile(uv_bin, pip_requirements, python_version, uv_platform, app_dir)
    key = cache_key(lockfile_content, python_version, uv_platform)

    cached_tar = get_cached_deps(key)
    if cached_tar is not None:
        if verbose:
            if rich_print:
                rich.print("\t:fast_up_button: Loading compressed Python dependencies from cache.", file=sys.stderr)
            else:
                log("   ⏫ Loading compressed Python dependencies from cache.")

        return cached_tar

    if verbose:
        if rich_print:
            rich.print(
                "\t:rabbit2: Downloading and compressing Python dependencies from package index.", file=sys.stderr
            )
        else:
            log("   🐇 Downloading and compressing Python dependencies from package index.")

    with tempfile.TemporaryDirectory(prefix="nextmv-deps-install-") as install_tmp:
        install_dir = os.path.join(install_tmp, "deps")
        os.makedirs(install_dir)
        __run_install(uv_bin, lockfile_content, python_version, uv_platform, app_dir, install_tmp, install_dir)
        store_deps(
            key=key,
            installed_deps_dir=install_dir,
            python_version=python_version,
            platform=uv_platform,
            lockfile_content=lockfile_content,
        )

    return get_cached_deps(key)


def __compile_lockfile(
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


def __run_install(
    uv_bin: str,
    lockfile_content: str,
    python_version: str,
    uv_platform: str,
    app_dir: str,
    temp_dir: str,
    target_dir: str,
) -> None:
    """Install packages from a pinned lockfile via `uv pip install`."""
    lockfile_file = os.path.join(temp_dir, "requirements.lock")
    with open(lockfile_file, "w") as f:
        f.write(lockfile_content)

    result = subprocess.run(
        [
            uv_bin,
            "pip",
            "install",
            "-r",
            lockfile_file,
            "--only-binary=:all:",
            "--target",
            target_dir,
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
        raise Exception(f"error installing dependencies: {os.linesep}{result.stdout}")


def __confirm_python_bundling_version(version: str) -> None:
    # Only accept versions in the form "major.minor" where both are integers
    re_version = re.compile(r"^(\d+)\.(\d+)$")
    match = re_version.fullmatch(version)
    if match:
        major, minor = int(match.group(1)), int(match.group(2))
        if major == 3 and minor >= 10:
            return
    raise Exception(f"python version 3.10 or higher is required for bundling, got {version}")


def __build_from_deps_tar(
    deps_tar: Path,
    files_dir: str,
    output_dir: str,
    verbose: bool = False,
    rich_print: bool = False,
) -> tuple[str, int]:
    """Build the final tarball by concatenating the cached deps.tar.gz with a
    freshly-compressed tarball of the app files.

    The gzip format (RFC 1952) explicitly supports concatenated streams, and
    tar decompressors handle them correctly.  This avoids decompressing and
    recompressing the (large) deps archive — only the small set of app files
    needs to be compressed from scratch.
    """

    if verbose:
        if rich_print:
            rich.print("\t:hammer_and_wrench:  Appending application files.", file=sys.stderr)
        else:
            log("   🛠️  Appending application files.")

    # Read the deps file count from cache_info.json stored next to deps.tar.gz.
    num_deps_files = 0
    info_path = deps_tar.parent / "cache_info.json"
    try:
        with open(info_path) as f:
            num_deps_files = json.load(f).get("num_files", 0)
    except Exception:
        pass

    # Compress only the app files (small) into a temporary gzip stream.
    app_files_tar_gz = os.path.join(output_dir, "app-files.tar.gz")
    num_app_files = 0
    with tarfile.open(app_files_tar_gz, "w:gz") as tar:
        for root, _, files in os.walk(files_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=files_dir)
                tar.add(file_path, arcname=arcname)
                num_app_files += 1

    # Concatenate the two gzip streams — valid per RFC 1952.
    output_file = os.path.join(output_dir, "app.tar.gz")
    with open(output_file, "wb") as f_out:
        with open(str(deps_tar), "rb") as f_deps:
            shutil.copyfileobj(f_deps, f_out)
        with open(app_files_tar_gz, "rb") as f_app:
            shutil.copyfileobj(f_app, f_out)

    os.remove(app_files_tar_gz)
    return output_file, num_deps_files + num_app_files


def __compress_tar(source: str, target: str, verbose: bool = False, rich_print: bool = False) -> tuple[str, int]:
    """Compress the source directory into a tar.gz file in the target"""

    if verbose:
        if rich_print:
            rich.print("\t:hammer_and_wrench:  Compressing tarball from scratch.", file=sys.stderr)
        else:
            log("   🛠️  Compressing tarball from scratch.")

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


def __human_friendly_file_size(path: str) -> str:
    """Return a human-friendly string representation of the file size."""

    try:
        size = os.path.getsize(path)
    except OSError as e:
        raise Exception(f"error getting file size: {e}") from e

    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KiB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MiB"
    else:
        return f"{size / (1024 * 1024 * 1024):.2f} GiB"
