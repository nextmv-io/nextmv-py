"""Tests for nextmv.cli.actions.run."""

import unittest
from unittest.mock import MagicMock


class TestSubmitRun(unittest.TestCase):
    def test_returns_run_id(self):
        app = MagicMock()
        app.new_run.return_value = "run-123"

        from nextmv.cli.actions.run import submit_run

        result = submit_run(app, input={"key": "value"}, instance_id="latest")

        app.new_run.assert_called_once_with(
            input={"key": "value"},
            input_dir_path=None,
            configuration=None,
            instance_id="latest",
            options={},
            managed_input_id=None,
            name=None,
            description=None,
            upload_id=None,
        )
        self.assertEqual(result, "run-123")

    def test_options_defaults_to_empty_dict(self):
        app = MagicMock()
        app.new_run.return_value = "run-456"

        from nextmv.cli.actions.run import submit_run

        submit_run(app)

        call_kwargs = app.new_run.call_args.kwargs
        self.assertEqual(call_kwargs["options"], {})

    def test_passes_all_params(self):
        app = MagicMock()
        app.new_run.return_value = "run-789"
        config = MagicMock()

        from nextmv.cli.actions.run import submit_run

        result = submit_run(
            app,
            input={"x": 1},
            input_dir_path="/some/dir",
            configuration=config,
            instance_id="inst-1",
            options={"solve.duration": "10s"},
            managed_input_id="mi-1",
            name="my run",
            description="desc",
            upload_id="up-1",
        )

        app.new_run.assert_called_once_with(
            input={"x": 1},
            input_dir_path="/some/dir",
            configuration=config,
            instance_id="inst-1",
            options={"solve.duration": "10s"},
            managed_input_id="mi-1",
            name="my run",
            description="desc",
            upload_id="up-1",
        )
        self.assertEqual(result, "run-789")


class TestSubmitRunWithResult(unittest.TestCase):
    def test_returns_run_result(self):
        app = MagicMock()
        mock_result = MagicMock()
        app.new_run_with_result.return_value = mock_result

        from nextmv.cli.actions.run import submit_run_with_result

        result = submit_run_with_result(app, input={"key": "value"})

        self.assertEqual(result, mock_result)
        app.new_run_with_result.assert_called_once()

    def test_uses_default_polling_options_when_none(self):
        app = MagicMock()
        app.new_run_with_result.return_value = MagicMock()

        from nextmv.cli.actions.run import submit_run_with_result

        submit_run_with_result(app, input={})

        call_kwargs = app.new_run_with_result.call_args.kwargs
        # polling_options should not be None (default was applied)
        self.assertIsNotNone(call_kwargs["polling_options"])

    def test_passes_custom_polling_options(self):
        app = MagicMock()
        app.new_run_with_result.return_value = MagicMock()
        polling_opts = MagicMock()

        from nextmv.cli.actions.run import submit_run_with_result

        submit_run_with_result(app, input={}, polling_options=polling_opts)

        call_kwargs = app.new_run_with_result.call_args.kwargs
        self.assertEqual(call_kwargs["polling_options"], polling_opts)

    def test_options_defaults_to_empty_dict(self):
        app = MagicMock()
        app.new_run_with_result.return_value = MagicMock()

        from nextmv.cli.actions.run import submit_run_with_result

        submit_run_with_result(app)

        call_kwargs = app.new_run_with_result.call_args.kwargs
        self.assertEqual(call_kwargs["run_options"], {})

    def test_passes_output_dir_path(self):
        app = MagicMock()
        app.new_run_with_result.return_value = MagicMock()

        from nextmv.cli.actions.run import submit_run_with_result

        submit_run_with_result(app, output_dir_path="/out/dir")

        call_kwargs = app.new_run_with_result.call_args.kwargs
        self.assertEqual(call_kwargs["output_dir_path"], "/out/dir")


class TestRunMetadata(unittest.TestCase):
    def test_returns_dict(self):
        app = MagicMock()
        mock_metadata = MagicMock()
        mock_metadata.to_dict.return_value = {"id": "run-1", "status": "succeeded"}
        app.run_metadata.return_value = mock_metadata

        from nextmv.cli.actions.run import run_metadata

        result = run_metadata(app, run_id="run-1")

        app.run_metadata.assert_called_once_with(run_id="run-1")
        self.assertEqual(result, {"id": "run-1", "status": "succeeded"})


