import os
import tempfile
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

import yaml
from nextmv.input import InputFormat
from nextmv.local.registry import AppEntry, Registry, _get_registry_path


class TestAppEntry(unittest.TestCase):
    """Test cases for the AppEntry class."""

    def test_app_entry_creation(self):
        """Test creation of an AppEntry with all fields."""
        now = datetime.now(timezone.utc)
        entry = AppEntry(
            app_id="test-app",
            src="/path/to/app",
            content_format=InputFormat.JSON,
            created_at=now,
            updated_at=now,
            description="Test application",
        )

        self.assertEqual(entry.app_id, "test-app")
        self.assertEqual(entry.src, "/path/to/app")
        self.assertEqual(entry.content_format, InputFormat.JSON)
        self.assertEqual(entry.created_at, now)
        self.assertEqual(entry.updated_at, now)
        self.assertEqual(entry.description, "Test application")

    def test_app_entry_without_description(self):
        """Test creation of an AppEntry without optional description."""
        now = datetime.now(timezone.utc)
        entry = AppEntry(
            app_id="test-app",
            src="/path/to/app",
            content_format=InputFormat.CSV_ARCHIVE,
            created_at=now,
            updated_at=now,
        )

        self.assertEqual(entry.app_id, "test-app")
        self.assertIsNone(entry.description)

    def test_app_entry_serialization(self):
        """Test that AppEntry can be serialized to dict."""
        now = datetime.now(timezone.utc)
        entry = AppEntry(
            app_id="test-app",
            src="/path/to/app",
            content_format=InputFormat.JSON,
            created_at=now,
            updated_at=now,
            description="Test application",
        )

        entry_dict = entry.to_dict()
        self.assertIsInstance(entry_dict, dict)
        self.assertEqual(entry_dict["app_id"], "test-app")
        self.assertEqual(entry_dict["src"], "/path/to/app")
        self.assertEqual(entry_dict["description"], "Test application")


class TestRegistry(unittest.TestCase):
    """Test cases for the Registry class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.app_dir = os.path.join(self.test_dir, "test_app")
        os.makedirs(self.app_dir)

        # Create a minimal manifest file
        self.manifest_content = {
            "spec_version": "v1beta1",
            "id": "test-app",
            "name": "Test App",
            "description": "Test application",
            "execution": {"entrypoint": "main.py"},
            "type": "python",
            "runtime": "ghcr.io/nextmv-io/runtime/python:3.11",
            "files": ["main.py"],
        }

        self.manifest_path = os.path.join(self.app_dir, "app.yaml")
        with open(self.manifest_path, "w") as f:
            yaml.dump(self.manifest_content, f)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_registry_creation(self):
        """Test creation of an empty registry."""
        registry = Registry()
        self.assertEqual(len(registry.apps), 0)
        self.assertIsInstance(registry.apps, list)

    def test_registry_with_apps(self):
        """Test creation of a registry with initial apps."""
        now = datetime.now(timezone.utc)
        entry = AppEntry(
            app_id="test-app",
            src="/path/to/app",
            content_format=InputFormat.JSON,
            created_at=now,
            updated_at=now,
        )
        registry = Registry(apps=[entry])

        self.assertEqual(len(registry.apps), 1)
        self.assertEqual(registry.apps[0].app_id, "test-app")


class TestRegistryFromYAML(unittest.TestCase):
    """Test cases for Registry.from_yaml method."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.registry_dir = os.path.join(self.test_dir, ".nextmv")
        os.makedirs(self.registry_dir, exist_ok=True)
        self.registry_path = os.path.join(self.registry_dir, "registry.yaml")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch("nextmv.local.registry._get_registry_path")
    def test_from_yaml_creates_empty_registry_if_not_exists(self, mock_get_path):
        """Test that from_yaml creates an empty registry when file doesn't exist."""
        mock_get_path.return_value = self.registry_path

        registry = Registry.from_yaml()

        self.assertIsInstance(registry, Registry)
        self.assertEqual(len(registry.apps), 0)
        self.assertTrue(os.path.exists(self.registry_path))

    @patch("nextmv.local.registry._get_registry_path")
    def test_from_yaml_loads_existing_registry(self, mock_get_path):
        """Test that from_yaml loads an existing registry from file."""
        mock_get_path.return_value = self.registry_path

        # Create a registry file with one app
        now = datetime.now(timezone.utc)
        registry_data = {
            "apps": [
                {
                    "app_id": "test-app",
                    "src": "/path/to/app",
                    "content_format": "json",
                    "created_at": now.isoformat(),
                    "updated_at": now.isoformat(),
                    "description": "Test app",
                }
            ]
        }

        with open(self.registry_path, "w") as f:
            yaml.dump(registry_data, f)

        registry = Registry.from_yaml()

        self.assertEqual(len(registry.apps), 1)
        self.assertEqual(registry.apps[0].app_id, "test-app")
        self.assertEqual(registry.apps[0].src, "/path/to/app")
        self.assertEqual(registry.apps[0].description, "Test app")


