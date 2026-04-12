import unittest
from nextmv.evals.scorer import score_tool_sequence, score_outcome


class TestScoreToolSequence(unittest.TestCase):

    def test_exact_match_scores_1(self):
        self.assertEqual(score_tool_sequence(["cloud_list_apps"], ["cloud_list_apps"]), 1.0)

    def test_missing_tool_scores_partial(self):
        self.assertEqual(score_tool_sequence(["cloud_list_apps", "cloud_get_app"], ["cloud_list_apps"]), 0.5)

    def test_extra_tools_dont_penalize(self):
        self.assertEqual(score_tool_sequence(["cloud_list_apps"], ["cloud_list_apps", "cloud_get_app"]), 1.0)

    def test_empty_expected_scores_1(self):
        self.assertEqual(score_tool_sequence([], []), 1.0)

    def test_wrong_tools_score_0(self):
        self.assertEqual(score_tool_sequence(["cloud_list_apps"], ["cloud_get_app"]), 0.0)

    def test_order_independent(self):
        self.assertEqual(score_tool_sequence(["cloud_get_app", "cloud_list_apps"], ["cloud_list_apps", "cloud_get_app"]), 1.0)


class TestScoreOutcome(unittest.TestCase):

    def test_contains_check_passes(self):
        result = [{"role": "tool", "content": '[{"id": "routing-app"}]'}]
        self.assertTrue(score_outcome(result, {"contains": "routing-app"}))

    def test_contains_check_fails(self):
        result = [{"role": "tool", "content": '[{"id": "other-app"}]'}]
        self.assertFalse(score_outcome(result, {"contains": "routing-app"}))

    def test_tool_called_check(self):
        result = [
            {"role": "tool", "tool": "cloud_list_apps", "content": "[]"},
            {"role": "tool", "tool": "cloud_get_app", "content": "{}"},
        ]
        self.assertTrue(score_outcome(result, {"tool_called": "cloud_get_app"}))

    def test_tool_not_called_check(self):
        result = [{"role": "tool", "tool": "cloud_list_apps", "content": "[]"}]
        self.assertFalse(score_outcome(result, {"tool_called": "cloud_get_app"}))

    def test_no_criteria_passes(self):
        self.assertTrue(score_outcome([], {}))
