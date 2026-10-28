"""Checks that results.csv follows the required format."""
from pathlib import Path

from conftest import COLUMNS, RULES, images

TYPES = {"face", "text", "face+text"}
PROGRAMS = {"smiley", "smileyworld"}
RULE_VALUES = {"PASS", "FAIL", "N/A"}


def test_columns(rows, results_csv):
    assert rows, "results.csv is empty."
    missing = [c for c in COLUMNS if c not in rows[0]]
    assert not missing, f"Missing columns in {results_csv.name}: {missing}"


def test_one_row_per_image(request, rows):
    names = [Path(r["file"]).name for r in rows]
    duplicates = sorted({n for n in names if names.count(n) > 1})
    assert not duplicates, f"Repeated files: {duplicates}"

    expected = set(images(request.config))
    missing = sorted(expected - set(names))
    extra = sorted(set(names) - expected)
    assert not missing, f"Images without a row: {missing}"
    assert not extra, f"Rows that match no image: {extra}"


def test_valid_values(rows):
    errors = []
    for r in rows:
        if r["type"] not in TYPES:
            errors.append(f"{r['file']}: type={r['type']!r}")
        if r["program"] not in PROGRAMS:
            errors.append(f"{r['file']}: program={r['program']!r}")
        if r["verdict"] not in {"PASS", "FAIL"}:
            errors.append(f"{r['file']}: verdict={r['verdict']!r}")
        for rule in RULES:
            if r[rule] not in RULE_VALUES:
                errors.append(f"{r['file']}: {rule}={r[rule]!r}")
    assert not errors, "Invalid values:\n" + "\n".join(errors)


def test_verdict_matches_rules(rows):
    """The verdict is FAIL if and only if some rule is FAIL."""
    errors = []
    for r in rows:
        any_fail = any(r[rule] == "FAIL" for rule in RULES)
        if (r["verdict"] == "FAIL") != any_fail:
            errors.append(r["file"])
    assert not errors, f"Verdict inconsistent with the rules in: {errors}"


APPLICABLE = {
    "face": {"mouth", "eyes"},
    "text": {"text"},
    "face+text": {"mouth", "eyes", "text"},
}


def test_rules_applicable_to_type(rows):
    """Each type evaluates its rules (PASS/FAIL) and leaves the rest as N/A."""
    errors = []
    for r in rows:
        applicable = APPLICABLE.get(r["type"], set())
        for rule in RULES:
            evaluated = r[rule] != "N/A"
            if evaluated != (rule in applicable):
                errors.append(f"{r['file']}: type={r['type']} with {rule}={r[rule]!r}")
    assert not errors, "\n".join(errors)


def test_reason_present(rows):
    empty = [r["file"] for r in rows if not r["reason"].strip()]
    assert not empty, f"Rows without a reason: {empty}"
