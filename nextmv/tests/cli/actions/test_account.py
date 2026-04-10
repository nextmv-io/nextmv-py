"""Tests for nextmv.cli.actions.account."""

import unittest
from unittest.mock import MagicMock, patch


class TestGetAccount(unittest.TestCase):
    @patch("nextmv.cli.actions.account.Account")
    def test_returns_account_dict(self, mock_account_class):
        mock_account = MagicMock()
        mock_account.to_dict.return_value = {"id": "my-account", "name": "My Account"}
        mock_account_class.get.return_value = mock_account

        client = MagicMock()

        from nextmv.cli.actions.account import get_account

        result = get_account(client, account_id="my-account")

        mock_account_class.get.assert_called_once_with(client=client, account_id="my-account")
        self.assertEqual(result, {"id": "my-account", "name": "My Account"})


class TestGetQueue(unittest.TestCase):
    @patch("nextmv.cli.actions.account.Account")
    def test_returns_queue_dict(self, mock_account_class):
        mock_queue = MagicMock()
        mock_queue.to_dict.return_value = {"depth": 5, "running": 2}
        mock_account = MagicMock()
        mock_account.queue.return_value = mock_queue
        mock_account_class.get.return_value = mock_account

        client = MagicMock()

        from nextmv.cli.actions.account import get_queue

        result = get_queue(client, account_id="my-account")

        mock_account_class.get.assert_called_once_with(client=client, account_id="my-account")
        mock_account.queue.assert_called_once()
        self.assertEqual(result, {"depth": 5, "running": 2})


if __name__ == "__main__":
    unittest.main()
