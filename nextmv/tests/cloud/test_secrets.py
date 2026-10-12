import unittest
from unittest.mock import MagicMock, patch

from nextmv.cloud import Application, Client
from nextmv.cloud.secrets import (
    Secret,
    SecretOperation,
    SecretOperationType,
    SecretsCollection,
    SecretType,
)

MASKED_VALUE = "***************"

COLLECTION_SUMMARY = {
    "id": "sc-1",
    "application_id": "my-app",
    "name": "API Keys",
    "description": "Keys for external services",
    "created_at": "2026-08-12T15:04:05Z",
    "updated_at": "2026-09-10T09:21:33Z",
}

MASKED_COLLECTION = {
    **COLLECTION_SUMMARY,
    "secrets": [
        {"type": "env", "location": "API_KEY", "value": MASKED_VALUE},
        {"type": "env", "location": "DATABASE_URL", "value": MASKED_VALUE},
    ],
}


def _response(data: dict) -> MagicMock:
    response = MagicMock()
    response.json.return_value = data
    return response


class TestSecretOperation(unittest.TestCase):
    """Test validation and serialization of SecretOperation."""

    def test_create_and_update_serialize_with_value(self):
        for op in (SecretOperationType.CREATE, SecretOperationType.UPDATE):
            with self.subTest(op=op):
                operation = SecretOperation(op=op, secret_type=SecretType.ENV, location="API_KEY", value="v")
                self.assertEqual(
                    operation.to_dict(),
                    {"op": op.value, "type": "env", "location": "API_KEY", "value": "v"},
                )

    def test_delete_serializes_without_value(self):
        operation = SecretOperation(op=SecretOperationType.DELETE, secret_type=SecretType.FILE, location="/a.pem")
        self.assertEqual(operation.to_dict(), {"op": "delete", "type": "file", "location": "/a.pem"})

    def test_create_and_update_require_value(self):
        for op in ("create", "update"):
            with self.subTest(op=op):
                with self.assertRaises(ValueError) as context:
                    SecretOperation.from_dict({"op": op, "type": "env", "location": "API_KEY"})
                self.assertIn(f"value is required for a `{op}` operation", str(context.exception))

    def test_delete_rejects_value(self):
        with self.assertRaises(ValueError) as context:
            SecretOperation.from_dict({"op": "delete", "type": "env", "location": "API_KEY", "value": "v"})
        self.assertIn("value must not be set for a `delete` operation", str(context.exception))


class TestPatchSecretsCollection(unittest.TestCase):
    """Test the PATCH-backed partial update of a secrets collection."""

    def setUp(self):
        self.app = Application(id="my-app", client=Client(api_key="test-key"))

    def test_metadata_only(self):
        with patch.object(Client, "request", return_value=_response(MASKED_COLLECTION)) as mock_request:
            collection = self.app.patch_secrets_collection("sc-1", name="New Name", description="New Description")

        mock_request.assert_called_once_with(
            method="PATCH",
            endpoint="v1/applications/my-app/secrets/sc-1",
            payload={"name": "New Name", "description": "New Description"},
        )
        self.assertIsInstance(collection, SecretsCollection)

    def test_operations_from_models_and_dicts(self):
        operations = [
            SecretOperation(op=SecretOperationType.CREATE, secret_type=SecretType.ENV, location="NEW", value="a"),
            {"op": "update", "type": "env", "location": "API_KEY", "value": "b"},
            {"op": "delete", "type": "file", "location": "/old.pem"},
        ]
        with patch.object(Client, "request", return_value=_response(MASKED_COLLECTION)) as mock_request:
            self.app.patch_secrets_collection("sc-1", operations=operations)

        mock_request.assert_called_once_with(
            method="PATCH",
            endpoint="v1/applications/my-app/secrets/sc-1",
            payload={
                "operations": [
                    {"op": "create", "type": "env", "location": "NEW", "value": "a"},
                    {"op": "update", "type": "env", "location": "API_KEY", "value": "b"},
                    {"op": "delete", "type": "file", "location": "/old.pem"},
                ]
            },
        )

    def test_same_location_with_different_types_is_allowed(self):
        operations = [
            {"op": "delete", "type": "env", "location": "KEY"},
            {"op": "create", "type": "file", "location": "KEY", "value": "a"},
        ]
        with patch.object(Client, "request", return_value=_response(MASKED_COLLECTION)) as mock_request:
            self.app.patch_secrets_collection("sc-1", operations=operations)

        mock_request.assert_called_once()

    def test_invalid_requests_raise_without_calling_api(self):
        cases = {
            "nothing to change": ({}, "at least one of name, description, or operations"),
            "empty operations": ({"operations": []}, "operations must not be an empty list"),
            "duplicate secret": (
                {
                    "operations": [
                        {"op": "delete", "type": "env", "location": "API_KEY"},
                        {"op": "create", "type": "env", "location": "API_KEY", "value": "a"},
                    ]
                },
                "operation at index 1 targets the same secret",
            ),
            "invalid operation type": (
                {"operations": ["not-an-operation"]},
                "operation at index 0 must be either a SecretOperation or dict object",
            ),
        }
        for case, (kwargs, message) in cases.items():
            with self.subTest(case=case):
                with patch.object(Client, "request") as mock_request:
                    with self.assertRaises(ValueError) as context:
                        self.app.patch_secrets_collection("sc-1", **kwargs)

                self.assertIn(message, str(context.exception))
                mock_request.assert_not_called()


