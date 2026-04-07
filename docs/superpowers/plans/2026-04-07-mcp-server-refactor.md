# MCP Server Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract shared business logic from CLI commands and MCP tools into a standalone `actions/` module, eliminating duplication and enabling direct testing of core functions.

**Architecture:** Create `cli/actions/` with one module per domain. Each module contains pure functions that take a `Client`/`Application` and return data. CLI commands and MCP tools become thin wrappers that import from actions. Split the monolithic MCP test file by domain.

**Tech Stack:** Python 3.13, pytest, nextmv SDK (`nextmv.cloud`), Typer (CLI), FastMCP (MCP server)

**Key paths:**
- Actions: `nextmv/nextmv/cli/actions/`
- CLI commands: `nextmv/nextmv/cli/cloud/`
- MCP tools: `nextmv/nextmv/cli/mcp/tools/`
- Tests: `nextmv/tests/cli/`

---

## Task 1: Scaffold the actions module

**Files:**
- Create: `nextmv/nextmv/cli/actions/__init__.py`

- [ ] **Step 1: Create the actions package**

```python
# nextmv/nextmv/cli/actions/__init__.py
"""Shared business logic for CLI commands and MCP tools.

Each submodule contains pure functions that:
- Take a Client or Application as their first argument
- Take plain-typed business parameters
- Return data (dict, list, str, bool, None)
- Have no side effects (no printing, no file I/O)
"""
```

- [ ] **Step 2: Verify the module is importable**

Run: `cd nextmv && python -c "import nextmv.cli.actions"`
Expected: No output, no errors.

- [ ] **Step 3: Commit**

```bash
git add nextmv/nextmv/cli/actions/__init__.py
git commit -m "refactor: scaffold cli/actions package for shared business logic"
```

---

## Task 2: Extract app actions + tests

**Files:**
- Create: `nextmv/nextmv/cli/actions/app.py`
- Create: `nextmv/tests/cli/actions/__init__.py`
- Create: `nextmv/tests/cli/actions/test_app.py`
- Modify: `nextmv/nextmv/cli/cloud/app/list.py`
- Modify: `nextmv/nextmv/cli/cloud/app/create.py`
- Modify: `nextmv/nextmv/cli/cloud/app/get.py`
- Modify: `nextmv/nextmv/cli/cloud/app/delete.py`
- Modify: `nextmv/nextmv/cli/cloud/app/update.py`
- Modify: `nextmv/nextmv/cli/cloud/app/push.py`
- Modify: `nextmv/nextmv/cli/cloud/app/exists.py`
- Modify: `nextmv/nextmv/cli/mcp/tools/app.py`

- [ ] **Step 1: Write the action module tests**

```python
# nextmv/tests/cli/actions/__init__.py
# (empty)
```

```python
# nextmv/tests/cli/actions/test_app.py
"""Tests for cli/actions/app.py core functions."""

import unittest
from unittest.mock import MagicMock, patch

from nextmv.cli.actions.app import (
    app_exists,
    create_app,
    delete_app,
    get_app,
    list_apps,
    push_app,
    update_app,
)


class TestListApps(unittest.TestCase):
    @patch("nextmv.cli.actions.app.list_applications")
    def test_list_apps_returns_dicts(self, mock_list):
        app1 = MagicMock()
        app1.to_dict.return_value = {"id": "app-1", "name": "App 1"}
        app2 = MagicMock()
        app2.to_dict.return_value = {"id": "app-2", "name": "App 2"}
        mock_list.return_value = [app1, app2]

        client = MagicMock()
        result = list_apps(client)

        mock_list.assert_called_once_with(client)
        self.assertEqual(result, [
            {"id": "app-1", "name": "App 1"},
            {"id": "app-2", "name": "App 2"},
        ])

    @patch("nextmv.cli.actions.app.list_applications")
    def test_list_apps_empty(self, mock_list):
        mock_list.return_value = []
        result = list_apps(MagicMock())
        self.assertEqual(result, [])


class TestCreateApp(unittest.TestCase):
    @patch("nextmv.cli.actions.app.Application")
    def test_create_app_minimal(self, mock_app_cls):
        mock_app = MagicMock()
        mock_app.to_dict.return_value = {"id": "new-app", "name": "New App"}
        mock_app_cls.new.return_value = mock_app

        client = MagicMock()
        result = create_app(client, name="New App")

        mock_app_cls.new.assert_called_once_with(
            client=client,
            name="New App",
            id=None,
            description=None,
            is_workflow=False,
            exist_ok=False,
            default_instance_id=None,
            default_experiment_instance=None,
        )
        self.assertEqual(result, {"id": "new-app", "name": "New App"})

    @patch("nextmv.cli.actions.app.Application")
    def test_create_app_all_params(self, mock_app_cls):
        mock_app = MagicMock()
        mock_app.to_dict.return_value = {"id": "my-app"}
        mock_app_cls.new.return_value = mock_app

        client = MagicMock()
        result = create_app(
            client,
            name="My App",
            app_id="my-app",
            description="desc",
            is_workflow=True,
            exist_ok=True,
            default_instance_id="prod",
            default_experiment_instance="exp-1",
        )

        mock_app_cls.new.assert_called_once_with(
            client=client,
            name="My App",
            id="my-app",
            description="desc",
            is_workflow=True,
            exist_ok=True,
            default_instance_id="prod",
            default_experiment_instance="exp-1",
        )
        self.assertEqual(result, {"id": "my-app"})


class TestGetApp(unittest.TestCase):
    @patch("nextmv.cli.actions.app.Application")
    def test_get_app(self, mock_app_cls):
        mock_app = MagicMock()
        mock_app.to_dict.return_value = {"id": "my-app", "name": "My App"}
        mock_app_cls.get.return_value = mock_app

        client = MagicMock()
        result = get_app(client, app_id="my-app")

        mock_app_cls.get.assert_called_once_with(client=client, id="my-app")
        self.assertEqual(result, {"id": "my-app", "name": "My App"})


class TestDeleteApp(unittest.TestCase):
    @patch("nextmv.cli.actions.app.Application")
    def test_delete_app(self, mock_app_cls):
        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app

        client = MagicMock()
        delete_app(client, app_id="my-app")

        mock_app_cls.assert_called_once_with(client=client, id="my-app")
        mock_app.delete.assert_called_once()


class TestAppExists(unittest.TestCase):
    @patch("nextmv.cli.actions.app.Application")
    def test_app_exists_true(self, mock_app_cls):
        mock_app_cls.exists.return_value = True
        result = app_exists(MagicMock(), app_id="my-app")
        self.assertTrue(result)

    @patch("nextmv.cli.actions.app.Application")
    def test_app_exists_false(self, mock_app_cls):
        mock_app_cls.exists.return_value = False
        result = app_exists(MagicMock(), app_id="my-app")
        self.assertFalse(result)


class TestUpdateApp(unittest.TestCase):
    @patch("nextmv.cli.actions.app.Application")
    def test_update_app(self, mock_app_cls):
        mock_app = MagicMock()
        mock_updated = MagicMock()
        mock_updated.to_dict.return_value = {"id": "my-app", "name": "Updated"}
        mock_app.update.return_value = mock_updated
        mock_app_cls.return_value = mock_app

        client = MagicMock()
        result = update_app(client, app_id="my-app", name="Updated")

        mock_app.update.assert_called_once_with(
            name="Updated",
            description=None,
            default_instance_id=None,
            default_experiment_instance=None,
        )
        self.assertEqual(result, {"id": "my-app", "name": "Updated"})


class TestPushApp(unittest.TestCase):
    @patch("nextmv.cli.actions.app.Application")
    def test_push_app(self, mock_app_cls):
        mock_app = MagicMock()
        mock_app_cls.return_value = mock_app

        client = MagicMock()
        push_app(client, app_id="my-app", app_dir="/path/to/app")

        mock_app.push.assert_called_once_with(app_dir="/path/to/app")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd nextmv && python -m pytest tests/cli/actions/test_app.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'nextmv.cli.actions.app'`

- [ ] **Step 3: Write the action module**