class TestRegistryRegister(unittest.TestCase):
    """Test cases for Registry.register method."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.app_dir = os.path.join(self.test_dir, "test_app")
        os.makedirs(self.app_dir)

        # Create a minimal manifest file
        manifest_content = {
            "spec_version": "v1beta1",
            "id": "test-app",
            "name": "Test App",
            "execution": {"entrypoint": "main.py"},
            "type": "python",
            "runtime": "ghcr.io/nextmv-io/runtime/python:3.11",
            "files": ["main.py"],
        }

        with open(os.path.join(self.app_dir, "app.yaml"), "w") as f:
            yaml.dump(manifest_content, f)

        self.registry_dir = os.path.join(self.test_dir, ".nextmv")
        os.makedirs(self.registry_dir, exist_ok=True)
        self.registry_path = os.path.join(self.registry_dir, "registry.yaml")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch("nextmv.local.registry._get_registry_path")
    def test_register_with_auto_generated_id(self, mock_get_path):
        """Test registering an app with auto-generated ID."""
        mock_get_path.return_value = self.registry_path

        registry = Registry()
        entry = registry.register(src=self.app_dir)

        self.assertIsNotNone(entry.app_id)
        self.assertTrue(entry.app_id.startswith("local-app"))
        self.assertEqual(entry.src, os.path.abspath(self.app_dir))
        self.assertEqual(entry.content_format, InputFormat.JSON)
        self.assertIsNone(entry.description)
        self.assertEqual(len(registry.apps), 1)

    @patch("nextmv.local.registry._get_registry_path")
    def test_register_with_custom_id(self, mock_get_path):
        """Test registering an app with custom ID."""
        mock_get_path.return_value = self.registry_path

        registry = Registry()
        entry = registry.register(src=self.app_dir, app_id="my-custom-app")

        self.assertEqual(entry.app_id, "my-custom-app")
        self.assertEqual(len(registry.apps), 1)

    @patch("nextmv.local.registry._get_registry_path")
    def test_register_with_description(self, mock_get_path):
        """Test registering an app with description."""
        mock_get_path.return_value = self.registry_path

        registry = Registry()
        entry = registry.register(
            src=self.app_dir,
            app_id="my-app",
            description="My test application",
        )

        self.assertEqual(entry.description, "My test application")
        self.assertEqual(len(registry.apps), 1)

    @patch("nextmv.local.registry._get_registry_path")
    def test_register_normalizes_path(self, mock_get_path):
        """Test that registering normalizes the source path."""
        mock_get_path.return_value = self.registry_path

        registry = Registry()
        # Use a relative path
        relative_path = os.path.relpath(self.app_dir)
        entry = registry.register(src=relative_path, app_id="test-app")

        # Should be normalized to absolute path
        self.assertEqual(entry.src, os.path.abspath(relative_path))

    @patch("nextmv.local.registry._get_registry_path")
    def test_register_duplicate_entry_ignored(self, mock_get_path):
        """Test that duplicate entries are ignored."""
        mock_get_path.return_value = self.registry_path

        registry = Registry()
        entry1 = registry.register(src=self.app_dir, app_id="test-app")
        entry2 = registry.register(src=self.app_dir, app_id="test-app")

        # Should still have only one entry
        self.assertEqual(len(registry.apps), 1)
        self.assertEqual(entry1.app_id, entry2.app_id)
        self.assertEqual(entry1.src, entry2.src)

    def test_register_without_manifest_raises_error(self):
        """Test that registering without manifest raises FileNotFoundError."""
        # Create a directory without manifest
        empty_dir = os.path.join(self.test_dir, "empty_app")
        os.makedirs(empty_dir)

        registry = Registry()

        with self.assertRaises(FileNotFoundError) as context:
            registry.register(src=empty_dir, app_id="test-app")

        self.assertIn("manifest", str(context.exception).lower())

    @patch("nextmv.local.registry._get_registry_path")
    def test_register_with_csv_content_format(self, mock_get_path):
        """Test registering an app with CSV archive content format."""
        mock_get_path.return_value = self.registry_path

        # Create manifest with CSV archive content format
        csv_app_dir = os.path.join(self.test_dir, "csv_app")
        os.makedirs(csv_app_dir)

        manifest_content = {
            "spec_version": "v1beta1",
            "id": "csv-app",
            "name": "CSV App",
            "execution": {"entrypoint": "main.py"},
            "type": "python",
            "runtime": "ghcr.io/nextmv-io/runtime/python:3.11",
            "files": ["main.py"],
            "configuration": {"content": {"format": "csv-archive"}},
        }

        with open(os.path.join(csv_app_dir, "app.yaml"), "w") as f:
            yaml.dump(manifest_content, f)

        registry = Registry()
        entry = registry.register(src=csv_app_dir, app_id="csv-app")

        self.assertEqual(entry.content_format, InputFormat.CSV_ARCHIVE)


class TestRegistryEntry(unittest.TestCase):
    """Test cases for Registry.entry method."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.registry_dir = os.path.join(self.test_dir, ".nextmv")
        os.makedirs(self.registry_dir, exist_ok=True)
        self.registry_path = os.path.join(self.registry_dir, "registry.yaml")

        # Create test entries
        now = datetime.now(timezone.utc)
        self.entry1 = AppEntry(
            app_id="app-1",
            src="/path/to/app1",
            content_format=InputFormat.JSON,
            created_at=now,
            updated_at=now,
        )
        self.entry2 = AppEntry(
            app_id="app-2",
            src="/path/to/app2",
            content_format=InputFormat.JSON,
            created_at=now,
            updated_at=now,
        )

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_entry_find_by_app_id(self):
        """Test finding an entry by app_id."""
        registry = Registry(apps=[self.entry1, self.entry2])

        found = registry.entry(app_id="app-1")

        self.assertIsNotNone(found)
        self.assertEqual(found.app_id, "app-1")
        self.assertEqual(found.src, "/path/to/app1")

    def test_entry_find_by_src(self):
        """Test finding an entry by src."""
        registry = Registry(apps=[self.entry1, self.entry2])

        found = registry.entry(src="/path/to/app2")

        self.assertIsNotNone(found)
        self.assertEqual(found.app_id, "app-2")
        self.assertEqual(found.src, "/path/to/app2")

    def test_entry_find_by_both_app_id_and_src(self):
        """Test finding an entry by both app_id and src."""
        registry = Registry(apps=[self.entry1, self.entry2])

        # Should find when both match
        found = registry.entry(app_id="app-1", src="/path/to/app1")
        self.assertIsNotNone(found)
        self.assertEqual(found.app_id, "app-1")

        # Should not find when only one matches
        not_found = registry.entry(app_id="app-1", src="/path/to/app2")
        self.assertIsNone(not_found)

    def test_entry_not_found(self):
        """Test that entry returns None when not found."""
        registry = Registry(apps=[self.entry1, self.entry2])

        not_found = registry.entry(app_id="nonexistent")

        self.assertIsNone(not_found)

    def test_entry_with_empty_values(self):
        """Test that empty strings are treated as None."""
        registry = Registry(apps=[self.entry1])

        # Empty string should be treated as not provided
        found = registry.entry(app_id="app-1", src="")
        self.assertIsNotNone(found)

    def test_entry_normalizes_src_path(self):
        """Test that src path is normalized when searching."""
        # Create entry with absolute path
        abs_path = os.path.abspath(self.test_dir)
        now = datetime.now(timezone.utc)
        entry = AppEntry(
            app_id="test-app",
            src=abs_path,
            content_format=InputFormat.JSON,
            created_at=now,
            updated_at=now,
        )
        registry = Registry(apps=[entry])

        # Search with relative path
        rel_path = os.path.relpath(self.test_dir)
        found = registry.entry(src=rel_path)

        self.assertIsNotNone(found)
        self.assertEqual(found.app_id, "test-app")