class TestRunResult(unittest.TestCase):
    def test_returns_run_result_object(self):
        app = MagicMock()
        mock_result = MagicMock()
        app.run_result.return_value = mock_result

        from nextmv.cli.actions.run import run_result

        result = run_result(app, run_id="run-1")

        app.run_result.assert_called_once_with(run_id="run-1", output_dir_path=None)
        self.assertEqual(result, mock_result)

    def test_passes_output_dir_path(self):
        app = MagicMock()
        app.run_result.return_value = MagicMock()

        from nextmv.cli.actions.run import run_result

        run_result(app, run_id="run-1", output_dir_path="/out/dir")

        app.run_result.assert_called_once_with(run_id="run-1", output_dir_path="/out/dir")


class TestRunInput(unittest.TestCase):
    def test_returns_input_data(self):
        app = MagicMock()
        app.run_input.return_value = {"key": "value"}

        from nextmv.cli.actions.run import run_input

        result = run_input(app, run_id="run-1")

        app.run_input.assert_called_once_with(run_id="run-1", output_dir_path=None)
        self.assertEqual(result, {"key": "value"})

    def test_passes_output_dir_path(self):
        app = MagicMock()
        app.run_input.return_value = None

        from nextmv.cli.actions.run import run_input

        run_input(app, run_id="run-1", output_dir_path="/some/dir")

        app.run_input.assert_called_once_with(run_id="run-1", output_dir_path="/some/dir")


class TestRunLogs(unittest.TestCase):
    def test_returns_logs_object(self):
        app = MagicMock()
        mock_logs = MagicMock()
        app.run_logs.return_value = mock_logs

        from nextmv.cli.actions.run import run_logs

        result = run_logs(app, run_id="run-1")

        app.run_logs.assert_called_once_with(run_id="run-1")
        self.assertEqual(result, mock_logs)


class TestCancelRun(unittest.TestCase):
    def test_calls_cancel_run(self):
        app = MagicMock()

        from nextmv.cli.actions.run import cancel_run

        cancel_run(app, run_id="run-1")

        app.cancel_run.assert_called_once_with(run_id="run-1")

    def test_returns_none(self):
        app = MagicMock()
        app.cancel_run.return_value = None

        from nextmv.cli.actions.run import cancel_run

        result = cancel_run(app, run_id="run-1")

        self.assertIsNone(result)


class TestListRuns(unittest.TestCase):
    def test_returns_list_of_dicts(self):
        app = MagicMock()
        mock_run1 = MagicMock()
        mock_run1.to_dict.return_value = {"id": "run-1", "status": "succeeded"}
        mock_run2 = MagicMock()
        mock_run2.to_dict.return_value = {"id": "run-2", "status": "failed"}
        app.list_runs.return_value = [mock_run1, mock_run2]

        from nextmv.cli.actions.run import list_runs

        result = list_runs(app)

        app.list_runs.assert_called_once_with(status=None)
        self.assertEqual(result, [
            {"id": "run-1", "status": "succeeded"},
            {"id": "run-2", "status": "failed"},
        ])

    def test_empty_list(self):
        app = MagicMock()
        app.list_runs.return_value = []

        from nextmv.cli.actions.run import list_runs

        result = list_runs(app)

        self.assertEqual(result, [])

    def test_filters_by_status(self):
        app = MagicMock()
        mock_run = MagicMock()
        mock_run.to_dict.return_value = {"id": "run-1", "status": "succeeded"}
        app.list_runs.return_value = [mock_run]

        from nextmv.cli.actions.run import list_runs
        from nextmv.status import StatusV2

        result = list_runs(app, status="succeeded")

        app.list_runs.assert_called_once_with(status=StatusV2("succeeded"))
        self.assertEqual(len(result), 1)

    def test_no_status_filter_passes_none(self):
        app = MagicMock()
        app.list_runs.return_value = []

        from nextmv.cli.actions.run import list_runs

        list_runs(app, status=None)

        app.list_runs.assert_called_once_with(status=None)


class TestDeleteRun(unittest.TestCase):
    def test_calls_delete_run(self):
        app = MagicMock()

        from nextmv.cli.actions.run import delete_run

        delete_run(app, run_id="run-1")

        app.delete_run.assert_called_once_with(run_id="run-1")

    def test_returns_none(self):
        app = MagicMock()
        app.delete_run.return_value = None

        from nextmv.cli.actions.run import delete_run

        result = delete_run(app, run_id="run-1")

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