```python
# nextmv/nextmv/cli/actions/app.py
"""Core application management actions.

Pure functions that wrap SDK calls. No CLI or MCP concerns.
"""

from typing import Any

from nextmv.cloud import Application, Client, list_applications


def list_apps(client: Client) -> list[dict[str, Any]]:
    """List all applications in the account."""
    apps = list_applications(client)
    return [a.to_dict() for a in apps]


def create_app(
    client: Client,
    name: str,
    app_id: str | None = None,
    description: str | None = None,
    is_workflow: bool = False,
    exist_ok: bool = False,
    default_instance_id: str | None = None,
    default_experiment_instance: str | None = None,
) -> dict[str, Any]:
    """Create a new application. Returns the app dict."""
    return Application.new(
        client=client,
        name=name,
        id=app_id,
        description=description,
        is_workflow=is_workflow,
        exist_ok=exist_ok,
        default_instance_id=default_instance_id,
        default_experiment_instance=default_experiment_instance,
    ).to_dict()


def get_app(client: Client, app_id: str) -> dict[str, Any]:
    """Get application details."""
    return Application.get(client=client, id=app_id).to_dict()


def delete_app(client: Client, app_id: str) -> None:
    """Delete an application."""
    Application(client=client, id=app_id).delete()


def app_exists(client: Client, app_id: str) -> bool:
    """Check whether an application exists."""
    return Application.exists(client=client, id=app_id)


def update_app(
    client: Client,
    app_id: str,
    name: str | None = None,
    description: str | None = None,
    default_instance_id: str | None = None,
    default_experiment_instance: str | None = None,
) -> dict[str, Any]:
    """Update application attributes. Returns the updated app dict."""
    app = Application(client=client, id=app_id)
    return app.update(
        name=name,
        description=description,
        default_instance_id=default_instance_id,
        default_experiment_instance=default_experiment_instance,
    ).to_dict()


def push_app(client: Client, app_id: str, app_dir: str) -> None:
    """Push local code to a cloud application."""
    app = Application(client=client, id=app_id)
    app.push(app_dir=app_dir)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd nextmv && python -m pytest tests/cli/actions/test_app.py -v`
Expected: All 9 tests PASS.

- [ ] **Step 5: Update CLI commands to use actions**

For each CLI command file, replace the inline SDK call with an import from actions. The Typer decorator, options, progress messages, and output handling stay as-is.

**`cli/cloud/app/list.py`** — replace the SDK call:
```python
# Add import at top:
from nextmv.cli.actions.app import list_apps as _list_apps

# Replace in the list() function body:
#   cloud_apps = list_applications(client)
#   cloud_apps_dicts = [cloud_app.to_dict() for cloud_app in cloud_apps]
# With:
#   cloud_apps_dicts = _list_apps(client)
```

**`cli/cloud/app/create.py`** — replace the SDK call:
```python
# Add import at top:
from nextmv.cli.actions.app import create_app as _create_app

# Replace in the create() function body:
#   cloud_app = Application.new(
#       client=client,
#       name=name,
#       id=app_id,
#       description=description,
#       is_workflow=is_workflow,
#       exist_ok=exist_ok,
#       default_instance_id=default_instance_id,
#       default_experiment_instance=default_experiment_instance,
#   )
#   print_json(cloud_app.to_dict())
# With:
#   result = _create_app(
#       client,
#       name=name,
#       app_id=app_id,
#       description=description,
#       is_workflow=is_workflow,
#       exist_ok=exist_ok,
#       default_instance_id=default_instance_id,
#       default_experiment_instance=default_experiment_instance,
#   )
#   print_json(result)
```

**`cli/cloud/app/get.py`** — replace the SDK call:
```python
# Add import at top:
from nextmv.cli.actions.app import get_app as _get_app

# Replace in the get() function body:
#   cloud_app = Application.get(client=client, id=app_id)
#   cloud_app_dict = cloud_app.to_dict()
# With:
#   cloud_app_dict = _get_app(client, app_id=app_id)
```

**`cli/cloud/app/delete.py`** — replace the SDK call:
```python
# Add import at top:
from nextmv.cli.actions.app import delete_app as _delete_app

# Replace in the delete() function body (after the confirmation flow):
#   cloud_app, _ = build_cloud_app(app_id=app_id, profile=profile)
#   cloud_app.delete()
# With:
#   client = Client(profile=profile)
#   _delete_app(client, app_id=app_id)
```

**`cli/cloud/app/exists.py`** — replace the SDK call:
```python
# Add import at top:
from nextmv.cli.actions.app import app_exists as _app_exists

# Replace the SDK call with:
#   exists_result = _app_exists(client, app_id=app_id)
```

**`cli/cloud/app/update.py`** — replace the SDK call:
```python
# Add import at top:
from nextmv.cli.actions.app import update_app as _update_app

# Replace in the update() function body:
#   cloud_app, _ = build_cloud_app(app_id=app_id, profile=profile)
#   in_progress(msg="Updating application...")
#   updated_app = cloud_app.update(
#       name=name,
#       description=description,
#       default_instance_id=default_instance_id,
#       default_experiment_instance=default_experiment_instance,
#   )
#   success(f"Application [magenta]{app_id}[/magenta] updated successfully.")
#   updated_app_dict = updated_app.to_dict()
# With:
#   client = Client(profile=profile)
#   in_progress(msg="Updating application...")
#   updated_app_dict = _update_app(
#       client,
#       app_id=app_id,
#       name=name,
#       description=description,
#       default_instance_id=default_instance_id,
#       default_experiment_instance=default_experiment_instance,
#   )
#   success(f"Application [magenta]{app_id}[/magenta] updated successfully.")
```

**`cli/cloud/app/push.py`** — replace the SDK push call:
```python
# Add import at top:
from nextmv.cli.actions.app import push_app as _push_app

# Replace the app.push() call with:
#   _push_app(client, app_id=app_id, app_dir=app_dir)
# Note: push.py also creates versions and instances. Only replace the push() call itself.
# Read push.py fully before editing — it has more complex logic than other app commands.
```

- [ ] **Step 6: Update MCP tools to use actions**

**`cli/mcp/tools/app.py`** — replace SDK calls with action imports:

```python
"""MCP tools for cloud application management."""

from typing import Any

from mcp.server.fastmcp import FastMCP

from nextmv.cli.actions.app import (
    app_exists,
    create_app,
    delete_app,
    get_app,
    list_apps,
    push_app,
    update_app,
)
from nextmv.cli.mcp.tools import _helpers


def register(mcp: FastMCP) -> None:
    """Register cloud application management tools."""

    @mcp.tool()
    def cloud_list_apps() -> list[dict[str, Any]]:
        """List all Nextmv Cloud applications in the current account.

        Returns a list of application dictionaries containing each
        application's ID, name, description, and default instance.
        """

        return list_apps(_helpers._get_client())

    @mcp.tool()
    def cloud_get_app(app_id: str) -> dict[str, Any]:
        """Get details of a specific Nextmv Cloud application.

        Returns the full application object including its name,
        description, default instance, and creation timestamp.

        Args:
            app_id: The application ID (e.g., ``"my-routing-app"``).
        """

        return get_app(_helpers._get_client(), app_id=app_id)

    @mcp.tool()
    def cloud_create_app(
        name: str,
        app_id: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create a new Nextmv Cloud application.

        Returns the created application object. A version and default
        instance are automatically provisioned.

        Args:
            name: A human-readable name for the application.
            app_id: Optional URL-friendly ID. Auto-generated from
                the name if omitted.
            description: Optional description of what the application does.
        """

        return create_app(
            _helpers._get_client(),
            name=name,
            app_id=_helpers._none_if_empty(app_id),
            description=_helpers._none_if_empty(description),
        )

    @mcp.tool()
    def cloud_delete_app(app_id: str) -> str:
        """Delete a Nextmv Cloud application permanently.

        This action cannot be undone. All versions, instances, and
        run history associated with the application will be removed.

        Args:
            app_id: The application ID to delete.
        """

        delete_app(_helpers._get_client(), app_id=app_id)
        return f"Deleted application {app_id}"

    @mcp.tool()
    def cloud_app_exists(app_id: str) -> bool:
        """Check whether a Nextmv Cloud application exists.

        Returns True if an application with the given ID exists in
        the current account, False otherwise.

        Args:
            app_id: The application ID to check.
        """

        return app_exists(_helpers._get_client(), app_id=app_id)

    @mcp.tool()
    def cloud_update_app(
        app_id: str,
        name: str | None = None,
        description: str | None = None,
        default_instance_id: str | None = None,
    ) -> dict[str, Any]:
        """Update attributes of a Nextmv Cloud application.

        Only the provided fields are updated; omitted fields remain
        unchanged. Returns the updated application object.

        Args:
            app_id: The application ID to update.
            name: New human-readable name for the application.
            description: New description.
            default_instance_id: New default instance ID used when no
                instance is specified at run time.
        """

        return update_app(
            _helpers._get_client(),
            app_id=app_id,
            name=_helpers._none_if_empty(name),
            description=_helpers._none_if_empty(description),
            default_instance_id=_helpers._none_if_empty(default_instance_id),
        )

    @mcp.tool()
    def cloud_push_app(app_id: str, app_dir: str) -> str:
        """Push local application code to a Nextmv Cloud application.

        Uploads the contents of a local directory as a new version of
        the application. The directory must contain an ``app.yaml``
        manifest.

        Args:
            app_id: The application ID to push to.
            app_dir: Absolute path to the local directory containing the
                application code and ``app.yaml`` manifest.
        """

        push_app(_helpers._get_client(), app_id=app_id, app_dir=app_dir)
        return f"Pushed {app_dir} to application {app_id}"
```

