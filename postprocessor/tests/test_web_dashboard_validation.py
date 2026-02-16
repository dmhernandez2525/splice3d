"""Tests for F9.2 web dashboard acceptance validation."""

import unittest

from postprocessor.web_dashboard_validation import (
    generate_report,
    load_spec,
    validate_http_methods,
    validate_api_routes,
    validate_websocket_events,
    validate_page_fields,
    validate_stats_fields,
    validate_features,
)


class TestWebDashboardValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("features", self.spec)

    def test_http_methods_complete(self) -> None:
        errors = validate_http_methods(self.spec)
        self.assertEqual(errors, [])

    def test_api_routes_complete(self) -> None:
        errors = validate_api_routes(self.spec)
        self.assertEqual(errors, [])

    def test_websocket_events_complete(self) -> None:
        errors = validate_websocket_events(self.spec)
        self.assertEqual(errors, [])

    def test_page_fields_complete(self) -> None:
        errors = validate_page_fields(self.spec)
        self.assertEqual(errors, [])

    def test_stats_fields_complete(self) -> None:
        errors = validate_stats_fields(self.spec)
        self.assertEqual(errors, [])

    def test_features_complete(self) -> None:
        errors = validate_features(self.spec)
        self.assertEqual(errors, [])

    def test_overall_report_passes(self) -> None:
        report = generate_report(self.spec)
        self.assertTrue(report["passed"])

    def test_missing_http_methods_item_detected(self) -> None:
        bad_spec = {"http_methods": ["GET"]}
        errors = validate_http_methods(bad_spec)
        self.assertGreater(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
