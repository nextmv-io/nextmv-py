import unittest

from nextmv.__about__ import __version__
from nextmv.cli.main import app
from typer.testing import CliRunner


class TestVersion(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.app = app

    def test_version_command(self):
        result = self.runner.invoke(self.app, ["version"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn(__version__, result.output)