- [ ] **Step 7: Run all existing tests**

Run: `cd nextmv && python -m pytest tests/cli/ -v`
Expected: All existing tests PASS. No regressions.

- [ ] **Step 8: Commit**

```bash
git add nextmv/nextmv/cli/actions/app.py nextmv/tests/cli/actions/ \
    nextmv/nextmv/cli/cloud/app/ nextmv/nextmv/cli/mcp/tools/app.py
git commit -m "refactor: extract app actions, update CLI and MCP to use them"
```

---

## Task 3: Extract version actions + tests

**Files:**
- Create: `nextmv/nextmv/cli/actions/version.py`
- Create: `nextmv/tests/cli/actions/test_version.py`
- Modify: `nextmv/nextmv/cli/cloud/version/create.py`
- Modify: `nextmv/nextmv/cli/cloud/version/delete.py`
- Modify: `nextmv/nextmv/cli/cloud/version/get.py`
- Modify: `nextmv/nextmv/cli/cloud/version/list.py`
- Modify: `nextmv/nextmv/cli/cloud/version/update.py`
- Modify: `nextmv/nextmv/cli/mcp/tools/version.py`

Follow the same pattern as Task 2. The action functions are:

- [ ] **Step 1: Write the action module**

```python
# nextmv/nextmv/cli/actions/version.py
"""Core version management actions."""

from typing import Any

from nextmv.cloud import Application, Client


def list_versions(client: Client, app_id: str) -> list[dict[str, Any]]:
    """List all versions for an application."""
    app = Application(client=client, id=app_id)
    return [v.to_dict() for v in app.list_versions()]


def get_version(client: Client, app_id: str, version_id: str) -> dict[str, Any]:
    """Get version details."""
    app = Application(client=client, id=app_id)
    return app.version(version_id=version_id).to_dict()


def create_version(
    client: Client,
    app_id: str,
    version_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
    exist_ok: bool = False,
) -> dict[str, Any]:
    """Create a new version. Returns the version dict."""
    app = Application(client=client, id=app_id)
    return app.new_version(
        id=version_id,
        name=name,
        description=description,
        exist_ok=exist_ok,
    ).to_dict()


def update_version(
    client: Client,
    app_id: str,
    version_id: str,
    name: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Update a version. Returns the updated version dict."""
    app = Application(client=client, id=app_id)
    return app.update_version(
        version_id=version_id,
        name=name,
        description=description,
    ).to_dict()


def delete_version(client: Client, app_id: str, version_id: str) -> None:
    """Delete a version."""
    app = Application(client=client, id=app_id)
    app.delete_version(version_id=version_id)
```

- [ ] **Step 2: Write tests for the action module**

Write `nextmv/tests/cli/actions/test_version.py` following the same mock pattern as `test_app.py`. Test each function: `list_versions`, `get_version`, `create_version`, `update_version`, `delete_version`. Mock `Application` class.

- [ ] **Step 3: Run tests to verify they pass**

Run: `cd nextmv && python -m pytest tests/cli/actions/test_version.py -v`
Expected: All tests PASS.

- [ ] **Step 4: Update CLI commands to use actions**

Update each file in `cli/cloud/version/` to import from `nextmv.cli.actions.version` and replace the SDK calls. Keep all Typer options, progress messages, and output handling.

- [ ] **Step 5: Update MCP tools to use actions**

Update `cli/mcp/tools/version.py` to import from `nextmv.cli.actions.version` and replace direct SDK calls. Keep `_none_if_empty()` normalization and MCP docstrings.

- [ ] **Step 6: Run all existing tests**

Run: `cd nextmv && python -m pytest tests/cli/ -v`
Expected: All tests PASS.

- [ ] **Step 7: Commit**

```bash
git add nextmv/nextmv/cli/actions/version.py nextmv/tests/cli/actions/test_version.py \
    nextmv/nextmv/cli/cloud/version/ nextmv/nextmv/cli/mcp/tools/version.py
git commit -m "refactor: extract version actions, update CLI and MCP"
```

---

## Task 4: Extract instance actions + tests

**Files:**
- Create: `nextmv/nextmv/cli/actions/instance.py`
- Create: `nextmv/tests/cli/actions/test_instance.py`
- Modify: `nextmv/nextmv/cli/cloud/instance/*.py`
- Modify: `nextmv/nextmv/cli/mcp/tools/instance.py`

Follow the same pattern as Tasks 2-3. The action functions are:

- [ ] **Step 1: Write the action module**

```python
# nextmv/nextmv/cli/actions/instance.py
"""Core instance management actions."""

from typing import Any

from nextmv.cloud import Application, Client, InstanceConfiguration


def list_instances(client: Client, app_id: str) -> list[dict[str, Any]]:
    """List all instances for an application."""
    app = Application(client=client, id=app_id)
    return [i.to_dict() for i in app.list_instances()]


def get_instance(client: Client, app_id: str, instance_id: str) -> dict[str, Any]:
    """Get instance details."""
    app = Application(client=client, id=app_id)
    return app.instance(instance_id=instance_id).to_dict()


def create_instance(
    client: Client,
    app_id: str,
    version_id: str,
    instance_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
    configuration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a new instance. Returns the instance dict."""
    app = Application(client=client, id=app_id)
    config = InstanceConfiguration(**configuration) if configuration else None
    return app.new_instance(
        version_id=version_id,
        id=instance_id,
        name=name,
        description=description,
        configuration=config,
    ).to_dict()


def update_instance(
    client: Client,
    app_id: str,
    instance_id: str,
    name: str | None = None,
    version_id: str | None = None,
    description: str | None = None,
    configuration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Update an instance. Returns the updated instance dict."""
    app = Application(client=client, id=app_id)
    return app.update_instance(
        id=instance_id,
        name=name,
        version_id=version_id,
        description=description,
        configuration=configuration,
    ).to_dict()


def delete_instance(client: Client, app_id: str, instance_id: str) -> None:
    """Delete an instance."""
    app = Application(client=client, id=app_id)
    app.delete_instance(instance_id=instance_id)
```

- [ ] **Step 2: Write tests, update CLI, update MCP, run all tests, commit**

Follow steps 2-7 from Task 3.

```bash
git commit -m "refactor: extract instance actions, update CLI and MCP"
```

---

## Task 5: Extract input_set actions + tests

**Files:**
- Create: `nextmv/nextmv/cli/actions/input_set.py`
- Create: `nextmv/tests/cli/actions/test_input_set.py`
- Modify: `nextmv/nextmv/cli/cloud/input_set/*.py`
- Modify: `nextmv/nextmv/cli/mcp/tools/input_set.py`

