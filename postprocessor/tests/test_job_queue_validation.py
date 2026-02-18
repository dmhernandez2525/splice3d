"""Tests for F4.3 job queue acceptance validation."""

import unittest

from postprocessor.job_queue_validation import (
    generate_report,
    load_spec,
    validate_features,
    validate_job_fields,
    validate_job_statuses,
)


class TestJobQueueValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec()

    def test_spec_loads(self) -> None:
        self.assertIn("job_statuses", self.spec)
        self.assertIn("features", self.spec)

    def test_job_statuses_complete(self) -> None:
        errors = validate_job_statuses(self.spec)
        self.assertEqual(errors, [])

    def test_job_fields_complete(self) -> None:
        errors = validate_job_fields(self.spec)
        self.assertEqual(errors, [])

    def test_features_complete(self) -> None:
        errors = validate_features(self.spec)
        self.assertEqual(errors, [])

    def test_overall_report_passes(self) -> None:
        report = generate_report(self.spec)
        self.assertTrue(report["passed"])

    def test_missing_status_detected(self) -> None:
        bad_spec = {"job_statuses": ["PENDING"]}
        errors = validate_job_statuses(bad_spec)
        self.assertGreater(len(errors), 0)

    def test_max_jobs_reasonable(self) -> None:
        max_jobs = self.spec.get("max_queued_jobs", 0)
        self.assertGreaterEqual(max_jobs, 4)
        self.assertLessEqual(max_jobs, 32)


if __name__ == "__main__":
    unittest.main()