class TestUpdateSecretsCollection(unittest.TestCase):
    """Test that update_secrets_collection never resends fetched secret values."""

    def setUp(self):
        self.app = Application(id="my-app", client=Client(api_key="test-key"))

    def test_metadata_only_uses_patch_without_secrets(self):
        for secrets in (None, []):
            with self.subTest(secrets=secrets):
                with patch.object(Client, "request", return_value=_response(MASKED_COLLECTION)) as mock_request:
                    self.app.update_secrets_collection("sc-1", name="New Name", secrets=secrets)

                mock_request.assert_called_once_with(
                    method="PATCH",
                    endpoint="v1/applications/my-app/secrets/sc-1",
                    payload={"name": "New Name"},
                )

    def test_nothing_to_update_raises(self):
        with patch.object(Client, "request") as mock_request:
            with self.assertRaises(ValueError):
                self.app.update_secrets_collection("sc-1")

        mock_request.assert_not_called()

    def test_with_secrets_replaces_via_patch_operations(self):
        responses = [_response(MASKED_COLLECTION), _response(MASKED_COLLECTION)]
        with patch.object(Client, "request", side_effect=responses) as mock_request:
            self.app.update_secrets_collection(
                "sc-1",
                description="New Description",
                secrets=[
                    Secret(secret_type=SecretType.ENV, location="API_KEY", value="new-api-key"),
                    {"type": "file", "location": "/cert.pem", "value": "cert"},
                ],
            )

        self.assertEqual(mock_request.call_count, 2)
        get_call, patch_call = mock_request.call_args_list
        self.assertEqual(get_call.kwargs["method"], "GET")
        self.assertEqual(patch_call.kwargs["method"], "PATCH")
        self.assertEqual(patch_call.kwargs["endpoint"], "v1/applications/my-app/secrets/sc-1")

        payload = patch_call.kwargs["payload"]
        self.assertEqual(
            payload,
            {
                "description": "New Description",
                "operations": [
                    {"op": "update", "type": "env", "location": "API_KEY", "value": "new-api-key"},
                    {"op": "create", "type": "file", "location": "/cert.pem", "value": "cert"},
                    {"op": "delete", "type": "env", "location": "DATABASE_URL"},
                ],
            },
        )
        self.assertNotIn(MASKED_VALUE, str(payload))

    def test_never_uses_put(self):
        responses = [_response(MASKED_COLLECTION), _response(MASKED_COLLECTION), _response(MASKED_COLLECTION)]
        with patch.object(Client, "request", side_effect=responses) as mock_request:
            self.app.update_secrets_collection("sc-1", name="New Name")
            self.app.update_secrets_collection(
                "sc-1",
                secrets=[Secret(secret_type=SecretType.ENV, location="API_KEY", value="v")],
            )

        methods = [call.kwargs["method"] for call in mock_request.call_args_list]
        self.assertNotIn("PUT", methods)

    def test_invalid_secret_raises_before_any_request(self):
        with patch.object(Client, "request") as mock_request:
            with self.assertRaises(ValueError):
                self.app.update_secrets_collection("sc-1", secrets=["not-a-secret"])

        mock_request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
