"""Module with the logic for pushing an app to Nextmv Cloud."""

import glob
import os
import platform
import re
import shutil
import subprocess
import tarfile
import tempfile
from typing import Optional

from nextmv.logger import log
from nextmv.manifest import MANIFEST_FILE_NAME, Manifest, ManifestBuild, ManifestType
from nextmv.model import Model, ModelConfiguration, _cleanup_python_model

_MANDATORY_FILES_PER_TYPE = {
    ManifestType.PYTHON: ["main.py"],
    ManifestType.GO: ["main"],
    ManifestType.JAVA: ["main.jar"],
}


def _package(
    app_dir: str,
    manifest: Manifest,
    model: Optional[Model] = None,
    model_configuration: Optional[ModelConfiguration] = None,
    verbose: bool = False,
) -> tuple[str, str]:
    """Package the app into a tarball."""

    with tempfile.TemporaryDirectory(prefix="nextmv-temp-") as temp_dir:
        if manifest.type == ManifestType.PYTHON:
            __handle_python(app_dir, temp_dir, manifest, model, model_configuration, verbose)

        found, missing, files = __find_files(app_dir, manifest.files)
        __confirm_mandatory_files(manifest, found)

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
            log(f'📋 Copied files listed in "{MANIFEST_FILE_NAME}" manifest.')

        if manifest.type == ManifestType.PYTHON:
            _cleanup_python_model(app_dir, model_configuration, verbose)

        output_dir = tempfile.mkdtemp(prefix="nextmv-build-out-")
        tar_file, file_count = __compress_tar(temp_dir, output_dir)
        file_count_msg = f"{file_count} file" if file_count == 1 else f"{file_count} files"
        if verbose:
            try:
                size = __human_friendly_file_size(tar_file)
                log(f"📦 Packaged application ({file_count_msg}, {size}).")
            except Exception:
                log(f"📦 Packaged application ({file_count_msg}).")

        return tar_file, output_dir


def _run_build_command(
    app_dir: str,
    manifest_build: Optional[ManifestBuild] = None,
    verbose: bool = False,
) -> None:
    """Run the build command specified in the manifest."""

    if manifest_build is None or manifest_build.command is None or manifest_build.command == "":
        return

    elements = manifest_build.command.split(" ")
    command_str = " ".join(elements)
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


def _run_pre_push_command(
    app_dir: str,
    pre_push_command: Optional[str] = None,
    verbose: bool = False,
) -> None:
    """Run the pre-push command specified in the manifest."""

    if pre_push_command is None or pre_push_command == "":
        return

    elements = ["bash", "-c", pre_push_command]
    if platform.system() == "Windows":
        elements = ["cmd", "/c", pre_push_command]

    command_str = " ".join(elements)
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


def __find_files(
    app_dir: str,
    filters: list[str],
) -> tuple[list[str], list[str], list[dict[str, str]]]:
    """Find all files matching the given filters in the given directory."""

    found = []
    missing = []

    # Temporarily switch to the directory to make the globbing work
    cwd = os.getcwd()
    try:
        os.chdir(app_dir)
    except OSError as e:
        raise Exception(f"error changing to file root directory: {e}") from e

    for filter in filters:
        # We support "some/path/" ending with a "/". We consider it equivalent
        # to "some/path/*".
        pattern = filter
        if filter.endswith("/"):
            pattern = filter + "*"
        # If the pattern starts with a '!': negate the pattern
        negated = False
        if pattern.startswith("!"):
            pattern = pattern[1:]
            negated = True
        matches = glob.glob(pattern, recursive=True)
        if not matches and not negated:
            missing.append(filter)
        else:
            if negated:
                found = [f for f in found if f not in matches]
            else:
                for match in matches:
                    if os.path.isdir(match):
                        continue

                    found.append(match)

    # Switch back to the original directory
    os.chdir(cwd)

    files = []
    for file in found:
        files.append(
            {
                "interior_path": file,
                "absolute_path": os.path.join(app_dir, file),
            }
        )

    return found, missing, files


def __confirm_mandatory_files(manifest: Manifest, present_files: list[str]) -> None:
    """Confirm that all mandatory files are present in the given list of files."""

    mandatory_files = _MANDATORY_FILES_PER_TYPE[manifest.type]
    found_files = {os.path.normpath(file): True for file in present_files}
    missing_files = [file for file in mandatory_files if file not in found_files]

    if missing_files:
        raise Exception(f"missing mandatory files: {', '.join(missing_files)}")


