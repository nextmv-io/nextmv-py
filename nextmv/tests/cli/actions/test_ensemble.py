"""Tests for nextmv.cli.actions.ensemble."""

import unittest
from unittest.mock import MagicMock, patch


class TestParseEvaluationRule(unittest.TestCase):
    def test_parses_with_dict_tolerance(self):
        from nextmv.cli.actions.ensemble import parse_evaluation_rule

        r = {
            "id": "rule-1",
            "statistics_path": "$.result.value",
            "objective": "minimize",
            "tolerance": {"value": 0.1, "type": "relative"},
        }
        rule = parse_evaluation_rule(r, 0)
        self.assertEqual(rule.id, "rule-1")
        self.assertEqual(rule.statistics_path, "$.result.value")
        self.assertEqual(rule.tolerance.value, 0.1)

    def test_parses_with_bare_tolerance(self):
        from nextmv.cli.actions.ensemble import parse_evaluation_rule

        r = {
            "id": "rule-1",
            "statistics_path": "$.value",
            "objective": "maximize",
            "tolerance": 0.05,
        }
        rule = parse_evaluation_rule(r, 0)
        self.assertEqual(rule.tolerance.value, 0.05)

    def test_normalizes_min_max_shorthand(self):
        from nextmv.cli.actions.ensemble import parse_evaluation_rule

        r = {
            "id": "rule-1",
            "statistics_path": "$.value",
            "objective": "min",
            "tolerance": 0.0,
        }
        rule = parse_evaluation_rule(r, 0)
        from nextmv.cloud.ensemble import RuleObjective
        self.assertEqual(rule.objective, RuleObjective.MINIMIZE)

    def test_raises_on_unknown_objective(self):
        from nextmv.cli.actions.ensemble import parse_evaluation_rule

        r = {
            "id": "rule-1",
            "statistics_path": "$.value",
            "objective": "unknown",
            "tolerance": 0.0,
        }
        with self.assertRaises(ValueError):
            parse_evaluation_rule(r, 0)

    def test_defaults_index_to_zero(self):
        from nextmv.cli.actions.ensemble import parse_evaluation_rule

        r = {
            "id": "rule-1",
            "statistics_path": "$.value",
            "objective": "minimize",
            "tolerance": 0.0,
        }
        rule = parse_evaluation_rule(r, 0)
        self.assertEqual(rule.index, 0)


class TestListEnsembles(unittest.TestCase):
    @patch("nextmv.cli.actions.ensemble.Application")
    def test_returns_list_of_dicts(self, mock_app_class):
        mock_e = MagicMock()
        mock_e.to_dict.return_value = {"id": "ens-1"}
        mock_app = MagicMock()
        mock_app.list_ensemble_definitions.return_value = [mock_e]
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.ensemble import list_ensembles

        result = list_ensembles(client, "my-app")

        mock_app_class.assert_called_once_with(client=client, id="my-app")
        self.assertEqual(result, [{"id": "ens-1"}])


class TestGetEnsemble(unittest.TestCase):
    @patch("nextmv.cli.actions.ensemble.Application")
    def test_returns_dict(self, mock_app_class):
        mock_ens = MagicMock()
        mock_ens.to_dict.return_value = {"id": "ens-1"}
        mock_app = MagicMock()
        mock_app.ensemble_definition.return_value = mock_ens
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.ensemble import get_ensemble

        result = get_ensemble(client, "my-app", "ens-1")

        mock_app.ensemble_definition.assert_called_once_with(ensemble_definition_id="ens-1")
        self.assertEqual(result, {"id": "ens-1"})


class TestCreateEnsemble(unittest.TestCase):
    @patch("nextmv.cli.actions.ensemble.RunGroup")
    @patch("nextmv.cli.actions.ensemble.Application")
    def test_creates_with_all_params(self, mock_app_class, mock_rg_class):
        mock_rg = MagicMock()
        mock_rg_class.from_dict.return_value = mock_rg
        mock_ens = MagicMock()
        mock_ens.to_dict.return_value = {"id": "new-ens"}
        mock_app = MagicMock()
        mock_app.new_ensemble_definition.return_value = mock_ens
        mock_app_class.return_value = mock_app

        client = MagicMock()
        run_groups = [{"id": "rg1", "instance_id": "inst-1"}]
        rules = [
            {
                "id": "rule-1",
                "statistics_path": "$.value",
                "objective": "minimize",
                "tolerance": 0.1,
            }
        ]

        from nextmv.cli.actions.ensemble import create_ensemble

        result = create_ensemble(
            client,
            "my-app",
            run_groups=run_groups,
            rules=rules,
            ensemble_definition_id="ens-id",
            name="My Ensemble",
            description="desc",
        )

        mock_app_class.assert_called_once_with(client=client, id="my-app")
        mock_rg_class.from_dict.assert_called_once_with(run_groups[0])
        mock_app.new_ensemble_definition.assert_called_once()
        self.assertEqual(result, {"id": "new-ens"})


class TestDeleteEnsemble(unittest.TestCase):
    @patch("nextmv.cli.actions.ensemble.Application")
    def test_deletes_ensemble(self, mock_app_class):
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app

        client = MagicMock()

        from nextmv.cli.actions.ensemble import delete_ensemble

        result = delete_ensemble(client, "my-app", "ens-1")

        mock_app.delete_ensemble_definition.assert_called_once_with(ensemble_definition_id="ens-1")
        self.assertIsNone(result)


class TestBuildEnsembleRunConfig(unittest.TestCase):
    def test_builds_config_with_ensemble_run_type(self):
        from nextmv.cli.actions.ensemble import build_ensemble_run_config
        from nextmv.run import RunType

        config = build_ensemble_run_config("ens-1")

        self.assertEqual(config.run_type.run_type, RunType.ENSEMBLE)
        self.assertEqual(config.run_type.definition_id, "ens-1")

    def test_builds_config_with_content_format(self):
        from nextmv.cli.actions.ensemble import build_ensemble_run_config
        from nextmv.run import RunType

        config = build_ensemble_run_config("ens-1", content_format="json")

        self.assertEqual(config.run_type.run_type, RunType.ENSEMBLE)
        self.assertEqual(config.run_type.definition_id, "ens-1")
        self.assertIsNotNone(config.format)


if __name__ == "__main__":
    unittest.main()