class TestRegistryDeleteEntry(unittest.TestCase):
    """Test cases for Registry.delete_entry method."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.registry_dir = os.path.join(self.test_dir, ".nextmv")
        os.makedirs(self.registry_dir, exist_ok=True)
        self.registry_path = os.path.join(self.registry_dir, "registry.yaml")

        # Create test entries
        now = datetime.now(timezone.utc)
        self.entry1 = AppEntry(
            app_id="app-1",
            src="/path/to/app1",
            content_format=InputFormat.JSON,
            created_at=now,
            updated_at=now,
        )
        self.entry2 = AppEntry(
            app_id="app-2",
            src="/path/to/app2",
            content_format=InputFormat.JSON,
            created_at=now,
            updated_at=now,
        )
        self.entry3 = AppEntry(
            app_id="app-3",
            src="/path/to/app3",
            content_format=InputFormat.JSON,
            created_at=now,
            updated_at=now,
        )

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch("nextmv.local.registry._get_registry_path")
    def test_delete_entry_by_app_id(self, mock_get_path):
        """Test deleting an entry by app_id."""
        mock_get_path.return_value = self.registry_path

        registry = Registry(apps=[self.entry1, self.entry2, self.entry3])
        self.assertEqual(len(registry.apps), 3)

        registry.delete_entry(app_id="app-2")

        self.assertEqual(len(registry.apps), 2)
        self.assertIsNone(registry.entry(app_id="app-2"))
        self.assertIsNotNone(registry.entry(app_id="app-1"))
        self.assertIsNotNone(registry.entry(app_id="app-3"))

    @patch("nextmv.local.registry._get_registry_path")
    def test_delete_entry_by_src(self, mock_get_path):
        """Test deleting an entry by src."""
        mock_get_path.return_value = self.registry_path

        registry = Registry(apps=[self.entry1, self.entry2, self.entry3])

        registry.delete_entry(src="/path/to/app1")

        self.assertEqual(len(registry.apps), 2)
        self.assertIsNone(registry.entry(src="/path/to/app1"))
        self.assertIsNotNone(registry.entry(app_id="app-2"))

    @patch("nextmv.local.registry._get_registry_path")
    def test_delete_entry_by_both_app_id_and_src(self, mock_get_path):
        """Test deleting an entry by both app_id and src."""
        mock_get_path.return_value = self.registry_path

        registry = Registry(apps=[self.entry1, self.entry2])

        # Delete with both matching
        registry.delete_entry(app_id="app-1", src="/path/to/app1")

        self.assertEqual(len(registry.apps), 1)
        self.assertIsNone(registry.entry(app_id="app-1"))

    @patch("nextmv.local.registry._get_registry_path")
    def test_delete_entry_requires_both_to_match(self, mock_get_path):
        """Test that when both app_id and src are provided, both must match."""
        mock_get_path.return_value = self.registry_path

        registry = Registry(apps=[self.entry1, self.entry2])

        # Try to delete with mismatched app_id and src
        registry.delete_entry(app_id="app-1", src="/path/to/app2")

        # Should not delete anything
        self.assertEqual(len(registry.apps), 2)
        self.assertIsNotNone(registry.entry(app_id="app-1"))

    @patch("nextmv.local.registry._get_registry_path")
    def test_delete_nonexistent_entry_does_nothing(self, mock_get_path):
        """Test that deleting a nonexistent entry doesn't error."""
        mock_get_path.return_value = self.registry_path

        registry = Registry(apps=[self.entry1])

        # Should not raise an error
        registry.delete_entry(app_id="nonexistent")

        self.assertEqual(len(registry.apps), 1)


