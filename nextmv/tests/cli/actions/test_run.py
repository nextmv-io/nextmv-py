"""Tests for nextmv.cli.actions.run."""

import unittest
from unittest.mock import MagicMock, patch


class TestSubmitRun(unittest.TestCase):
    @patch("nextmv.cli.actions.run.Application")
    def test_returns_run_id(self, mock_app_cls):
        app = MagicMock()
        app.new_run.return_value = "run-123"
        mock_app_cls.return_value = app

        from nextmv.cli.actions.run import submit_run

        client = MagicMock()
        result = submit_run(client, app_id="a1", input={"key": "value"}, instance_id="latest")

        mock_app_cls.assert_called_once_with(client=client, id="a1")
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

    @patch("nextmv.cli.actions.run.Application")
    def test_options_defaults_to_empty_dict(self, mock_app_cls):
        app = MagicMock()
        app.new_run.return_value = "run-456"
        mock_app_cls.return_value = app

        from nextmv.cli.actions.run import submit_run

        submit_run(MagicMock(), app_id="a1")

        call_kwargs = app.new_run.call_args.kwargs
        self.assertEqual(call_kwargs["options"], {})

    @patch("nextmv.cli.actions.run.Application")
    def test_passes_all_params(self, mock_app_cls):
        app = MagicMock()
        app.new_run.return_value = "run-789"
        mock_app_cls.return_value = app
        config = MagicMock()

        from nextmv.cli.actions.run import submit_run

        result = submit_run(
            MagicMock(),
            app_id="a1",
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
    @patch("nextmv.cli.actions.run.Application")
    def test_returns_run_result(self, mock_app_cls):
        app = MagicMock()
        mock_result = MagicMock()
        app.new_run_with_result.return_value = mock_result
        mock_app_cls.return_value = app

        from nextmv.cli.actions.run import submit_run_with_result

        result = submit_run_with_result(MagicMock(), app_id="a1", input={"key": "value"})

        self.assertEqual(result, mock_result)
        app.new_run_with_result.assert_called_once()

    @patch("nextmv.cli.actions.run.Application")
    def test_uses_default_polling_options_when_none(self, mock_app_cls):
        app = MagicMock()
        app.new_run_with_result.return_value = MagicMock()
        mock_app_cls.return_value = app

        from nextmv.cli.actions.run import submit_run_with_result

        submit_run_with_result(MagicMock(), app_id="a1", input={})

        call_kwargs = app.new_run_with_result.call_args.kwargs
        self.assertIsNotNone(call_kwargs["polling_options"])

    @patch("nextmv.cli.actions.run.Application")
    def test_passes_custom_polling_options(self, mock_app_cls):
        app = MagicMock()
        app.new_run_with_result.return_value = MagicMock()
        mock_app_cls.return_value = app
        polling_opts = MagicMock()

        from nextmv.cli.actions.run import submit_run_with_result

        submit_run_with_result(MagicMock(), app_id="a1", input={}, polling_options=polling_opts)

        call_kwargs = app.new_run_with_result.call_args.kwargs
        self.assertEqual(call_kwargs["polling_options"], polling_opts)

    @patch("nextmv.cli.actions.run.Application")
    def test_options_defaults_to_empty_dict(self, mock_app_cls):
        app = MagicMock()
        app.new_run_with_result.return_value = MagicMock()
        mock_app_cls.return_value = app

        from nextmv.cli.actions.run import submit_run_with_result

        submit_run_with_result(MagicMock(), app_id="a1")

        call_kwargs = app.new_run_with_result.call_args.kwargs
        self.assertEqual(call_kwargs["run_options"], {})

    @patch("nextmv.cli.actions.run.Application")
    def test_passes_output_dir_path(self, mock_app_cls):
        app = MagicMock()
        app.new_run_with_result.return_value = MagicMock()
        mock_app_cls.return_value = app

        from nextmv.cli.actions.run import submit_run_with_result

        submit_run_with_result(MagicMock(), app_id="a1", output_dir_path="/out/dir")

        call_kwargs = app.new_run_with_result.call_args.kwargs
        self.assertEqual(call_kwargs["output_dir_path"], "/out/dir")


class TestRunMetadata(unittest.TestCase):
    @patch("nextmv.cli.actions.run.Application")
    def test_returns_dict(self, mock_app_cls):
        app = MagicMock()
        mock_metadata = MagicMock()
        mock_metadata.to_dict.return_value = {"id": "run-1", "status": "succeeded"}
        app.run_metadata.return_value = mock_metadata
        mock_app_cls.return_value = app

        from nextmv.cli.actions.run import run_metadata

        result = run_metadata(MagicMock(), app_id="a1", run_id="run-1")

        app.run_metadata.assert_called_once_with(run_id="run-1")
        self.assertEqual(result, {"id": "run-1", "status": "succeeded"})


class TestRunResult(unittest.TestCase):
    @patch("nextmv.cli.actions.run.Application")
    def test_returns_run_result_object(self, mock_app_cls):
        app = MagicMock()
        mock_result = MagicMock()
        app.run_result.return_value = mock_result
        mock_app_cls.return_value = app

        from nextmv.cli.actions.run import run_result

        result = run_result(MagicMock(), app_id="a1", run_id="run-1")

        app.run_result.assert_called_once_with(run_id="run-1", output_dir_path=None)
        self.assertEqual(result, mock_result)

    @patch("nextmv.cli.actions.run.Application")
    def test_passes_output_dir_path(self, mock_app_cls):
        app = MagicMock()
        app.run_result.return_value = MagicMock()
        mock_app_cls.return_value = app

        from nextmv.cli.actions.run import run_result

        run_result(MagicMock(), app_id="a1", run_id="run-1", output_dir_path="/out/dir")

        app.run_result.assert_called_once_with(run_id="run-1", output_dir_path="/out/dir")


class TestRunInput(unittest.TestCase):
    @patch("nextmv.cli.actions.run.Application")
    def test_returns_input_data(self, mock_app_cls):
        app = MagicMock()
        app.run_input.return_value = {"key": "value"}
        mock_app_cls.return_value = app

        from nextmv.cli.actions.run import run_input

        result = run_input(MagicMock(), app_id="a1", run_id="run-1")

        app.run_input.assert_called_once_with(run_id="run-1", output_dir_path=None)
        self.assertEqual(result, {"key": "value"})

    @patch("nextmv.cli.actions.run.Application")
    def test_passes_output_dir_path(self, mock_app_cls):
        app = MagicMock()
        app.run_input.return_value = None
        mock_app_cls.return_value = app

        from nextmv.cli.actions.run import run_input

        run_input(MagicMock(), app_id="a1", run_id="run-1", output_dir_path="/some/dir")

        app.run_input.assert_called_once_with(run_id="run-1", output_dir_path="/some/dir")


class TestRunLogs(unittest.TestCase):
    @patch("nextmv.cli.actions.run.Application")
    def test_returns_logs_object(self, mock_app_cls):
        app = MagicMock()
        mock_logs = MagicMock()
        app.run_logs.return_value = mock_logs
        mock_app_cls.return_value = app

        from nextmv.cli.actions.run import run_logs

        result = run_logs(MagicMock(), app_id="a1", run_id="run-1")

        app.run_logs.assert_called_once_with(run_id="run-1")
        self.assertEqual(result, mock_logs)


class TestCancelRun(unittest.TestCase):
    @patch("nextmv.cli.actions.run.Application")
    def test_calls_cancel_run(self, mock_app_cls):
        app = MagicMock()
        mock_app_cls.return_value = app

        from nextmv.cli.actions.run import cancel_run

        cancel_run(MagicMock(), app_id="a1", run_id="run-1")

        app.cancel_run.assert_called_once_with(run_id="run-1")

    @patch("nextmv.cli.actions.run.Application")
    def test_returns_none(self, mock_app_cls):
        app = MagicMock()
        app.cancel_run.return_value = None
        mock_app_cls.return_value = app

        from nextmv.cli.actions.run import cancel_run

        result = cancel_run(MagicMock(), app_id="a1", run_id="run-1")

        self.assertIsNone(result)


class TestListRuns(unittest.TestCase):
    @patch("nextmv.cli.actions.run.Application")
    def test_returns_list_of_dicts(self, mock_app_cls):
        app = MagicMock()
        mock_run1 = MagicMock()
        mock_run1.to_dict.return_value = {"id": "run-1", "status": "succeeded"}
        mock_run2 = MagicMock()
        mock_run2.to_dict.return_value = {"id": "run-2", "status": "failed"}
        app.list_runs.return_value = [mock_run1, mock_run2]
        mock_app_cls.return_value = app

        from nextmv.cli.actions.run import list_runs

        result = list_runs(MagicMock(), app_id="a1")

        app.list_runs.assert_called_once_with(status=None)
        self.assertEqual(result, [
            {"id": "run-1", "status": "succeeded"},
            {"id": "run-2", "status": "failed"},
        ])

    @patch("nextmv.cli.actions.run.Application")
    def test_empty_list(self, mock_app_cls):
        app = MagicMock()
        app.list_runs.return_value = []
        mock_app_cls.return_value = app

        from nextmv.cli.actions.run import list_runs

        result = list_runs(MagicMock(), app_id="a1")

        self.assertEqual(result, [])

    @patch("nextmv.cli.actions.run.Application")
    def test_filters_by_status(self, mock_app_cls):
        app = MagicMock()
        mock_run = MagicMock()
        mock_run.to_dict.return_value = {"id": "run-1", "status": "succeeded"}
        app.list_runs.return_value = [mock_run]
        mock_app_cls.return_value = app

        from nextmv.cli.actions.run import list_runs
        from nextmv.status import StatusV2

        result = list_runs(MagicMock(), app_id="a1", status="succeeded")

        app.list_runs.assert_called_once_with(status=StatusV2("succeeded"))
        self.assertEqual(len(result), 1)

    @patch("nextmv.cli.actions.run.Application")
    def test_no_status_filter_passes_none(self, mock_app_cls):
        app = MagicMock()
        app.list_runs.return_value = []
        mock_app_cls.return_value = app

        from nextmv.cli.actions.run import list_runs

        list_runs(MagicMock(), app_id="a1", status=None)

        app.list_runs.assert_called_once_with(status=None)


class TestDeleteRun(unittest.TestCase):
    @patch("nextmv.cli.actions.run.Application")
    def test_calls_delete_run(self, mock_app_cls):
        app = MagicMock()
        mock_app_cls.return_value = app

        from nextmv.cli.actions.run import delete_run

        delete_run(MagicMock(), app_id="a1", run_id="run-1")

        app.delete_run.assert_called_once_with(run_id="run-1")

    @patch("nextmv.cli.actions.run.Application")
    def test_returns_none(self, mock_app_cls):
        app = MagicMock()
        app.delete_run.return_value = None
        mock_app_cls.return_value = app

        from nextmv.cli.actions.run import delete_run

        result = delete_run(MagicMock(), app_id="a1", run_id="run-1")

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
