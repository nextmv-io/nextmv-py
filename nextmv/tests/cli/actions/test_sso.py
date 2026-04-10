"""Tests for nextmv.cli.actions.sso."""

import unittest
from unittest.mock import MagicMock, patch


class TestDeleteDomain(unittest.TestCase):
    @patch("nextmv.cli.actions.sso.SSOConfiguration")
    def test_deletes_domain(self, mock_sso_class):
        mock_sso = MagicMock()
        mock_sso_class.get.return_value = mock_sso

        client = MagicMock()

        from nextmv.cli.actions.sso import delete_domain

        result = delete_domain(client, domain="example.com")

        mock_sso_class.get.assert_called_once_with(client=client)
        mock_sso.delete_domain.assert_called_once_with(domain="example.com")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