class TestRegistryUpdateEntry(unittest.TestCase):
    """Test cases for Registry.update_entry method."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.registry_dir = os.path.join(self.test_dir, ".nextmv")
        os.makedirs(self.registry_dir, exist_ok=True)
        self.registry_path = os.path.join(self.registry_dir, "registry.yaml")

        # Create test entries
        now = datetime.now(timezone.utc)
        self.entry1 = AppEntry(
            app_id="app-1",
            src="/path/to/app1",
            content_format=InputFormat.JSON,
            created_at=now,
            updated_at=now,
            description="Original description",
        )
        self.entry2 = AppEntry(
            app_id="app-2",
            src="/path/to/app2",
            content_format=InputFormat.JSON,
            created_at=now,
            updated_at=now,
        )

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch("nextmv.local.registry._get_registry_path")
    def test_update_entry_changes_description(self, mock_get_path):
        """Test updating an entry's description."""
        mock_get_path.return_value = self.registry_path

        registry = Registry(apps=[self.entry1, self.entry2])

        # Update the entry
        updated_entry = AppEntry(
            app_id="app-1",
            src="/path/to/app1",
            content_format=InputFormat.JSON,
            created_at=self.entry1.created_at,
            updated_at=self.entry1.updated_at,
            description="Updated description",
        )

        registry.update_entry(updated_entry)

        # Check that description was updated
        found = registry.entry(app_id="app-1")
        self.assertEqual(found.description, "Updated description")
        # updated_at should be changed
        self.assertNotEqual(found.updated_at, self.entry1.updated_at)

    @patch("nextmv.local.registry._get_registry_path")
    def test_update_entry_changes_content_format(self, mock_get_path):
        """Test updating an entry's content format."""
        mock_get_path.return_value = self.registry_path

        registry = Registry(apps=[self.entry1])

        # Update the entry with new content format
        updated_entry = AppEntry(
            app_id="app-1",
            src="/path/to/app1",
            content_format=InputFormat.CSV_ARCHIVE,  # Changed from JSON
            created_at=self.entry1.created_at,
            updated_at=self.entry1.updated_at,
            description="Original description",
        )

        registry.update_entry(updated_entry)

        # Check that content format was updated
        found = registry.entry(app_id="app-1")
        self.assertEqual(found.content_format, InputFormat.CSV_ARCHIVE)

    @patch("nextmv.local.registry._get_registry_path")
    def test_update_entry_requires_both_app_id_and_src_to_match(self, mock_get_path):
        """Test that update requires both app_id and src to match."""
        mock_get_path.return_value = self.registry_path

        registry = Registry(apps=[self.entry1, self.entry2])

        # Create update with mismatched app_id/src combination
        updated_entry = AppEntry(
            app_id="app-1",
            src="/path/to/different",  # Different src
            content_format=InputFormat.CSV_ARCHIVE,
            created_at=self.entry1.created_at,
            updated_at=self.entry1.updated_at,
            description="Should not update",
        )

        registry.update_entry(updated_entry)

        # Original entry should remain unchanged
        found = registry.entry(app_id="app-1")
        self.assertEqual(found.description, "Original description")
        self.assertEqual(found.content_format, InputFormat.JSON)

    @patch("nextmv.local.registry._get_registry_path")
    def test_update_nonexistent_entry_does_nothing(self, mock_get_path):
        """Test that updating a nonexistent entry doesn't error."""
        mock_get_path.return_value = self.registry_path

        registry = Registry(apps=[self.entry1])
        now = datetime.now(timezone.utc)

        # Try to update non-existent entry
        nonexistent_entry = AppEntry(
            app_id="nonexistent",
            src="/path/to/nonexistent",
            content_format=InputFormat.JSON,
            created_at=now,
            updated_at=now,
        )

        # Should not raise an error
        registry.update_entry(nonexistent_entry)

        # Registry should be unchanged
        self.assertEqual(len(registry.apps), 1)

    @patch("nextmv.local.registry._get_registry_path")
    def test_update_entry_updates_timestamp(self, mock_get_path):
        """Test that update_entry updates the updated_at timestamp."""
        mock_get_path.return_value = self.registry_path

        registry = Registry(apps=[self.entry1])
        original_updated_at = self.entry1.updated_at

        # Wait a tiny bit to ensure timestamp difference
        import time

        time.sleep(0.01)

        # Update the entry
        updated_entry = AppEntry(
            app_id="app-1",
            src="/path/to/app1",
            content_format=InputFormat.JSON,
            created_at=self.entry1.created_at,
            updated_at=self.entry1.updated_at,  # This will be overwritten
            description="Updated",
        )

        registry.update_entry(updated_entry)

        # Check that updated_at was changed
        found = registry.entry(app_id="app-1")
        self.assertGreater(found.updated_at, original_updated_at)


