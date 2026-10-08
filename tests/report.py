"""
tests/report.py

Generates a machine-readable test execution report from actual pytest runs.
Saves results to data/testing/test_report.json.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import pytest


class ResultCollector:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.errors = 0
        self.total = 0

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            self.total += 1
            if report.passed:
                self.passed += 1
            elif report.failed:
                self.failed += 1
            elif report.skipped:
                self.skipped += 1
        elif report.when in ("setup", "teardown") and report.failed:
            self.errors += 1
            self.total += 1


def run_and_report(target_args: list[str] | None = None) -> dict:
    """Runs pytest with the collector plugin and outputs test_report.json."""
    output_dir = Path("data") / "testing"
    output_dir.mkdir(parents=True, exist_ok=True)
    report_file = output_dir / "test_report.json"

    collector = ResultCollector()
    start_time = time.time()

    args = target_args or ["tests", "-v"]
    exit_code = pytest.main(args, plugins=[collector])
    duration = round(time.time() - start_time, 2)

    report_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_tests": collector.total,
        "passed": collector.passed,
        "failed": collector.failed,
        "skipped": collector.skipped,
        "errors": collector.errors,
        "duration_seconds": duration,
        "exit_code": int(exit_code),
        "status": "PASSED" if exit_code == 0 else "FAILED",
    }

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    print(f"\nTest report saved to: {report_file}")
    print(json.dumps(report_data, indent=2))
    return report_data


if __name__ == "__main__":
    args = sys.argv[1:] if len(sys.argv) > 1 else None
    run_and_report(args)
