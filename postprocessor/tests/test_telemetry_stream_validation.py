"""Tests for F4.1 telemetry stream acceptance validation."""

import unittest

from postprocessor.telemetry_stream_validation import (
    generate_report,
    load_spec,
    validate_features,
    validate_stream_modes,
    validate_summary_fields,
    validate_verbose_sections,
)


class TestTelemetryStreamValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("stream_modes", self.spec)
        self.assertIn("summary_fields", self.spec)

    def test_stream_modes_complete(self) -> None:
        errors = validate_stream_modes(self.spec)
        self.assertEqual(errors, [])

    def test_summary_fields_complete(self) -> None:
        errors = validate_summary_fields(self.spec)
        self.assertEqual(errors, [])

    def test_verbose_sections_complete(self) -> None:
        errors = validate_verbose_sections(self.spec)
        self.assertEqual(errors, [])

    def test_features_complete(self) -> None:
        errors = validate_features(self.spec)
        self.assertEqual(errors, [])

    def test_overall_report_passes(self) -> None:
        report = generate_report(self.spec)
        self.assertTrue(report["passed"])

    def test_missing_mode_detected(self) -> None:
        bad_spec = {"stream_modes": ["OFF"]}
        errors = validate_stream_modes(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_serial_commands_present(self) -> None:
        commands = self.spec.get("serial_commands", [])
        self.assertIn("STREAM SUMMARY", commands)
        self.assertIn("STREAM HEARTBEAT", commands)


if __name__ == "__main__":
    unittest.main()