class TestRegistryListEntries(unittest.TestCase):
    """Test cases for Registry.list_entries method."""

    def test_list_entries_empty_registry(self):
        """Test listing entries from an empty registry."""
        registry = Registry()

        entries = registry.list_entries()

        self.assertEqual(len(entries), 0)
        self.assertIsInstance(entries, list)

    def test_list_entries_returns_all_apps(self):
        """Test that list_entries returns all apps in the registry."""
        now = datetime.now(timezone.utc)
        entry1 = AppEntry(
            app_id="app-1",
            src="/path/to/app1",
            content_format=InputFormat.JSON,
            created_at=now,
            updated_at=now,
        )
        entry2 = AppEntry(
            app_id="app-2",
            src="/path/to/app2",
            content_format=InputFormat.CSV_ARCHIVE,
            created_at=now,
            updated_at=now,
        )
        entry3 = AppEntry(
            app_id="app-3",
            src="/path/to/app3",
            content_format=InputFormat.JSON,
            created_at=now,
            updated_at=now,
        )

        registry = Registry(apps=[entry1, entry2, entry3])

        entries = registry.list_entries()

        self.assertEqual(len(entries), 3)
        app_ids = [e.app_id for e in entries]
        self.assertIn("app-1", app_ids)
        self.assertIn("app-2", app_ids)
        self.assertIn("app-3", app_ids)