- [ ] **Step 1: Write the action module**

```python
# nextmv/nextmv/cli/actions/input_set.py
"""Core input set management actions."""

from typing import Any

from nextmv.cloud import Application, Client
from nextmv.cloud.input_set import ManagedInput


def list_input_sets(client: Client, app_id: str) -> list[dict[str, Any]]:
    """List all input sets for an application."""
    app = Application(client=client, id=app_id)
    return [s.to_dict() for s in app.list_input_sets()]


def get_input_set(client: Client, app_id: str, input_set_id: str) -> dict[str, Any]:
    """Get input set details."""
    app = Application(client=client, id=app_id)
    return app.input_set(input_set_id=input_set_id).to_dict()


def create_input_set(
    client: Client,
    app_id: str,
    input_set_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
    instance_id: str | None = None,
    maximum_runs: int | None = None,
    run_ids: list[str] | None = None,
    managed_input_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Create a new input set. Returns the input set dict."""
    app = Application(client=client, id=app_id)

    inputs = None
    if managed_input_ids:
        inputs = [ManagedInput(id=mid) for mid in managed_input_ids]

    return app.new_input_set(
        id=input_set_id,
        name=name,
        description=description,
        instance_id=instance_id,
        maximum_runs=maximum_runs,
        run_ids=run_ids,
        inputs=inputs,
    ).to_dict()


def update_input_set(
    client: Client,
    app_id: str,
    input_set_id: str,
    name: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Update an input set. Returns the updated input set dict."""
    app = Application(client=client, id=app_id)
    return app.update_input_set(
        id=input_set_id,
        name=name,
        description=description,
    ).to_dict()


def delete_input_set(client: Client, app_id: str, input_set_id: str) -> None:
    """Delete an input set."""
    app = Application(client=client, id=app_id)
    app.delete_input_set(input_set_id=input_set_id)
```

- [ ] **Step 2: Write tests, update CLI, update MCP, run all tests, commit**

Follow the standard pattern. Note `create_input_set` validation (exactly one of `instance_id`, `run_ids`, or `managed_input_ids`) stays in MCP wrapper since it's LLM-specific error messaging. The action function trusts its caller.

```bash
git commit -m "refactor: extract input_set actions, update CLI and MCP"
```

---

## Task 6: Extract secrets actions + tests

**Files:**
- Create: `nextmv/nextmv/cli/actions/secrets.py`
- Create: `nextmv/tests/cli/actions/test_secrets.py`
- Modify: `nextmv/nextmv/cli/cloud/secrets/*.py`
- Modify: `nextmv/nextmv/cli/mcp/tools/secrets.py`

- [ ] **Step 1: Write the action module**

```python
# nextmv/nextmv/cli/actions/secrets.py
"""Core secrets collection management actions."""

from typing import Any

from nextmv.cloud import Application, Client


def list_secrets_collections(client: Client, app_id: str) -> list[dict[str, Any]]:
    """List all secrets collections for an application."""
    app = Application(client=client, id=app_id)
    return [c.to_dict() for c in app.list_secrets_collections()]


def get_secrets_collection(
    client: Client, app_id: str, secrets_collection_id: str
) -> dict[str, Any]:
    """Get secrets collection details."""
    app = Application(client=client, id=app_id)
    return app.secrets_collection(
        secrets_collection_id=secrets_collection_id
    ).to_dict()


def create_secrets_collection(
    client: Client,
    app_id: str,
    secrets: list[dict[str, str]],
    secrets_collection_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Create a secrets collection. Returns the collection dict."""
    app = Application(client=client, id=app_id)
    return app.new_secrets_collection(
        secrets=secrets,
        id=secrets_collection_id,
        name=name,
        description=description,
    ).to_dict()


def delete_secrets_collection(
    client: Client, app_id: str, secrets_collection_id: str
) -> None:
    """Delete a secrets collection."""
    app = Application(client=client, id=app_id)
    app.delete_secrets_collection(
        secrets_collection_id=secrets_collection_id
    )
```

- [ ] **Step 2: Write tests, update CLI, update MCP, run all tests, commit**

```bash
git commit -m "refactor: extract secrets actions, update CLI and MCP"
```

---

## Task 7: Extract account and sso actions + tests

**Files:**
- Create: `nextmv/nextmv/cli/actions/account.py`
- Create: `nextmv/nextmv/cli/actions/sso.py`
- Create: `nextmv/tests/cli/actions/test_account.py`
- Modify: `nextmv/nextmv/cli/cloud/account/*.py`
- Modify: `nextmv/nextmv/cli/cloud/sso/domain/*.py`
- Modify: `nextmv/nextmv/cli/mcp/tools/account.py`
- Modify: `nextmv/nextmv/cli/mcp/tools/sso.py`

- [ ] **Step 1: Write the action modules**

```python
# nextmv/nextmv/cli/actions/account.py
"""Core account management actions."""

from typing import Any

from nextmv.cloud.account import Account
from nextmv.cloud.client import Client


def get_account(client: Client) -> dict[str, Any]:
    """Get account details."""
    return Account.get(client=client).to_dict()


def get_queue(client: Client) -> dict[str, Any]:
    """Get the account's run queue status."""
    account = Account.get(client=client)
    return account.queue().to_dict()
```

```python
# nextmv/nextmv/cli/actions/sso.py
"""Core SSO management actions."""

from nextmv.cloud.client import Client
from nextmv.cloud.sso import SSOConfiguration


def delete_domain(client: Client, domain: str) -> None:
    """Delete an SSO domain."""
    sso = SSOConfiguration.get(client=client)
    sso.delete_domain(domain=domain)
```

- [ ] **Step 2: Write tests, update CLI, update MCP, run all tests, commit**

```bash
git commit -m "refactor: extract account and sso actions, update CLI and MCP"
```

---

## Task 8: Extract managed_input actions + tests

**Files:**
- Create: `nextmv/nextmv/cli/actions/managed_input.py`
- Create: `nextmv/tests/cli/actions/test_managed_input.py`
- Modify: `nextmv/nextmv/cli/cloud/managed_input/*.py`
- Modify: `nextmv/nextmv/cli/mcp/tools/managed_input.py`

- [ ] **Step 1: Write the action module**

Read the current CLI and MCP implementations for managed_input fully before writing. The `create` action involves upload_url + upload_data which is more complex. Structure the action to handle both the metadata creation and data upload:

```python
# nextmv/nextmv/cli/actions/managed_input.py
"""Core managed input actions."""

from typing import Any

from nextmv.cloud import Application, Client


def list_managed_inputs(client: Client, app_id: str) -> list[dict[str, Any]]:
    """List all managed inputs for an application."""
    app = Application(client=client, id=app_id)
    return [m.to_dict() for m in app.list_managed_inputs()]


def get_managed_input(
    client: Client, app_id: str, managed_input_id: str
) -> dict[str, Any]:
    """Get managed input details."""
    app = Application(client=client, id=app_id)
    return app.managed_input(managed_input_id=managed_input_id).to_dict()


def create_managed_input(
    client: Client,
    app_id: str,
    data: Any,
    managed_input_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Create a managed input with uploaded data. Returns the managed input dict."""
    app = Application(client=client, id=app_id)
    upload_url = app.upload_url()
    app.upload_data(data=data, upload_url=upload_url)
    return app.new_managed_input(
        upload_id=upload_url.upload_id,
        id=managed_input_id,
        name=name,
        description=description,
    ).to_dict()


def delete_managed_input(
    client: Client, app_id: str, managed_input_id: str
) -> None:
    """Delete a managed input."""
    app = Application(client=client, id=app_id)
    app.delete_managed_input(managed_input_id=managed_input_id)
```

- [ ] **Step 2: Write tests, update CLI, update MCP, run all tests, commit**

Note: Read the current MCP `managed_input.py` and CLI `managed_input/create.py` before editing — the upload flow may differ between them.

```bash
git commit -m "refactor: extract managed_input actions, update CLI and MCP"
```

---

## Task 9: Extract batch actions + tests

