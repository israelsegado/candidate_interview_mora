"""Smiley brand rules engine.

Usage:
    python review.py faces/ wordmarks/ -o results.csv

Writes results.csv and, next to it, results.xlsx with the same rows.

This file is only the entry point. Replace the body of main() with your
implementation (feel free to split the code into other modules).
"""
import argparse
import sys

COLUMNS = ["file", "type", "program", "verdict", "mouth", "eyes", "text", "reason"]


def main():
    parser = argparse.ArgumentParser(description="Check images against the Smiley brand rules.")
    parser.add_argument("folders", nargs="+", help="Image folders (searched recursively).")
    parser.add_argument("-o", "--output", default="results.csv", help="Output CSV.")
    args = parser.parse_args()

    # TODO: walk args.folders, evaluate each image and write args.output (CSV)
    # plus the same content to an .xlsx with the same name, both with COLUMNS.
    print("review.py is not implemented yet.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
