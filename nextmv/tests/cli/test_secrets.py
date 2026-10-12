import unittest
from unittest.mock import MagicMock, patch

from nextmv.cli.cloud.secrets import app
from nextmv.cloud.secrets import Secret, SecretOperation, SecretOperationType, SecretType
from typer.testing import CliRunner


class TestSecretsUpdateCommand(unittest.TestCase):
    """Test the `nextmv cloud secrets update` command."""

    def setUp(self):
        self.runner = CliRunner()
        self.cloud_app = MagicMock()
        self.cloud_app.patch_secrets_collection.return_value.to_dict.return_value = {"id": "sc-1"}

    def _invoke(self, *args: str):
        with patch(
            "nextmv.cli.cloud.secrets.update.build_cloud_app",
            return_value=(self.cloud_app, False),
        ):
            return self.runner.invoke(app, ["update", "--app-id", "my-app", "--secrets-collection-id", "sc-1", *args])

    def test_builds_operations(self):
        result = self._invoke(
            "--name",
            "New Name",
            "--create",
            '{"type": "env", "location": "NEW_KEY", "value": "a"}',
            "--update",
            '[{"type": "env", "location": "API_KEY", "value": "b"}]',
            "--delete",
            '{"type": "file", "location": "/old.pem"}',
        )

        self.assertEqual(result.exit_code, 0, result.output)
        self.cloud_app.patch_secrets_collection.assert_called_once_with(
            secrets_collection_id="sc-1",
            name="New Name",
            description=None,
            operations=[
                SecretOperation(
                    op=SecretOperationType.CREATE, secret_type=SecretType.ENV, location="NEW_KEY", value="a"
                ),
                SecretOperation(
                    op=SecretOperationType.UPDATE, secret_type=SecretType.ENV, location="API_KEY", value="b"
                ),
                SecretOperation(op=SecretOperationType.DELETE, secret_type=SecretType.FILE, location="/old.pem"),
            ],
        )

    def test_metadata_only_sends_no_operations(self):
        result = self._invoke("--description", "New Description")

        self.assertEqual(result.exit_code, 0, result.output)
        self.cloud_app.patch_secrets_collection.assert_called_once_with(
            secrets_collection_id="sc-1",
            name=None,
            description="New Description",
            operations=None,
        )

    def test_no_options_errors(self):
        result = self._invoke()

        self.assertEqual(result.exit_code, 1)
        self.cloud_app.patch_secrets_collection.assert_not_called()

    def test_delete_with_value_errors_without_echoing_it(self):
        result = self._invoke("--delete", '{"type": "env", "location": "API_KEY", "value": "super-secret"}')

        self.assertEqual(result.exit_code, 1)
        self.assertNotIn("super-secret", result.output)
        self.cloud_app.patch_secrets_collection.assert_not_called()

    def test_secrets_replaces_all_via_sdk(self):
        self.cloud_app.update_secrets_collection.return_value.to_dict.return_value = {"id": "sc-1"}

        result = self._invoke("--secrets", '{"type": "env", "location": "API_KEY", "value": "a"}')

        self.assertEqual(result.exit_code, 0, result.output)
        self.cloud_app.update_secrets_collection.assert_called_once_with(
            secrets_collection_id="sc-1",
            name=None,
            description=None,
            secrets=[Secret(secret_type=SecretType.ENV, location="API_KEY", value="a")],
        )
        self.cloud_app.patch_secrets_collection.assert_not_called()

    def test_secrets_cannot_be_combined_with_operations(self):
        result = self._invoke(
            "--secrets",
            '{"type": "env", "location": "API_KEY", "value": "a"}',
            "--delete",
            '{"type": "env", "location": "OLD_KEY"}',
        )

        self.assertEqual(result.exit_code, 1)
        self.cloud_app.update_secrets_collection.assert_not_called()
        self.cloud_app.patch_secrets_collection.assert_not_called()


if __name__ == "__main__":
    unittest.main()