**Files:**
- Create: `nextmv/nextmv/cli/actions/batch.py`
- Create: `nextmv/tests/cli/actions/test_batch.py`
- Modify: `nextmv/nextmv/cli/cloud/batch/*.py`
- Modify: `nextmv/nextmv/cli/mcp/tools/batch.py`

- [ ] **Step 1: Write the action module**

```python
# nextmv/nextmv/cli/actions/batch.py
"""Core batch experiment actions."""

from typing import Any

from nextmv.cloud import Application, Client


def list_batches(client: Client, app_id: str) -> list[dict[str, Any]]:
    """List all batch experiments for an application."""
    app = Application(client=client, id=app_id)
    return [b.to_dict() for b in app.list_batch_experiments()]


def get_batch(client: Client, app_id: str, batch_id: str) -> dict[str, Any]:
    """Get batch experiment details."""
    app = Application(client=client, id=app_id)
    return app.batch_experiment(batch_id=batch_id).to_dict()


def batch_metadata(client: Client, app_id: str, batch_id: str) -> dict[str, Any]:
    """Get batch experiment metadata."""
    app = Application(client=client, id=app_id)
    return app.batch_experiment_metadata(batch_id=batch_id).to_dict()


def create_batch(
    client: Client,
    app_id: str,
    input_set_id: str,
    name: str | None = None,
    description: str | None = None,
    option_sets: dict[str, dict[str, str]] | None = None,
) -> str:
    """Create a batch experiment. Returns the batch experiment ID."""
    app = Application(client=client, id=app_id)
    return app.new_batch_experiment(
        input_set_id=input_set_id,
        name=name,
        description=description,
        option_sets=option_sets,
    )


def delete_batch(client: Client, app_id: str, batch_id: str) -> None:
    """Delete a batch experiment."""
    app = Application(client=client, id=app_id)
    app.delete_batch_experiment(batch_id=batch_id)
```

- [ ] **Step 2: Write tests, update CLI, update MCP, run all tests, commit**

```bash
git commit -m "refactor: extract batch actions, update CLI and MCP"
```

---

## Task 10: Extract acceptance actions + tests

**Files:**
- Create: `nextmv/nextmv/cli/actions/acceptance.py`
- Create: `nextmv/tests/cli/actions/test_acceptance.py`
- Modify: `nextmv/nextmv/cli/cloud/acceptance/*.py`
- Modify: `nextmv/nextmv/cli/mcp/tools/acceptance.py`

- [ ] **Step 1: Write the action module**

```python
# nextmv/nextmv/cli/actions/acceptance.py
"""Core acceptance test actions."""

from typing import Any

from nextmv.cloud import Application, Client


def list_acceptance_tests(client: Client, app_id: str) -> list[dict[str, Any]]:
    """List all acceptance tests for an application."""
    app = Application(client=client, id=app_id)
    return [t.to_dict() for t in app.list_acceptance_tests()]


def get_acceptance_test(
    client: Client, app_id: str, acceptance_test_id: str
) -> dict[str, Any]:
    """Get acceptance test details."""
    app = Application(client=client, id=app_id)
    return app.acceptance_test(acceptance_test_id=acceptance_test_id).to_dict()


def create_acceptance_test(
    client: Client,
    app_id: str,
    candidate_instance_id: str,
    baseline_instance_id: str,
    metrics: list[dict[str, Any]],
    acceptance_test_id: str | None = None,
    name: str | None = None,
    input_set_id: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Create an acceptance test. Returns the test dict."""
    app = Application(client=client, id=app_id)
    return app.new_acceptance_test(
        candidate_instance_id=candidate_instance_id,
        baseline_instance_id=baseline_instance_id,
        metrics=metrics,
        id=acceptance_test_id,
        name=name,
        input_set_id=input_set_id,
        description=description,
    ).to_dict()


def delete_acceptance_test(
    client: Client, app_id: str, acceptance_test_id: str
) -> None:
    """Delete an acceptance test."""
    app = Application(client=client, id=app_id)
    app.delete_acceptance_test(acceptance_test_id=acceptance_test_id)
```

- [ ] **Step 2: Write tests, update CLI, update MCP, run all tests, commit**

```bash
git commit -m "refactor: extract acceptance actions, update CLI and MCP"
```

---

## Task 11: Extract scenario actions + tests

**Files:**
- Create: `nextmv/nextmv/cli/actions/scenario.py`
- Create: `nextmv/tests/cli/actions/test_scenario.py`
- Modify: `nextmv/nextmv/cli/cloud/scenario/*.py`
- Modify: `nextmv/nextmv/cli/mcp/tools/scenario.py`

Important: Move `_build_scenario()` from `mcp/tools/scenario.py` into the action module — it's pure data transformation, not MCP-specific.

- [ ] **Step 1: Write the action module**

```python
# nextmv/nextmv/cli/actions/scenario.py
"""Core scenario test actions."""

from typing import Any

from nextmv.cloud import Application, Client
from nextmv.cloud.scenario import (
    Scenario,
    ScenarioConfiguration,
    ScenarioInput,
    ScenarioInputType,
)


def build_scenario(s: dict[str, Any]) -> Scenario:
    """Convert a plain dict into a Scenario dataclass instance.

    Moved from mcp/tools/scenario.py — this is pure data transformation.
    """

    missing = [k for k in ("scenario_input", "instance_id") if k not in s]
    if missing:
        raise ValueError(f"scenario is missing required keys: {missing}")

    raw_input = s["scenario_input"]
    if "scenario_input_type" in raw_input:
        si = ScenarioInput(
            scenario_input_type=ScenarioInputType(raw_input["scenario_input_type"]),
            scenario_input_data=raw_input["scenario_input_data"],
        )
    elif "input_set_id" in raw_input:
        si = ScenarioInput(
            scenario_input_type=ScenarioInputType.INPUT_SET,
            scenario_input_data=raw_input["input_set_id"],
        )
    elif "managed_input_ids" in raw_input:
        si = ScenarioInput(
            scenario_input_type=ScenarioInputType.INPUT,
            scenario_input_data=raw_input["managed_input_ids"],
        )
    else:
        raise ValueError(
            "scenario_input must contain 'scenario_input_type' + "
            "'scenario_input_data', or 'input_set_id', or "
            f"'managed_input_ids'. Got: {raw_input}"
        )

    config = None
    raw_config = s.get("configuration")
    if isinstance(raw_config, list):
        for i, c in enumerate(raw_config):
            cfg_missing = [k for k in ("name", "values") if k not in c]
            if cfg_missing:
                raise ValueError(
                    f"configuration[{i}] is missing required keys: {cfg_missing}"
                )
        config = [
            ScenarioConfiguration(name=c["name"], values=c["values"])
            for c in raw_config
        ]
    elif isinstance(raw_config, dict):
        opts = raw_config.get("options", raw_config)
        config = [
            ScenarioConfiguration(
                name=k,
                values=v if isinstance(v, list) else [v],
            )
            for k, v in opts.items()
        ]

    return Scenario(
        scenario_input=si,
        instance_id=s["instance_id"],
        scenario_id=s.get("scenario_id"),
        configuration=config,
    )


def list_scenario_tests(client: Client, app_id: str) -> list[dict[str, Any]]:
    """List all scenario tests for an application."""
    app = Application(client=client, id=app_id)
    return [t.to_dict() for t in app.list_scenario_tests()]


def get_scenario_test(
    client: Client, app_id: str, scenario_test_id: str
) -> dict[str, Any]:
    """Get scenario test details."""
    app = Application(client=client, id=app_id)
    return app.scenario_test(scenario_test_id=scenario_test_id).to_dict()


def create_scenario_test(
    client: Client,
    app_id: str,
    scenarios: list[dict[str, Any]],
    scenario_test_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
    repetitions: int = 0,
    content_type: str | None = None,
) -> str:
    """Create a scenario test. Returns the test ID."""
    app = Application(client=client, id=app_id)
    scenario_objs = [build_scenario(s) for s in scenarios]
    return app.new_scenario_test(
        scenarios=scenario_objs,
        id=scenario_test_id,
        name=name,
        description=description,
        repetitions=repetitions,
        content_type=content_type,
    )


def delete_scenario_test(
    client: Client, app_id: str, scenario_test_id: str
) -> None:
    """Delete a scenario test."""
    app = Application(client=client, id=app_id)
    app.delete_scenario_test(scenario_test_id=scenario_test_id)
```

