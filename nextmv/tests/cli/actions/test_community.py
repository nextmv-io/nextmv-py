"""Tests for nextmv.cli.actions.community."""

import unittest
from unittest.mock import MagicMock, patch


class TestGetCommunityApps(unittest.TestCase):
    @patch("nextmv.cli.actions.community.list_community_apps")
    def test_returns_list_of_community_app_objects(self, mock_list):
        mock_app1 = MagicMock()
        mock_app2 = MagicMock()
        mock_list.return_value = [mock_app1, mock_app2]

        client = MagicMock()

        from nextmv.cli.actions.community import get_community_apps

        result = get_community_apps(client)

        mock_list.assert_called_once_with(client)
        self.assertEqual(result, [mock_app1, mock_app2])

    @patch("nextmv.cli.actions.community.list_community_apps")
    def test_empty_list(self, mock_list):
        mock_list.return_value = []
        client = MagicMock()

        from nextmv.cli.actions.community import get_community_apps

        result = get_community_apps(client)

        self.assertEqual(result, [])


class TestListCommunityAppsDicts(unittest.TestCase):
    @patch("nextmv.cli.actions.community.list_community_apps")
    def test_returns_list_of_dicts(self, mock_list):
        mock_app1 = MagicMock()
        mock_app1.to_dict.return_value = {"name": "app-1", "description": "App One"}
        mock_app2 = MagicMock()
        mock_app2.to_dict.return_value = {"name": "app-2", "description": "App Two"}
        mock_list.return_value = [mock_app1, mock_app2]

        client = MagicMock()

        from nextmv.cli.actions.community import list_community_apps_dicts

        result = list_community_apps_dicts(client)

        mock_list.assert_called_once_with(client)
        self.assertEqual(result, [
            {"name": "app-1", "description": "App One"},
            {"name": "app-2", "description": "App Two"},
        ])

    @patch("nextmv.cli.actions.community.list_community_apps")
    def test_empty_list(self, mock_list):
        mock_list.return_value = []
        client = MagicMock()

        from nextmv.cli.actions.community import list_community_apps_dicts

        result = list_community_apps_dicts(client)

        self.assertEqual(result, [])


class TestCloneApp(unittest.TestCase):
    @patch("nextmv.cli.actions.community.clone_community_app")
    def test_calls_clone_with_defaults(self, mock_clone):
        client = MagicMock()

        from nextmv.cli.actions.community import clone_app

        clone_app(client=client, app="python-ortools-routing")

        mock_clone.assert_called_once_with(
            client=client,
            app="python-ortools-routing",
            directory=None,
            version="latest",
            verbose=False,
            rich_print=False,
            should_register=False,
        )

    @patch("nextmv.cli.actions.community.clone_community_app")
    def test_passes_all_params(self, mock_clone):
        client = MagicMock()

        from nextmv.cli.actions.community import clone_app

        clone_app(
            client=client,
            app="go-nextroute",
            directory="/tmp/my-app",
            version="v1.2.0",
            verbose=True,
            rich_print=True,
            should_register=True,
        )

        mock_clone.assert_called_once_with(
            client=client,
            app="go-nextroute",
            directory="/tmp/my-app",
            version="v1.2.0",
            verbose=True,
            rich_print=True,
            should_register=True,
        )

    @patch("nextmv.cli.actions.community.clone_community_app")
    def test_returns_none(self, mock_clone):
        mock_clone.return_value = None
        client = MagicMock()

        from nextmv.cli.actions.community import clone_app

        result = clone_app(client=client, app="go-nextroute")

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
