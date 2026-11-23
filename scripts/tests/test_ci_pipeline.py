"""Protege el aislamiento de CI y el rechazo de pruebas omitidas o fallidas."""

import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "ci_pipeline", Path(__file__).parents[1] / "ci_pipeline.py"
)
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)


@pytest.mark.parametrize(
    "run_id", ["../jg-repuestos", "/tmp", "", "jg;docker", "x" * 49]
)
def test_rejects_identifiers_that_could_escape_owned_resources(run_id):
    with pytest.raises(ValueError):
        ci.Pipeline(run_id)


@pytest.mark.parametrize("stage", ["test", "build"])
def test_later_stage_requires_a_success_record(tmp_path, monkeypatch, stage):
    monkeypatch.setattr(ci, "ROOT", tmp_path)
    pipeline = ci.Pipeline("safety-test")
    pipeline.prepare()
    with pytest.raises(RuntimeError):
        pipeline.require_passed(stage)
    pipeline.record(stage, "failed")
    with pytest.raises(RuntimeError):
        pipeline.require_passed(stage)


@pytest.mark.parametrize(
    "tests,skipped,failures,errors",
    [(0, 0, 0, 0), (32, 18, 0, 0), (32, 0, 1, 0), (32, 0, 0, 1)],
)
def test_does_not_accept_empty_skipped_or_failing_report(
    tmp_path, tests, skipped, failures, errors
):
    report = tmp_path / "pytest.xml"
    report.write_text(
        f'<testsuites><testsuite tests="{tests}" skipped="{skipped}" failures="{failures}" errors="{errors}"/></testsuites>'
    )
    with pytest.raises(RuntimeError):
        ci.validate_report(report)


def test_accepts_successful_pytest_report(tmp_path):
    report = tmp_path / "pytest.xml"
    report.write_text(
        '<testsuites><testsuite tests="32" skipped="0" failures="0" errors="0"/></testsuites>'
    )
    assert ci.validate_report(report) == 32