- [ ] **Step 2: Write tests** — include tests for `build_scenario()` with valid input, missing keys, different input types (input_set, managed_input, explicit type), and configuration parsing (list and dict shorthand).

- [ ] **Step 3: Update CLI, update MCP, run all tests, commit**

MCP `scenario.py` should delete its local `_build_scenario()` and `_cloud_create_scenario_test_impl()`, importing from actions instead.

```bash
git commit -m "refactor: extract scenario actions, update CLI and MCP"
```

---

## Task 12: Extract ensemble actions + tests

**Files:**
- Create: `nextmv/nextmv/cli/actions/ensemble.py`
- Create: `nextmv/tests/cli/actions/test_ensemble.py`
- Modify: `nextmv/nextmv/cli/cloud/ensemble/*.py`
- Modify: `nextmv/nextmv/cli/mcp/tools/ensemble.py`

Move `_parse_evaluation_rule()` and `_build_ensemble_run_config()` from MCP tools into the action module.

- [ ] **Step 1: Write the action module**

```python
# nextmv/nextmv/cli/actions/ensemble.py
"""Core ensemble definition and run actions."""

from typing import Any

from nextmv.cloud import Application, Client
from nextmv.cloud.ensemble import (
    EvaluationRule,
    RuleObjective,
    RuleTolerance,
    RuleToleranceType,
    RunGroup,
)
from nextmv.polling import PollingOptions, default_polling_options
from nextmv.run import RunConfiguration, RunType, RunTypeConfiguration


def parse_evaluation_rule(r: dict[str, Any], index: int) -> EvaluationRule:
    """Parse a single evaluation rule dict into an EvaluationRule.

    Raises ValueError on invalid input.
    """

    raw_tol = r.get("tolerance")
    if isinstance(raw_tol, dict):
        tol = RuleTolerance(
            value=raw_tol["value"],
            type=RuleToleranceType(raw_tol.get("type", "relative")),
        )
    else:
        tol = RuleTolerance(
            value=float(raw_tol) if raw_tol is not None else 0.0,
            type=RuleToleranceType.RELATIVE,
        )

    raw_obj = r["objective"]
    obj_map = {"min": "minimize", "max": "maximize"}
    mapped = obj_map.get(raw_obj, raw_obj)
    valid_objectives = {o.value for o in RuleObjective}
    if mapped not in valid_objectives:
        raise ValueError(
            f"rules[{index}] has unknown objective '{raw_obj}'; "
            f"use one of: {sorted(valid_objectives)} "
            f"(or shorthand 'min'/'max')."
        )
    objective = RuleObjective(mapped)

    return EvaluationRule(
        id=r["id"],
        statistics_path=r["statistics_path"],
        objective=objective,
        tolerance=tol,
        index=r.get("index", 0),
    )


def list_ensembles(client: Client, app_id: str) -> list[dict[str, Any]]:
    """List all ensemble definitions for an application."""
    app = Application(client=client, id=app_id)
    return [e.to_dict() for e in app.list_ensemble_definitions()]


def get_ensemble(client: Client, app_id: str, ensemble_id: str) -> dict[str, Any]:
    """Get ensemble definition details."""
    app = Application(client=client, id=app_id)
    return app.ensemble_definition(
        ensemble_definition_id=ensemble_id
    ).to_dict()


def create_ensemble(
    client: Client,
    app_id: str,
    run_groups: list[dict[str, Any]],
    rules: list[dict[str, Any]],
    ensemble_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Create an ensemble definition. Returns the ensemble dict."""
    app = Application(client=client, id=app_id)
    run_group_objs = [RunGroup.from_dict(rg) for rg in run_groups]
    rule_objs = [parse_evaluation_rule(r, i) for i, r in enumerate(rules)]
    return app.new_ensemble_definition(
        run_groups=run_group_objs,
        rules=rule_objs,
        id=ensemble_id,
        name=name,
        description=description,
    ).to_dict()


def delete_ensemble(client: Client, app_id: str, ensemble_id: str) -> None:
    """Delete an ensemble definition."""
    app = Application(client=client, id=app_id)
    app.delete_ensemble_definition(ensemble_definition_id=ensemble_id)


def build_ensemble_run_config(
    ensemble_id: str,
    content_format: str | None = None,
) -> RunConfiguration:
    """Build a RunConfiguration for an ensemble run."""

    from nextmv.cli.mcp.tools._helpers import _build_run_configuration

    config = _build_run_configuration(content_format) or RunConfiguration()
    config.run_type = RunTypeConfiguration(
        run_type=RunType.ENSEMBLE,
        definition_id=ensemble_id,
    )
    return config


def ensemble_run_with_result(
    client: Client,
    app_id: str,
    ensemble_id: str,
    input: dict[str, Any] | None = None,
    input_dir_path: str | None = None,
    content_format: str | None = None,
    run_options: dict[str, str] | None = None,
    managed_input_id: str | None = None,
    polling_options: PollingOptions | None = None,
) -> dict[str, Any]:
    """Run an ensemble and wait for the result. Returns the result dict."""
    app = Application(client=client, id=app_id)
    config = build_ensemble_run_config(ensemble_id, content_format)
    result = app.new_run_with_result(
        input=input,
        input_dir_path=input_dir_path,
        configuration=config,
        run_options=run_options or {},
        polling_options=polling_options or default_polling_options(),
        managed_input_id=managed_input_id,
    )
    return result.to_dict()


def ensemble_run_submit(
    client: Client,
    app_id: str,
    ensemble_id: str,
    input: dict[str, Any] | None = None,
    input_dir_path: str | None = None,
    content_format: str | None = None,
    run_options: dict[str, str] | None = None,
    managed_input_id: str | None = None,
) -> str:
    """Submit an ensemble run without waiting. Returns the run ID."""
    app = Application(client=client, id=app_id)
    config = build_ensemble_run_config(ensemble_id, content_format)
    return app.new_run(
        input=input,
        input_dir_path=input_dir_path,
        configuration=config,
        options=run_options or {},
        managed_input_id=managed_input_id,
    )
```

- [ ] **Step 2: Write tests** — include tests for `parse_evaluation_rule()` (valid, shorthand min/max, invalid objective, tolerance dict vs float).

- [ ] **Step 3: Update CLI, update MCP, run all tests, commit**

MCP `ensemble.py` should delete `_cloud_create_ensemble_impl()`, `_parse_evaluation_rule()`, and `_build_ensemble_run_config()`, importing from actions instead.

```bash
git commit -m "refactor: extract ensemble actions, update CLI and MCP"
```

---

## Task 13: Extract shadow actions + tests

**Files:**
- Create: `nextmv/nextmv/cli/actions/shadow.py`
- Create: `nextmv/tests/cli/actions/test_shadow.py`
- Modify: `nextmv/nextmv/cli/cloud/shadow/*.py`
- Modify: `nextmv/nextmv/cli/mcp/tools/shadow.py`

- [ ] **Step 1: Write the action module**

