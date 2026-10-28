from pathlib import Path

ROOT = Path(__file__).resolve().parent


def pytest_addoption(parser):
    parser.addoption(
        "--images",
        action="append",
        default=None,
        help="Image folder to review (repeatable). Default: faces/ and wordmarks/.",
    )
    parser.addoption(
        "--expected",
        default=str(ROOT / "tests" / "expected.csv"),
        help="CSV with the correct answers.",
    )
    parser.addoption(
        "--results",
        default=None,
        help="Use an existing results.csv instead of running review.py.",
    )
    parser.addoption(
        "--timeout",
        type=int,
        default=1800,
        help="Maximum seconds for review.py to finish.",
    )
