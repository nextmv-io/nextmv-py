"""
Smoketest the MCP server that ships with the single-binary build.

`nextmv mcp --help` proves that the MCP modules can be imported, which is the
failure mode to expect from a frozen binary: PyInstaller resolves imports
statically, so anything the MCP stack reaches dynamically can go missing. This
script goes one step further and completes a JSON-RPC `initialize` handshake
against the bundled server over stdio, the transport that MCP clients use by
default, so that a binary which imports but cannot serve is caught in CI.

Usage:

    python .github/scripts/smoketest-mcp-server.py ./nextmv
"""

import json
import subprocess
import sys
import tempfile
import threading

# The handshake an MCP client sends first. The server is expected to answer
# with its capabilities and its own name and version.
REQUEST = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "smoketest", "version": "1"},
    },
}

# Generous, because the frozen binary is slow to start up on some platforms
# (Windows in particular) and this should not be a flaky test.
TIMEOUT_SECONDS = 90


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(f"usage: {sys.argv[0]} PATH_TO_BINARY")

    binary = sys.argv[1]

    # The server speaks JSON-RPC on stdout, so its logging must be kept out of
    # the way. It is captured to a file instead of a pipe, to be able to report
    # it without risking a blocking read on a pipe nobody is draining.
    with tempfile.TemporaryFile(mode="w+") as log:
        process = subprocess.Popen(
            [binary, "mcp", "serve", "--transport", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=log,
            text=True,
        )

        def fail(message: str) -> None:
            process.kill()
            log.seek(0)
            sys.exit(f"{message}\n--- server output ---\n{log.read()}")

        lines: list[str] = []
        reader = threading.Thread(target=lambda: lines.append(process.stdout.readline()), daemon=True)
        reader.start()

        process.stdin.write(json.dumps(REQUEST) + "\n")
        process.stdin.flush()

        reader.join(TIMEOUT_SECONDS)
        if reader.is_alive():
            fail(f"The MCP server did not respond within {TIMEOUT_SECONDS} seconds.")

        response = lines[0].strip()
        if not response:
            fail("The MCP server exited without responding to the initialize request.")

        try:
            server_info = json.loads(response)["result"]["serverInfo"]
        except (KeyError, ValueError):
            fail(f"The MCP server sent an unexpected response: {response}")

        print(f"MCP server responded to initialize: {server_info}")

        process.terminate()
        try:
            process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            process.kill()


if __name__ == "__main__":
    main()