class TestRegistryToYAML(unittest.TestCase):
    """Test cases for Registry.to_yaml method."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.registry_dir = os.path.join(self.test_dir, ".nextmv")
        os.makedirs(self.registry_dir, exist_ok=True)
        self.registry_path = os.path.join(self.registry_dir, "registry.yaml")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch("nextmv.local.registry._get_registry_path")
    def test_to_yaml_creates_file(self, mock_get_path):
        """Test that to_yaml creates the registry file."""
        mock_get_path.return_value = self.registry_path

        registry = Registry()
        registry.to_yaml()

        self.assertTrue(os.path.exists(self.registry_path))

    @patch("nextmv.local.registry._get_registry_path")
    def test_to_yaml_writes_correct_content(self, mock_get_path):
        """Test that to_yaml writes the correct content to file."""
        mock_get_path.return_value = self.registry_path

        now = datetime.now(timezone.utc)
        entry = AppEntry(
            app_id="test-app",
            src="/path/to/app",
            content_format=InputFormat.JSON,
            created_at=now,
            updated_at=now,
            description="Test application",
        )
        registry = Registry(apps=[entry])

        registry.to_yaml()

        # Read the file and verify content
        with open(self.registry_path) as f:
            data = yaml.safe_load(f)

        self.assertIn("apps", data)
        self.assertEqual(len(data["apps"]), 1)
        self.assertEqual(data["apps"][0]["app_id"], "test-app")
        self.assertEqual(data["apps"][0]["src"], "/path/to/app")
        self.assertEqual(data["apps"][0]["description"], "Test application")

    @patch("nextmv.local.registry._get_registry_path")
    def test_to_yaml_can_be_loaded_back(self, mock_get_path):
        """Test that data written by to_yaml can be loaded back correctly."""
        mock_get_path.return_value = self.registry_path

        now = datetime.now(timezone.utc)
        entry1 = AppEntry(
            app_id="app-1",
            src="/path/to/app1",
            content_format=InputFormat.JSON,
            created_at=now,
            updated_at=now,
        )
        entry2 = AppEntry(
            app_id="app-2",
            src="/path/to/app2",
            content_format=InputFormat.CSV_ARCHIVE,
            created_at=now,
            updated_at=now,
            description="Second app",
        )
        registry = Registry(apps=[entry1, entry2])

        # Write to file
        registry.to_yaml()

        # Load back
        loaded_registry = Registry.from_yaml()

        self.assertEqual(len(loaded_registry.apps), 2)
        self.assertEqual(loaded_registry.apps[0].app_id, "app-1")
        self.assertEqual(loaded_registry.apps[1].app_id, "app-2")
        self.assertEqual(loaded_registry.apps[1].description, "Second app")


class TestGetRegistryPath(unittest.TestCase):
    """Test cases for the _get_registry_path helper function."""

    def test_get_registry_path_returns_correct_path(self):
        """Test that _get_registry_path returns the expected path."""
        path = _get_registry_path()

        self.assertIsInstance(path, str)
        self.assertTrue(path.endswith(".nextmv/registry.yaml"))
        # Verify the .nextmv directory exists
        self.assertTrue(os.path.exists(os.path.dirname(path)))

    def test_get_registry_path_creates_directory(self):
        """Test that _get_registry_path creates the .nextmv directory if needed."""
        import pathlib
        import shutil

        # Get the path to the .nextmv directory
        home_dir = str(pathlib.Path.home())
        nextmv_dir = os.path.join(home_dir, ".nextmv")

        # Temporarily rename it if it exists
        temp_backup = None
        if os.path.exists(nextmv_dir):
            temp_backup = nextmv_dir + "_test_backup"
            if os.path.exists(temp_backup):
                shutil.rmtree(temp_backup)
            os.rename(nextmv_dir, temp_backup)

        try:
            # Call the function
            path = _get_registry_path()

            # Verify the directory was created
            self.assertTrue(os.path.exists(nextmv_dir))
            self.assertTrue(os.path.isdir(nextmv_dir))
            # Verify the path points to the registry file
            self.assertTrue(path.endswith("registry.yaml"))
        finally:
            # Restore the original directory if it existed
            if temp_backup:
                if os.path.exists(nextmv_dir):
                    shutil.rmtree(nextmv_dir)
                os.rename(temp_backup, nextmv_dir)


class TestRegistryIntegration(unittest.TestCase):
    """Integration tests for the Registry class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.app1_dir = os.path.join(self.test_dir, "app1")
        self.app2_dir = os.path.join(self.test_dir, "app2")
        os.makedirs(self.app1_dir)
        os.makedirs(self.app2_dir)

        # Create manifests for both apps
        manifest1 = {
            "spec_version": "v1beta1",
            "id": "app-1",
            "name": "App 1",
            "execution": {"entrypoint": "main.py"},
            "type": "python",
            "runtime": "ghcr.io/nextmv-io/runtime/python:3.11",
            "files": ["main.py"],
        }
        manifest2 = {
            "spec_version": "v1beta1",
            "id": "app-2",
            "name": "App 2",
            "execution": {"entrypoint": "main.py"},
            "type": "python",
            "runtime": "ghcr.io/nextmv-io/runtime/python:3.11",
            "files": ["main.py"],
            "configuration": {"content": {"format": "csv-archive"}},
        }

        with open(os.path.join(self.app1_dir, "app.yaml"), "w") as f:
            yaml.dump(manifest1, f)
        with open(os.path.join(self.app2_dir, "app.yaml"), "w") as f:
            yaml.dump(manifest2, f)

        self.registry_dir = os.path.join(self.test_dir, ".nextmv")
        os.makedirs(self.registry_dir, exist_ok=True)
        self.registry_path = os.path.join(self.registry_dir, "registry.yaml")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch("nextmv.local.registry._get_registry_path")
    def test_full_lifecycle(self, mock_get_path):
        """Test the full lifecycle: create, register, update, list, delete."""
        mock_get_path.return_value = self.registry_path

        # 1. Create a new registry
        registry = Registry.from_yaml()
        self.assertEqual(len(registry.apps), 0)

        # 2. Register two apps
        entry1 = registry.register(src=self.app1_dir, app_id="my-app-1", description="First app")
        entry2 = registry.register(src=self.app2_dir, app_id="my-app-2", description="Second app")

        # 3. Verify both are registered
        self.assertEqual(len(registry.apps), 2)
        self.assertEqual(entry1.content_format, InputFormat.JSON)
        self.assertEqual(entry2.content_format, InputFormat.CSV_ARCHIVE)

        # 4. List all entries
        entries = registry.list_entries()
        self.assertEqual(len(entries), 2)

        # 5. Find specific entries
        found1 = registry.entry(app_id="my-app-1")
        self.assertIsNotNone(found1)
        self.assertEqual(found1.description, "First app")

        found2 = registry.entry(src=os.path.abspath(self.app2_dir))
        self.assertIsNotNone(found2)
        self.assertEqual(found2.app_id, "my-app-2")

        # 6. Update an entry
        entry1.description = "Updated first app"
        registry.update_entry(entry1)
        updated = registry.entry(app_id="my-app-1")
        self.assertEqual(updated.description, "Updated first app")

        # 7. Delete an entry by app_id
        registry.delete_entry(app_id="my-app-1")
        self.assertEqual(len(registry.apps), 1)
        self.assertIsNone(registry.entry(app_id="my-app-1"))

        # 8. Delete remaining entry by src
        registry.delete_entry(src=os.path.abspath(self.app2_dir))
        self.assertEqual(len(registry.apps), 0)

        # 9. Verify persistence by loading from file
        loaded_registry = Registry.from_yaml()
        self.assertEqual(len(loaded_registry.apps), 0)

    @patch("nextmv.local.registry._get_registry_path")
    def test_persistence_across_instances(self, mock_get_path):
        """Test that registry changes persist across different instances."""
        mock_get_path.return_value = self.registry_path

        # Create and register in first instance
        registry1 = Registry.from_yaml()
        registry1.register(src=self.app1_dir, app_id="test-app")

        # Load in second instance
        registry2 = Registry.from_yaml()

        # Should see the app registered in first instance
        self.assertEqual(len(registry2.apps), 1)
        found = registry2.entry(app_id="test-app")
        self.assertIsNotNone(found)


if __name__ == "__main__":
    unittest.main()
