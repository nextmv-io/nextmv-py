#!/usr/bin/env bash
set -e

# Change to the project dir
cd "$(dirname "$0")"/../../nextmv

# Detect the platform
OS_NAME=$(uname -s | tr '[:upper:]' '[:lower:]')
echo "Detected platform: $OS_NAME"

# Set the separator based on the OS
if [[ "$OS_NAME" == *"mingw"* ]] || [[ "$OS_NAME" == *"msys"* ]] || [[ "$OS_NAME" == "windows" ]]; then
    ADD_DATA_SEPARATOR=";"
else
    ADD_DATA_SEPARATOR=":"
fi

# Resolve uv binary
UV_BIN=$(python -c "from uv import find_uv_bin; print(find_uv_bin())")
echo "Bundling uv binary from: $UV_BIN"

# Run PyInstaller
uv run --with pyinstaller pyinstaller \
    --name nextmv \
    --onefile \
    --clean \
    --add-data "nextmv/templates${ADD_DATA_SEPARATOR}nextmv/templates" \
    --add-data "nextmv/local/executor.py${ADD_DATA_SEPARATOR}nextmv/local" \
    --add-data "${UV_BIN}${ADD_DATA_SEPARATOR}uv_bin" \
    --console nextmv/cli/main.py
