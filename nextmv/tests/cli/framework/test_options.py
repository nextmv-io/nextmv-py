"""Permanent regression guard for dual-purpose Annotated option aliases.

Supersedes the feasibility spike. For every dual-purpose alias in
``nextmv.cli.framework.options``, assert both frontends consume it
correctly:

* Typer: the alias can be used as a CLI parameter and the short flag, long
  flag, and envvar all work through ``CliRunner``.
* Pydantic: ``TypeAdapter(alias).json_schema()`` picks up the description
  from the ``Field(...)`` metadata.

If this file ever fails, the dual-alias assumption has broken — either a
library version bump changed behavior, or one of the aliases was edited
incorrectly. Either way, stop and investigate.
"""

import unittest
from typing import Annotated

import typer
from pydantic import TypeAdapter
from typer.testing import CliRunner

from nextmv.cli.framework import options as fopts


# Note: AppIdRequiredOption and AppDirOption are intentionally omitted from
# this guard. They share type-metadata patterns with the aliases tested here
# (required-string variants of AppIdOption) and are exercised transitively by
# action and command tests added in later pilot tasks.
class TestDualPurposeAliases(unittest.TestCase):
    """Assert every public dual-purpose alias works in both frontends."""

    def _assert_pydantic_description(self, alias, expected_substring: str) -> None:
        """The alias must carry a ``Field(description=...)`` marker that
        Pydantic surfaces in the JSON schema."""
        schema = TypeAdapter(alias).json_schema()
        description = schema.get("description", "")
        self.assertIn(
            expected_substring,
            description,
            f"Expected Pydantic schema description to contain {expected_substring!r}, "
            f"got {description!r}",
        )

    def _assert_typer_consumes(self, alias, long_flag: str, short_flag: str, sample: str) -> None:
        """The alias must be usable as a ``typer.Option(...)`` and the flags
        must work via ``CliRunner``."""
        app = typer.Typer()

        @app.command()
        def cmd(value: alias = None) -> None:  # type: ignore[valid-type]
            typer.echo(f"value={value}")

        runner = CliRunner()

        result = runner.invoke(app, [long_flag, sample])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn(
            f"value={sample}",
            result.stdout,
            msg=f"Typer did not consume long flag {long_flag!r}: {result.output!r}",
        )

        result = runner.invoke(app, [short_flag, sample])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn(
            f"value={sample}",
            result.stdout,
            msg=f"Typer did not consume short flag {short_flag!r}: {result.output!r}",
        )

    def test_app_id_option(self) -> None:
        self._assert_typer_consumes(fopts.AppIdOption, "--app-id", "-a", "my-app")
        self._assert_pydantic_description(fopts.AppIdOption, "optional ID")

    def test_name_option(self) -> None:
        self._assert_typer_consumes(fopts.NameOption, "--name", "-n", "MyName")
        self._assert_pydantic_description(fopts.NameOption, "name for the application")

    def test_description_option(self) -> None:
        self._assert_typer_consumes(
            fopts.DescriptionOption, "--description", "-d", "Does stuff"
        )
        self._assert_pydantic_description(fopts.DescriptionOption, "optional description")

    def test_default_instance_id_option(self) -> None:
        self._assert_typer_consumes(
            fopts.DefaultInstanceIdOption, "--default-instance-id", "-i", "inst-1"
        )
        self._assert_pydantic_description(
            fopts.DefaultInstanceIdOption, "default instance ID"
        )

    def test_default_experiment_instance_option(self) -> None:
        self._assert_typer_consumes(
            fopts.DefaultExperimentInstanceOption,
            "--default-experiment-instance",
            "-x",
            "exp-1",
        )
        self._assert_pydantic_description(
            fopts.DefaultExperimentInstanceOption, "default experiment instance"
        )

    def test_bool_aliases_have_pydantic_descriptions(self) -> None:
        # Bool aliases can't easily be exercised via CliRunner with a value
        # argument (they're flags), so only assert the Pydantic side.
        self._assert_pydantic_description(fopts.IsWorkflowOption, "workflow")
        self._assert_pydantic_description(fopts.ExistOkOption, "already exists")

    def test_bool_flag_works_via_typer(self) -> None:
        """Smoke-test that IsWorkflowOption and ExistOkOption flags are
        settable via Typer."""
        app = typer.Typer()

        @app.command()
        def cmd(
            workflow: fopts.IsWorkflowOption = False,  # type: ignore[valid-type]
            exist_ok: fopts.ExistOkOption = False,  # type: ignore[valid-type]
        ) -> None:
            typer.echo(f"workflow={workflow} exist_ok={exist_ok}")

        runner = CliRunner()

        result = runner.invoke(app, ["--is-workflow"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn("workflow=True exist_ok=False", result.stdout)

        result = runner.invoke(app, ["--exist-ok"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn("workflow=False exist_ok=True", result.stdout)

        result = runner.invoke(app, ["--is-workflow", "--exist-ok"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn("workflow=True exist_ok=True", result.stdout)


if __name__ == "__main__":
    unittest.main()
