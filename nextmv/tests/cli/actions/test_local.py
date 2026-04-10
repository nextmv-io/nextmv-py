"""Tests for nextmv.cli.actions.local."""

import unittest
from unittest.mock import MagicMock, patch


class TestNewLocalRun(unittest.TestCase):
    def test_returns_run_id(self):
        app = MagicMock()
        app.new_run.return_value = "local-run-123"

        from nextmv.cli.actions.local import new_local_run

        result = new_local_run(app, input={"key": "value"})

        app.new_run.assert_called_once_with(
            input={"key": "value"},
            input_dir_path=None,
            configuration=None,
            options=None,
            name=None,
            description=None,
        )
        self.assertEqual(result, "local-run-123")

    def test_passes_all_params(self):
        app = MagicMock()
        app.new_run.return_value = "local-run-456"
        config = MagicMock()

        from nextmv.cli.actions.local import new_local_run

        result = new_local_run(
            app,
            input={"x": 1},
            input_dir_path="/some/dir",
            configuration=config,
            options={"solve.duration": "10s"},
            name="my run",
            description="desc",
        )

        app.new_run.assert_called_once_with(
            input={"x": 1},
            input_dir_path="/some/dir",
            configuration=config,
            options={"solve.duration": "10s"},
            name="my run",
            description="desc",
        )
        self.assertEqual(result, "local-run-456")


class TestNewLocalRunWithResult(unittest.TestCase):
    def test_returns_run_result(self):
        app = MagicMock()
        mock_result = MagicMock()
        app.new_run_with_result.return_value = mock_result

        from nextmv.cli.actions.local import new_local_run_with_result

        result = new_local_run_with_result(app, input={"key": "value"})

        self.assertEqual(result, mock_result)
        app.new_run_with_result.assert_called_once()

    def test_uses_default_polling_options_when_none(self):
        app = MagicMock()
        app.new_run_with_result.return_value = MagicMock()

        from nextmv.cli.actions.local import new_local_run_with_result

        new_local_run_with_result(app, input={})

        call_kwargs = app.new_run_with_result.call_args.kwargs
        self.assertIsNotNone(call_kwargs["polling_options"])

    def test_passes_custom_polling_options(self):
        app = MagicMock()
        app.new_run_with_result.return_value = MagicMock()
        polling_opts = MagicMock()

        from nextmv.cli.actions.local import new_local_run_with_result

        new_local_run_with_result(app, input={}, polling_options=polling_opts)

        call_kwargs = app.new_run_with_result.call_args.kwargs
        self.assertEqual(call_kwargs["polling_options"], polling_opts)

    def test_passes_run_options(self):
        app = MagicMock()
        app.new_run_with_result.return_value = MagicMock()

        from nextmv.cli.actions.local import new_local_run_with_result

        new_local_run_with_result(app, run_options={"solve.duration": "5s"})

        call_kwargs = app.new_run_with_result.call_args.kwargs
        self.assertEqual(call_kwargs["run_options"], {"solve.duration": "5s"})


class TestLocalRunPollResult(unittest.TestCase):
    def test_returns_run_result(self):
        app = MagicMock()
        mock_result = MagicMock()
        app.run_result_with_polling.return_value = mock_result

        from nextmv.cli.actions.local import local_run_poll_result

        result = local_run_poll_result(app, run_id="run-1")

        self.assertEqual(result, mock_result)
        app.run_result_with_polling.assert_called_once()

    def test_uses_default_polling_options_when_none(self):
        app = MagicMock()
        app.run_result_with_polling.return_value = MagicMock()

        from nextmv.cli.actions.local import local_run_poll_result

        local_run_poll_result(app, run_id="run-1")

        call_kwargs = app.run_result_with_polling.call_args.kwargs
        self.assertIsNotNone(call_kwargs["polling_options"])


class TestLocalRunMetadata(unittest.TestCase):
    def test_returns_dict(self):
        app = MagicMock()
        mock_metadata = MagicMock()
        mock_metadata.to_dict.return_value = {"id": "run-1", "status": "succeeded"}
        app.run_metadata.return_value = mock_metadata

        from nextmv.cli.actions.local import local_run_metadata

        result = local_run_metadata(app, run_id="run-1")

        app.run_metadata.assert_called_once_with(run_id="run-1")
        self.assertEqual(result, {"id": "run-1", "status": "succeeded"})


class TestLocalListRuns(unittest.TestCase):
    def test_returns_list_of_dicts(self):
        app = MagicMock()
        mock_run1 = MagicMock()
        mock_run1.to_dict.return_value = {"id": "run-1", "status": "succeeded"}
        mock_run2 = MagicMock()
        mock_run2.to_dict.return_value = {"id": "run-2", "status": "failed"}
        app.list_runs.return_value = [mock_run1, mock_run2]

        from nextmv.cli.actions.local import local_list_runs

        result = local_list_runs(app)

        app.list_runs.assert_called_once_with(status=None)
        self.assertEqual(result, [
            {"id": "run-1", "status": "succeeded"},
            {"id": "run-2", "status": "failed"},
        ])

    def test_empty_list(self):
        app = MagicMock()
        app.list_runs.return_value = []

        from nextmv.cli.actions.local import local_list_runs

        result = local_list_runs(app)

        self.assertEqual(result, [])

    def test_filters_by_status(self):
        app = MagicMock()
        mock_run = MagicMock()
        mock_run.to_dict.return_value = {"id": "run-1", "status": "succeeded"}
        app.list_runs.return_value = [mock_run]

        from nextmv.cli.actions.local import local_list_runs
        from nextmv.status import StatusV2

        result = local_list_runs(app, status="succeeded")

        app.list_runs.assert_called_once_with(status=StatusV2("succeeded"))
        self.assertEqual(len(result), 1)


