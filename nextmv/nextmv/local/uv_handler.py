import os
import platform
import sys


def _find_uv_binary() -> str:
    """
    Locate the uv binary at runtime.

    Resolves the binary in this order:
    1. If running in a PyInstaller bundle, the uv binary is expected to be bundled under
       `sys._MEIPASS/uv_bin/`.
    2. Otherwise, check whether uv module is installed and use its helper function to find
        the binary.
    3. Finally, check if uv is available on the system PATH.

    Returns
    -------
    str
        Absolute path to the uv binary.

    Raises
    ------
    FileNotFoundError
        If the uv binary cannot be located.
    """

    # 1. Check for PyInstaller bundled uv binary.
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # In case of single binary PyInstaller distribution, the uv binary is bundled
        # under sys._MEIPASS/uv_bin/.
        exe_suffix = ".exe" if platform.system() == "Windows" else ""
        uv_path = os.path.join(sys._MEIPASS, "uv_bin", f"uv{exe_suffix}")
        if not os.path.isfile(uv_path):
            raise FileNotFoundError(
                f"Bundled uv binary not found at {uv_path}, please ensure proper installation of the Nextmv CLI."
            )
        return uv_path

    # 2. Fall back to finding uv via the installed module (if available).
    try:
        import uv  # type: ignore[import]

        return uv.find_uv_bin()
    except ImportError:
        pass

    # 3. Finally, check if uv is available on the system PATH.
    from shutil import which

    uv_path = which("uv")
    if uv_path:
        return uv_path

    raise FileNotFoundError(
        "uv binary not found. Please ensure that uv is installed and available "
        + "on your system (via PATH or as module in Python)."
    )