```python
# nextmv/nextmv/cli/actions/shadow.py
"""Core shadow test actions."""

from typing import Any

from nextmv.cloud import Application, Client, StopIntent


def list_shadow_tests(client: Client, app_id: str) -> list[dict[str, Any]]:
    """List all shadow tests for an application."""
    app = Application(client=client, id=app_id)
    return [t.to_dict() for t in app.list_shadow_tests()]


def get_shadow_test(
    client: Client, app_id: str, shadow_test_id: str
) -> dict[str, Any]:
    """Get shadow test details."""
    app = Application(client=client, id=app_id)
    return app.shadow_test(shadow_test_id=shadow_test_id).to_dict()


def create_shadow_test(
    client: Client,
    app_id: str,
    comparisons: dict[str, list[str]],
    termination_events: dict[str, Any],
    shadow_test_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
    start_events: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a shadow test. Returns the test dict."""
    app = Application(client=client, id=app_id)
    return app.new_shadow_test(
        comparisons=comparisons,
        termination_events=termination_events,
        shadow_test_id=shadow_test_id,
        name=name,
        description=description,
        start_events=start_events,
    ).to_dict()


def start_shadow_test(client: Client, app_id: str, shadow_test_id: str) -> None:
    """Start a shadow test."""
    app = Application(client=client, id=app_id)
    app.start_shadow_test(shadow_test_id=shadow_test_id)


def stop_shadow_test(
    client: Client, app_id: str, shadow_test_id: str, intent: str = "cancel"
) -> None:
    """Stop a shadow test."""
    app = Application(client=client, id=app_id)
    app.stop_shadow_test(
        shadow_test_id=shadow_test_id,
        intent=StopIntent(intent),
    )


def delete_shadow_test(client: Client, app_id: str, shadow_test_id: str) -> None:
    """Delete a shadow test."""
    app = Application(client=client, id=app_id)
    app.delete_shadow_test(shadow_test_id=shadow_test_id)
```

- [ ] **Step 2: Write tests, update CLI, update MCP, run all tests, commit**

```bash
git commit -m "refactor: extract shadow actions, update CLI and MCP"
```

---

## Task 14: Extract switchback actions + tests

**Files:**
- Create: `nextmv/nextmv/cli/actions/switchback.py`
- Create: `nextmv/tests/cli/actions/test_switchback.py`
- Modify: `nextmv/nextmv/cli/cloud/switchback/*.py`
- Modify: `nextmv/nextmv/cli/mcp/tools/switchback.py`

- [ ] **Step 1: Write the action module**

```python
# nextmv/nextmv/cli/actions/switchback.py
"""Core switchback test actions."""

from typing import Any

from nextmv.cloud import Application, Client, StopIntent, TestComparisonSingle


def list_switchback_tests(client: Client, app_id: str) -> list[dict[str, Any]]:
    """List all switchback tests for an application."""
    app = Application(client=client, id=app_id)
    return [t.to_dict() for t in app.list_switchback_tests()]


def get_switchback_test(
    client: Client, app_id: str, switchback_test_id: str
) -> dict[str, Any]:
    """Get switchback test details."""
    app = Application(client=client, id=app_id)
    return app.switchback_test(switchback_test_id=switchback_test_id).to_dict()


def create_switchback_test(
    client: Client,
    app_id: str,
    baseline_instance_id: str,
    candidate_instance_id: str,
    unit_duration_minutes: float,
    units: int,
    switchback_test_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Create a switchback test. Returns the test dict."""
    app = Application(client=client, id=app_id)
    comparison = TestComparisonSingle(
        baseline_instance_id=baseline_instance_id,
        candidate_instance_id=candidate_instance_id,
    )
    return app.new_switchback_test(
        comparison=comparison,
        unit_duration_minutes=unit_duration_minutes,
        units=units,
        switchback_test_id=switchback_test_id,
        name=name,
        description=description,
    ).to_dict()


def start_switchback_test(
    client: Client, app_id: str, switchback_test_id: str
) -> None:
    """Start a switchback test."""
    app = Application(client=client, id=app_id)
    app.start_switchback_test(switchback_test_id=switchback_test_id)


def stop_switchback_test(
    client: Client, app_id: str, switchback_test_id: str, intent: str = "cancel"
) -> None:
    """Stop a switchback test."""
    app = Application(client=client, id=app_id)
    app.stop_switchback_test(
        switchback_test_id=switchback_test_id,
        intent=StopIntent(intent),
    )


def delete_switchback_test(
    client: Client, app_id: str, switchback_test_id: str
) -> None:
    """Delete a switchback test."""
    app = Application(client=client, id=app_id)
    app.delete_switchback_test(switchback_test_id=switchback_test_id)
```

- [ ] **Step 2: Write tests, update CLI, update MCP, run all tests, commit**

```bash
git commit -m "refactor: extract switchback actions, update CLI and MCP"
```

---

## Task 15: Extract run actions + tests (complex)

**Files:**
- Create: `nextmv/nextmv/cli/actions/run.py`
- Create: `nextmv/tests/cli/actions/test_run.py`
- Modify: `nextmv/nextmv/cli/cloud/run/create.py`
- Modify: `nextmv/nextmv/cli/cloud/run/cancel.py`
- Modify: `nextmv/nextmv/cli/cloud/run/list.py`
- Modify: `nextmv/nextmv/cli/cloud/run/metadata.py`
- Modify: `nextmv/nextmv/cli/cloud/run/get.py`
- Modify: `nextmv/nextmv/cli/cloud/run/input.py`
- Modify: `nextmv/nextmv/cli/cloud/run/logs.py`
- Modify: `nextmv/nextmv/cli/mcp/tools/run.py`

This is the most complex domain. The CLI has stdin/tar/wait/tail logic. The MCP has caching. The action layer captures the common SDK calls.

- [ ] **Step 1: Write the action module**

```python
# nextmv/nextmv/cli/actions/run.py
"""Core run management actions.

These functions handle the common SDK calls. CLI-specific concerns (stdin,
tar detection, --wait/--tail) and MCP-specific concerns (caching to
~/.nextmv/runs/) stay in their respective wrappers.
"""

from typing import Any

from nextmv.cloud import Application, Client
from nextmv.polling import PollingOptions, default_polling_options
from nextmv.run import RunConfiguration
from nextmv.status import StatusV2


def submit_run(
    app: Application,
    input: Any | None = None,
    input_dir_path: str | None = None,
    configuration: RunConfiguration | None = None,
    instance_id: str | None = None,
    options: dict[str, str] | None = None,
    managed_input_id: str | None = None,
    name: str | None = None,
    description: str | None = None,
    upload_id: str | None = None,
) -> str:
    """Submit a run. Returns the run ID."""
    return app.new_run(
        input=input,
        input_dir_path=input_dir_path,
        configuration=configuration,
        instance_id=instance_id,
        options=options or {},
        managed_input_id=managed_input_id,
        name=name,
        description=description,
        upload_id=upload_id,
    )


def submit_run_with_result(
    app: Application,
    input: Any | None = None,
    input_dir_path: str | None = None,
    configuration: RunConfiguration | None = None,
    instance_id: str | None = None,
    options: dict[str, str] | None = None,
    managed_input_id: str | None = None,
    polling_options: PollingOptions | None = None,
    output_dir_path: str | None = None,
):
    """Submit a run and poll until complete. Returns the RunResult."""
    return app.new_run_with_result(
        input=input,
        input_dir_path=input_dir_path,
        configuration=configuration,
        instance_id=instance_id,
        run_options=options or {},
        polling_options=polling_options or default_polling_options(),
        managed_input_id=managed_input_id,
        output_dir_path=output_dir_path,
    )


def run_metadata(app: Application, run_id: str) -> dict[str, Any]:
    """Get run status and metadata."""
    return app.run_metadata(run_id=run_id).to_dict()


def run_result(app: Application, run_id: str, output_dir_path: str | None = None):
    """Fetch the result of a completed run. Returns the RunResult."""
    return app.run_result(run_id=run_id, output_dir_path=output_dir_path)


def run_input(app: Application, run_id: str, output_dir_path: str | None = None):
    """Fetch the input data for a run."""
    return app.run_input(run_id=run_id, output_dir_path=output_dir_path)


def run_logs(app: Application, run_id: str):
    """Fetch log snapshot for a run."""
    return app.run_logs(run_id=run_id)


def cancel_run(app: Application, run_id: str) -> None:
    """Cancel a queued or running run."""
    app.cancel_run(run_id=run_id)


def list_runs(
    app: Application, status: str | None = None
) -> list[dict[str, Any]]:
    """List runs, optionally filtered by status."""
    status_filter = StatusV2(status) if status else None
    return [r.to_dict() for r in app.list_runs(status=status_filter)]
```

- [ ] **Step 2: Write tests for the action functions**

Mock `Application` and test each function. For `submit_run_with_result`, verify it passes polling_options through.

- [ ] **Step 3: Update CLI run commands to use actions**