class TestLocalRunResult(unittest.TestCase):
    def test_returns_run_result_object(self):
        app = MagicMock()
        mock_result = MagicMock()
        app.run_result.return_value = mock_result

        from nextmv.cli.actions.local import local_run_result

        result = local_run_result(app, run_id="run-1")

        app.run_result.assert_called_once_with(run_id="run-1", output_dir_path=None)
        self.assertEqual(result, mock_result)

    def test_passes_output_dir_path(self):
        app = MagicMock()
        app.run_result.return_value = MagicMock()

        from nextmv.cli.actions.local import local_run_result

        local_run_result(app, run_id="run-1", output_dir_path="/out/dir")

        app.run_result.assert_called_once_with(run_id="run-1", output_dir_path="/out/dir")


class TestLocalRunInput(unittest.TestCase):
    def test_returns_input_data(self):
        app = MagicMock()
        app.run_input.return_value = {"key": "value"}

        from nextmv.cli.actions.local import local_run_input

        result = local_run_input(app, run_id="run-1")

        app.run_input.assert_called_once_with(run_id="run-1", output_dir_path=None)
        self.assertEqual(result, {"key": "value"})

    def test_passes_output_dir_path(self):
        app = MagicMock()
        app.run_input.return_value = None

        from nextmv.cli.actions.local import local_run_input

        local_run_input(app, run_id="run-1", output_dir_path="/some/dir")

        app.run_input.assert_called_once_with(run_id="run-1", output_dir_path="/some/dir")


class TestLocalRunLogs(unittest.TestCase):
    def test_returns_logs(self):
        app = MagicMock()
        app.run_logs.return_value = "some log output"

        from nextmv.cli.actions.local import local_run_logs

        result = local_run_logs(app, run_id="run-1")

        app.run_logs.assert_called_once_with(run_id="run-1")
        self.assertEqual(result, "some log output")


class TestLocalSync(unittest.TestCase):
    def test_calls_sync(self):
        app = MagicMock()
        target = MagicMock()

        from nextmv.cli.actions.local import local_sync

        local_sync(app=app, target=target)

        app.sync.assert_called_once_with(
            target=target,
            run_ids=None,
            instance_id=None,
            verbose=False,
            rich_print=False,
        )

    def test_passes_all_params(self):
        app = MagicMock()
        target = MagicMock()

        from nextmv.cli.actions.local import local_sync

        local_sync(
            app=app,
            target=target,
            run_ids=["run-1", "run-2"],
            instance_id="inst-1",
            verbose=True,
            rich_print=True,
        )

        app.sync.assert_called_once_with(
            target=target,
            run_ids=["run-1", "run-2"],
            instance_id="inst-1",
            verbose=True,
            rich_print=True,
        )

    def test_returns_none(self):
        app = MagicMock()
        target = MagicMock()
        app.sync.return_value = None

        from nextmv.cli.actions.local import local_sync

        result = local_sync(app=app, target=target)

        self.assertIsNone(result)


class TestManifestInit(unittest.TestCase):
    @patch("nextmv.cli.actions.local.initialize_manifest")
    def test_returns_path(self, mock_init):
        mock_init.return_value = "/some/dir/app.yaml"

        from nextmv.cli.actions.local import manifest_init

        result = manifest_init(manifest_type="python", content_format="json")

        self.assertEqual(result, "/some/dir/app.yaml")

    @patch("nextmv.cli.actions.local.initialize_manifest")
    def test_calls_with_correct_types(self, mock_init):
        mock_init.return_value = "/dir/app.yaml"

        from nextmv.cli.actions.local import manifest_init
        from nextmv.content_format import ContentFormat
        from nextmv.manifest import ManifestType

        manifest_init(manifest_type="go", content_format="multi-file", dirpath="/my/app")

        mock_init.assert_called_once_with(
            manifest_type=ManifestType("go"),
            content_format=ContentFormat("multi-file"),
            dirpath="/my/app",
        )

    @patch("nextmv.cli.actions.local.initialize_manifest")
    def test_uses_default_dirpath(self, mock_init):
        mock_init.return_value = "./app.yaml"

        from nextmv.cli.actions.local import manifest_init

        manifest_init(manifest_type="python", content_format="json")

        call_kwargs = mock_init.call_args.kwargs
        self.assertEqual(call_kwargs["dirpath"], ".")


if __name__ == "__main__":
    unittest.main()
