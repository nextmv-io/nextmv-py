"""Module with the logic for pushing an app to Nextmv Cloud."""

import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

import rich

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
        if manifest.type == ManifestType.PYTHON:
            __handle_python(app_dir, temp_dir, manifest, model, model_configuration, verbose, rich_print)

        found, missing, files = find_files(app_dir, manifest.files)
        manifest.confirm_mandatory_files(found)

        if len(missing) > 0:
            raise Exception(f"could not find files listed in manifest: {', '.join(missing)}")

        manifest.to_yaml(temp_dir)

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

        if verbose:
            if rich_print:
                rich.print(
                    f":clipboard: Copied files listed in [magenta]{MANIFEST_FILE_NAME}[/magenta] manifest.",
                    file=sys.stderr,
                )
            else:
                log(f'📋 Copied files listed in "{MANIFEST_FILE_NAME}" manifest.')

        if manifest.type == ManifestType.PYTHON:
            _cleanup_python_model(app_dir, model_configuration, verbose)

        output_dir = tempfile.mkdtemp(prefix="nextmv-build-out-")
        tar_file, file_count = __compress_tar(temp_dir, output_dir)
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

    if verbose:
        log(result.stdout)


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

    if verbose:
        log(result.stdout)


def __handle_python(
    app_dir: str,
    temp_dir: str,
    manifest: Manifest,
    model: Model | None = None,
    model_configuration: ModelConfiguration | None = None,
    verbose: bool = False,
    rich_print: bool = False,
) -> None:
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

    __install_dependencies(manifest, app_dir, temp_dir)


def __install_dependencies(  # noqa: C901 # complexity
    manifest: Manifest,
    app_dir: str,
    temp_dir: str,
) -> None:
    """Install dependencies for the Python app."""

    if manifest.python is None:
        return

    pip_requirements = manifest.python.pip_requirements

    if pip_requirements is None or pip_requirements == "":
        # If no pip requirements are specified, we do not install any dependencies.
        return

    if isinstance(pip_requirements, list):
        # If pip_requirements is a list, we write it to a temporary file so that we can
        # pass it to pip.
        pip_requirements_file = os.path.join(temp_dir, "requirements.txt")
        with open(pip_requirements_file, "w") as f:
            for requirement in pip_requirements:
                f.write(requirement + "\n")

        pip_requirements = pip_requirements_file
    elif isinstance(pip_requirements, str):
        # If pip_requirements is a string, we expect it to be a file path to a
        # requirements file.
        pip_requirements = pip_requirements.strip()
        if not os.path.isfile(os.path.join(app_dir, pip_requirements)):
            raise FileNotFoundError(f"pip requirements file '{pip_requirements}' not found in '{app_dir}'")

        if os.path.basename(pip_requirements) == "pyproject.toml":
            # If the requirements file is a pyproject.toml, read [project.dependencies]
            # and write them to a temporary requirements.txt file for pip.
            deps = read_pyproject_dependencies(os.path.join(app_dir, pip_requirements))
            pip_requirements_file = os.path.join(temp_dir, "requirements.txt")
            with open(pip_requirements_file, "w") as f:
                for dep in deps:
                    f.write(dep + "\n")

            pip_requirements = pip_requirements_file

    dep_dir = os.path.join(".nextmv", "python", "deps")
    target_dir = os.path.join(temp_dir, dep_dir)

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
    command = [
        uv_bin,
        "pip",
        "install",
        "-r",
        pip_requirements,
        "--only-binary=:all:",
        "--upgrade",
        "--target",
        target_dir,
        "--quiet",
        f"--python-platform={uv_platform}",
        f"--python-version={python_version}",
    ]
    result = subprocess.run(
        command,
        cwd=app_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Merge stderr into stdout
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


def __compress_tar(source: str, target: str) -> tuple[str, int]:
    """Compress the source directory into a tar.gz file in the target"""

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
