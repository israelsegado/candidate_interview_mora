import csv
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}

COLUMNS = ["file", "type", "program", "verdict", "mouth", "eyes", "text", "reason"]
RULES = ["mouth", "eyes", "text"]


def folders(config):
    return [Path(p) for p in (config.getoption("--images") or [ROOT / "faces", ROOT / "wordmarks"])]


def images(config):
    found = []
    for folder in folders(config):
        for path in sorted(folder.rglob("*")):
            if path.is_file() and path.suffix.lower() in EXTENSIONS:
                found.append(path.name)
    return found


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def expected(config):
    return read_csv(config.getoption("--expected"))


def pytest_generate_tests(metafunc):
    if "case" in metafunc.fixturenames:
        rows = expected(metafunc.config)
        metafunc.parametrize("case", rows, ids=[r["file"] for r in rows])
    if "rejected" in metafunc.fixturenames:
        rows = [r for r in expected(metafunc.config) if r["verdict"] == "FAIL"]
        metafunc.parametrize("rejected", rows, ids=[r["file"] for r in rows])


@pytest.fixture(scope="session")
def results_csv(request, tmp_path_factory):
    """Runs review.py once per session and returns the path to the CSV."""
    existing = request.config.getoption("--results")
    if existing:
        return Path(existing)

    output = tmp_path_factory.mktemp("output") / "results.csv"
    cmd = [sys.executable, str(ROOT / "review.py")]
    cmd += [str(f) for f in folders(request.config)]
    cmd += ["-o", str(output)]
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=request.config.getoption("--timeout"),
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
    except subprocess.TimeoutExpired:
        pytest.exit("review.py did not finish in time.", returncode=1)
    if proc.returncode != 0:
        pytest.exit(
            f"review.py exited with code {proc.returncode}.\n"
            f"--- stdout ---\n{proc.stdout[-3000:]}\n--- stderr ---\n{proc.stderr[-3000:]}",
            returncode=1,
        )
    if not output.exists():
        pytest.exit(f"review.py did not write {output}.", returncode=1)
    return output


@pytest.fixture(scope="session")
def results_xlsx(results_csv):
    """The Excel file is written next to the CSV, with the same name and an .xlsx extension."""
    return results_csv.with_suffix(".xlsx")


@pytest.fixture(scope="session")
def rows(results_csv):
    return read_csv(results_csv)


@pytest.fixture(scope="session")
def by_file(rows):
    """Indexes rows by file name (a path or a bare name are both accepted)."""
    return {Path(r.get("file", "")).name: r for r in rows}


# --- Accuracy summary at the end of the run ---

_hits = {}


def record(field, ok):
    total, good = _hits.get(field, (0, 0))
    _hits[field] = (total + 1, good + int(ok))


def pytest_terminal_summary(terminalreporter):
    if not _hits:
        return
    terminalreporter.section("Accuracy summary")
    for field, (total, good) in _hits.items():
        terminalreporter.write_line(f"{field:<12} {good:>3}/{total:<3} ({100 * good / total:.0f}%)")