def __handle_python(
    app_dir: str,
    temp_dir: str,
    manifest: Manifest,
    model: Optional[Model] = None,
    model_configuration: Optional[ModelConfiguration] = None,
    verbose: bool = False,
) -> None:
    """Handles the Python-specific packaging logic."""

    if model is not None and model_configuration is not None:
        if verbose:
            log("🔮 Encoding Python model.")
        model.save(app_dir, model_configuration)

    if verbose:
        log("🐍 Bundling Python dependencies.")
    __install_dependencies(manifest, app_dir, temp_dir)


def __install_dependencies(
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

    py_cmd = __get_python_command()
    dep_dir = os.path.join(".nextmv", "python", "deps")
    command = [
        py_cmd,
        "-m",
        "pip",
        "install",
        "-r",
        pip_requirements,
        "--platform=manylinux2014_aarch64",
        "--platform=manylinux_2_17_aarch64",
        "--platform=manylinux_2_24_aarch64",
        "--platform=manylinux_2_28_aarch64",
        "--platform=linux_aarch64",
        "--only-binary=:all:",
        "--python-version=3.11",
        "--implementation=cp",
        "--upgrade",
        "--no-warn-conflicts",
        "--target",
        os.path.join(temp_dir, dep_dir),
        "--no-user",  # We explicitly avoid user mode (mainly to fix issues with Windows store Python installations)
        "--no-input",
        "--quiet",
    ]
    result = subprocess.run(
        command,
        cwd=app_dir,
        text=True,
        capture_output=True,
        check=True,
    )
    if result.returncode != 0:
        raise Exception(f"error installing dependencies: {result.stderr}")


def __run_command(binary: str, dir: str, redirect_out_err: bool, *arguments: str) -> str:
    os_agnostic_cmd = binary
    if arguments:
        os_agnostic_cmd += " " + " ".join(arguments)

    if platform.system() == "Windows":
        bin = "cmd"
        args = ["/c", os_agnostic_cmd]
    else:
        bin = "bash"
        args = ["-c", os_agnostic_cmd]

    cmd = subprocess.Popen(
        [bin] + args,
        cwd=dir if dir else None,
        env=os.environ,
        stdout=subprocess.PIPE if redirect_out_err else None,
        stderr=subprocess.PIPE if redirect_out_err else None,
        text=True,
    )

    if redirect_out_err:
        out, err = cmd.communicate()
        if cmd.returncode != 0:
            raise Exception(f"Command failed with error: {err}")
        return out
    else:
        cmd.wait()
        if cmd.returncode != 0:
            raise Exception("Command failed")
        return ""


def __get_python_command() -> str:
    py_cmds = ["python3", "python"]
    py_cmd = ""
    for cmd in py_cmds:
        try:
            output = __run_command(cmd, "", True, "--version")
            __confirm_python_version(output)
            py_cmd = cmd
            break
        except Exception:
            continue

    if not py_cmd:
        raise Exception("Python not found in PATH")

    output = __run_command(py_cmd, "", True, "-m", "pip", "--version")
    __confirm_pip_version(output)

    return py_cmd


def __confirm_pip_version(output: str) -> None:
    elements = output.split()
    if len(elements) < 2:
        raise Exception("pip version not found")

    version = elements[1].strip()
    re_version = re.compile(r"\d+\.\d+")
    if re_version.match(version):
        try:
            major, _, _ = map(int, version.split("."))
        except ValueError:
            major, _ = map(int, version.split("."))

        if major >= 22:
            return

    raise Exception("pip version 22.0 or higher is required")


def __confirm_python_version(output: str) -> None:
    elements = output.split()
    if len(elements) < 2:
        raise Exception("python version not found")

    version = elements[1].strip()
    re_version = re.compile(r"\d+\.\d+\.\d+")
    if re_version.match(version):
        try:
            major, minor, _ = map(int, version.split("."))
        except ValueError:
            major, minor = map(int, version.split("."))

        if major == 3 and minor >= 9:
            return

    raise Exception("python version 3.9 or higher is required")


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
