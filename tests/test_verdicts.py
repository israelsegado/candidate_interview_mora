"""Compares each row of results.csv with the correct answer in expected.csv.

There is one test per image and field, so you can see exactly what fails and where.
"""
import pytest

from conftest import record


def row_for(by_file, case):
    row = by_file.get(case["file"])
    if row is None:
        pytest.fail(f"{case['file']} does not appear in results.csv")
    return row


def compare(field, got, expected, file):
    ok = got == expected
    record(field, ok)
    assert ok, f"{file}: {field} = {got!r}, expected {expected!r}"


def test_type(by_file, case):
    row = row_for(by_file, case)
    compare("type", row["type"], case["type"], case["file"])


def test_program(by_file, case):
    row = row_for(by_file, case)
    compare("program", row["program"], case["program"], case["file"])


def test_verdict(by_file, case):
    row = row_for(by_file, case)
    compare("verdict", row["verdict"], case["verdict"], case["file"])


def test_failed_rule(by_file, rejected):
    """Rejected images must fail for the right rule."""
    row = row_for(by_file, rejected)
    for rule in rejected["failed_rules"].split(";"):
        compare("rule", row.get(rule), "FAIL", f"{rejected['file']} ({rule})")
