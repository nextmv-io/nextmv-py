"""
Tests for the encoding behaviour of _cli_call in nextmv.cli.init.

On Windows, subprocess pipes default to the system codepage (e.g. cp1252).
Byte 0x8f is undefined in cp1252, so without an explicit encoding this raises
UnicodeDecodeError.  The fix decodes each stream independently:

- stderr  → utf-8 with errors="replace"  (human-facing, replacement char is OK)
- stdout  → utf-8 strict                 (machine-readable JSON; corruption must
                                          surface as a clear UnicodeDecodeError,
                                          not a silent JSONDecodeError later)
"""

import subprocess
import unittest
from io import BytesIO
from unittest.mock import MagicMock, patch

import typer


def _make_pipe(raw_bytes: bytes):
    """Return a mock binary pipe whose iteration yields lines from *raw_bytes*."""
    bio = BytesIO(raw_bytes)
    mock_pipe = MagicMock()
    mock_pipe.__iter__ = lambda self: iter(bio)
    return mock_pipe


def _make_process(stdout_bytes: bytes = b"", stderr_bytes: bytes = b"", returncode: int = 0):
    mock = MagicMock()
    mock.stdout = _make_pipe(stdout_bytes)
    mock.stderr = _make_pipe(stderr_bytes)
    mock.returncode = returncode
    mock.wait = MagicMock()
    return mock


class TestCliCallEncoding(unittest.TestCase):
    """Verify that _cli_call survives non-UTF-8 bytes and applies the correct
    decoding strategy to each stream."""

    def _invoke(self, stdout_bytes: bytes, stderr_bytes: bytes) -> subprocess.CompletedProcess:
        """Call _cli_call with a mocked Popen and return its result."""
        from nextmv.cli.init import _cli_call

        mock_process = _make_process(stdout_bytes, stderr_bytes)

        with patch("nextmv.cli.init.subprocess.Popen", return_value=mock_process):
            return _cli_call(["echo", "test"])

    def test_non_utf8_in_stderr_replaced_not_raised(self):
        """Byte 0x8f (undefined in cp1252) in stderr must not raise; it becomes a replacement char."""
        result = self._invoke(
            stdout_bytes=b"",
            stderr_bytes=b"warning: bad byte \x8f here\n",
        )
        # The replacement character U+FFFD (or '?') appears; no exception was raised.
        self.assertIn("warning: bad byte", result.stderr)

    def test_valid_utf8_stderr_preserved(self):
        """Normal UTF-8 stderr (including non-ASCII) must be preserved exactly."""
        result = self._invoke(
            stdout_bytes=b"",
            stderr_bytes="info: résumé 日本語\n".encode("utf-8"),
        )
        self.assertIn("résumé", result.stderr)
        self.assertIn("日本語", result.stderr)

    def test_valid_utf8_stdout_preserved(self):
        """Normal UTF-8 stdout is decoded and returned intact."""
        result = self._invoke(
            stdout_bytes=b'{"key": "value"}\n',
            stderr_bytes=b"",
        )
        self.assertIn('"key"', result.stdout)

    def test_non_utf8_in_stdout_raises_unicode_error(self):
        """Non-UTF-8 bytes in stdout must not be silently swallowed.

        The UnicodeDecodeError is caught by _cli_call's outer handler, which
        prints a human-readable message and raises typer.Exit(code=1).  That is
        the correct production behaviour: the caller sees a clear failure rather
        than a confusing JSONDecodeError or silently corrupted data.
        """
        with self.assertRaises((UnicodeDecodeError, typer.Exit)):
            self._invoke(
                stdout_bytes=b'{"key": "\x8f"}\n',
                stderr_bytes=b"",
            )

    def test_popen_called_in_binary_mode(self):
        """_cli_call must open the subprocess in binary mode (no text=True / encoding kwarg)
        so that each stream can be decoded with its own strategy."""
        from nextmv.cli.init import _cli_call

        mock_process = _make_process(b'{"ok": true}\n', b"")

        with patch("nextmv.cli.init.subprocess.Popen", return_value=mock_process) as mock_popen:
            _cli_call(["echo", "test"])

        call_kwargs = mock_popen.call_args[1]
        # Must NOT pass text=True or a global encoding – binary mode is required.
        self.assertNotIn("encoding", call_kwargs)
        self.assertNotIn("text", call_kwargs)


if __name__ == "__main__":
    unittest.main()
