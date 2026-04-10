"""Tests for visual generation warning behavior."""

import os
import shutil
import tempfile
import unittest
from unittest.mock import patch


class TestVisualGenerationWarning(unittest.TestCase):
    """Test that visual generation failure logs a warning."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_visual_failure_logs_warning(self):
        """_extract_cloud_run_outputs logs a warning when visuals fail."""
        from nextmv.cli.mcp.tools._helpers import _extract_cloud_run_outputs

        run_dir = os.path.join(self.tmp_dir, "run-warn")

        with (
            patch(
                "nextmv.cli.mcp.tools._helpers._cloud_run_dir",
                return_value=run_dir,
            ),
            patch(
                "nextmv.cli.mcp.tools._helpers.process_run_visuals",
                side_effect=RuntimeError("plotly exploded"),
            ),
            patch(
                "nextmv.cli.mcp.tools._helpers.log",
            ) as mock_log,
        ):
            _extract_cloud_run_outputs(
                {"output": {"solution": {"x": 1}}},
                "ep",
                "run-warn",
            )
            mock_log.assert_called_once()
            msg = mock_log.call_args[0][0]
            self.assertIn("run-warn", msg)
            self.assertIn("plotly exploded", msg)