Read each CLI run command file fully before editing. The key changes:
- `cli/cloud/run/create.py`: Replace `cloud_app.new_run(...)` with `submit_run(cloud_app, ...)`. The stdin/tar/upload handling stays in the CLI.
- `cli/cloud/run/cancel.py`: Replace `cloud_app.cancel_run(...)` with `cancel_run(cloud_app, ...)`.
- `cli/cloud/run/list.py`: Replace `cloud_app.list_runs(...)` with `list_runs(cloud_app, ...)`.
- `cli/cloud/run/metadata.py`: Replace `cloud_app.run_metadata(...)` with `run_metadata(cloud_app, ...)`.
- Others: similar pattern.

- [ ] **Step 4: Update MCP tools to use actions**

MCP `run.py` should delete `_cloud_run_impl`, `_cloud_list_runs_impl`, `_cloud_run_result_impl`, `_cloud_run_input_impl`, `_cloud_run_logs_impl`, `_cloud_poll_run_logs_impl`, replacing them with calls to action functions. The caching logic (saving to `~/.nextmv/runs/`) stays in the MCP wrappers.

- [ ] **Step 5: Run all tests, commit**

```bash
git commit -m "refactor: extract run actions, update CLI and MCP"
```

---

## Task 16: Extract community and local actions + tests

**Files:**
- Create: `nextmv/nextmv/cli/actions/community.py`
- Create: `nextmv/nextmv/cli/actions/local.py`
- Create: `nextmv/tests/cli/actions/test_community.py`
- Create: `nextmv/tests/cli/actions/test_local.py`
- Modify: `nextmv/nextmv/cli/mcp/tools/community.py`
- Modify: `nextmv/nextmv/cli/mcp/tools/local.py`

Read the current community and local CLI commands and MCP tools fully before writing actions. Local is complex — it involves file-based run management. Extract what's shared between CLI and MCP, leave file-specific I/O in the wrappers.

- [ ] **Step 1: Write the action modules**
- [ ] **Step 2: Write tests**
- [ ] **Step 3: Update CLI and MCP**
- [ ] **Step 4: Run all tests, commit**

```bash
git commit -m "refactor: extract community and local actions, update CLI and MCP"
```

---

## Task 17: Move _build_run_configuration and _validate_content_format to actions

**Files:**
- Create: `nextmv/nextmv/cli/actions/config.py`
- Modify: `nextmv/nextmv/cli/mcp/tools/_helpers.py`
- Modify: `nextmv/nextmv/cli/actions/ensemble.py`

The `_build_run_configuration()` and `_validate_content_format()` functions in `_helpers.py` are pure data transformation used by multiple action modules. Move them to a shared config module.

- [ ] **Step 1: Create the config action module**

```python
# nextmv/nextmv/cli/actions/config.py
"""Shared configuration building utilities."""

from nextmv.input import InputFormat
from nextmv.run import Format, FormatInput, RunConfiguration

_VALID_CONTENT_FORMATS = {f.value for f in InputFormat}


def validate_content_format(content_format: str) -> None:
    """Raise ValueError if content_format is not a recognised value."""
    if content_format not in _VALID_CONTENT_FORMATS:
        raise ValueError(
            f"Invalid content_format '{content_format}'. "
            f"Allowed values: {sorted(_VALID_CONTENT_FORMATS)}"
        )


def build_run_configuration(content_format: str | None) -> RunConfiguration | None:
    """Build a RunConfiguration for the given content format string, or None."""
    if content_format is None:
        return None
    validate_content_format(content_format)
    config = RunConfiguration()
    config.format = Format(
        format_input=FormatInput(input_type=InputFormat(content_format)),
    )
    return config
```

- [ ] **Step 2: Update _helpers.py to import from actions**

Replace `_build_run_configuration` and `_validate_content_format` in `_helpers.py` with imports from `nextmv.cli.actions.config`. Keep backward-compatible aliases if other code imports from `_helpers`.

- [ ] **Step 3: Update ensemble.py action to use actions.config**

Replace the `_helpers._build_run_configuration` call in `ensemble.py` action with a direct import from `actions.config`.

- [ ] **Step 4: Run all tests, commit**

```bash
git commit -m "refactor: move run configuration utilities to actions/config"
```

---

## Task 18: Split MCP tests by domain

**Files:**
- Create: `nextmv/tests/cli/mcp/__init__.py`
- Create: `nextmv/tests/cli/mcp/test_serve.py`
- Create: `nextmv/tests/cli/mcp/test_tools.py`
- Create: `nextmv/tests/cli/mcp/test_client.py`
- Create: `nextmv/tests/cli/mcp/test_helpers.py`
- Create: `nextmv/tests/cli/mcp/test_profiles.py`
- Create: `nextmv/tests/cli/mcp/test_run.py`
- Create: `nextmv/tests/cli/mcp/test_ensemble.py`
- Create: `nextmv/tests/cli/mcp/test_visuals.py`
- Create: `nextmv/tests/cli/mcp/test_content_type.py`
- Delete: `nextmv/tests/cli/test_mcp.py`

- [ ] **Step 1: Create the mcp test package**

```bash
mkdir -p nextmv/tests/cli/mcp
touch nextmv/tests/cli/mcp/__init__.py
```

- [ ] **Step 2: Split test classes into domain files**

Move each class from `test_mcp.py` to its new file:

| Class | Target file |
|-------|------------|
| `TestMCPServeCommand` | `test_serve.py` |
| `TestMCPOptionalDependency` | `test_serve.py` |
| `TestMCPServerTools` | `test_tools.py` |
| `TestGetClient` | `test_client.py` |
| `TestProfileSessionIsolation` | `test_client.py` |
| `TestSaveToFile` | `test_helpers.py` |
| `TestHelperFunctions` | `test_helpers.py` |
| `TestProfiles` | `test_profiles.py` |
| `TestBugFixes` | `test_run.py` |
| `TestMultiFileRunSupport` | `test_run.py` |
| `TestCloudRunCache` | `test_run.py` |
| `TestEnsembleRunTools` | `test_ensemble.py` |
| `TestVisualGenerationWarning` | `test_visuals.py` |
| `TestSDKContentType` | `test_content_type.py` |

Each file needs its own imports. Copy the shared helpers (`_strip_ansi`, `_ANSI_RE`) into a `conftest.py` or into each file that uses them.

- [ ] **Step 3: Run all tests from the new locations**

Run: `cd nextmv && python -m pytest tests/cli/mcp/ -v`
Expected: All tests PASS.

- [ ] **Step 4: Verify total test count matches**

Run: `cd nextmv && python -m pytest tests/cli/mcp/ --co -q | tail -1`
Compare with: `cd nextmv && python -m pytest tests/cli/test_mcp.py --co -q | tail -1`
Expected: Same number of tests.

- [ ] **Step 5: Delete the old monolithic test file**

```bash
rm nextmv/tests/cli/test_mcp.py
```

- [ ] **Step 6: Run the full test suite**

Run: `cd nextmv && python -m pytest tests/ -v`
Expected: All tests PASS. No regressions.

- [ ] **Step 7: Commit**

```bash
git add nextmv/tests/cli/mcp/ && git rm nextmv/tests/cli/test_mcp.py
git commit -m "refactor: split monolithic MCP tests into domain-specific files"
```

---

## Task 19: Final cleanup and verification

- [ ] **Step 1: Remove unused imports from MCP tool files**

After refactoring, many MCP tool files may still import SDK classes they no longer use directly (now imported via actions). Clean up unused imports in all `cli/mcp/tools/*.py` files.

- [ ] **Step 2: Remove unused imports from CLI command files**

Similarly clean up CLI command files that no longer directly import SDK classes.

- [ ] **Step 3: Run the full test suite**

Run: `cd nextmv && python -m pytest tests/ -v`
Expected: All tests PASS.

- [ ] **Step 4: Run linting if configured**

Run: `cd nextmv && ruff check nextmv/cli/actions/ nextmv/cli/mcp/tools/ nextmv/cli/cloud/`
Expected: No errors.

- [ ] **Step 5: Commit**

```bash
git add -u
git commit -m "refactor: clean up unused imports after actions extraction"
```
