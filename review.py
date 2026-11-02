"""Smiley brand rules engine.

Usage:
    python review.py faces/ wordmarks/ -o results.csv

Writes results.csv and, next to it, results.xlsx with the same rows.

This file is only the entry point. Replace the body of main() with your
implementation (feel free to split the code into other modules).
"""
import argparse
import sys
from pathlib import Path
import cv2 as cv
import os

from src.core.detector import process_HSV_image, face_features
from src.core.mouth_detection import (crop_and_skeletonized_mouth, 
                                      dimple_information, 
                                      assign_branches, 
                                      classify_branches)
from src.outputs.csv_handler import write_csv
from src.outputs.xlsx_handler import write_xlsx

COLUMNS = ["file", "type", "program", "verdict", "mouth", "eyes", "text", "reason"]
FILE_EXTENSIONS = [".png", ".jpg", ".jpeg"]

def review_image(image_path: Path):
    row = dict.fromkeys(COLUMNS, "N/A")
    row["file"] = image_path.name
    row["type"] = "face" # TODO: distinguir face / text / face+text
    row["program"] = "smiley" # TODO: distinguir smiley / smileyworld

    try:
        binary_image, contours = process_HSV_image(img_path=str(image_path))

        if len(contours) > 6:
            row["verdict"] = "FAIL"
            row["reason"] = "Too much contours."
            return row

        face = max(contours, key=cv.contourArea)
        features = face_features(binarized_img=binary_image, face_contour=face)

        if features is None:
            row.update(
                mouth="FAIL",
                eyes="FAIL",
                verdict="FAIL",
                reason="Neither eyes nor mouth in the face."
            )
            return row

        reasons = []

        num_eyes = len(features["face_features"]["eyes"])
        row["eyes"] = "PASS" if num_eyes==2 else "FAIL"
        if num_eyes != 2:
            reasons.append(f"The face has {num_eyes}. A valid face has 2 eyes.")

        skeleton = crop_and_skeletonized_mouth(features=features)
        dimples = dimple_information(skeleton=skeleton)
        h, w = skeleton.shape
        branches = assign_branches(dimples=dimples, size=max(h, w))
        mouth_ok, mouth_reason = classify_branches(branches=branches, 
                                                   crosses_centroids=dimples["crosses"]["centroids"], 
                                                   w=w, h=h)
        row["mouth"] = "PASS" if mouth_ok else "FAIL"
        if not mouth_ok:
            reasons.append(mouth_reason)

        row["verdict"] = "FAIL" if reasons else "PASS"
        row["reason"] = "; ".join(reasons) if reasons else "Valid face"

    except Exception as e:
        row.update(
            mouth="FAIL",
            eyes="FAIL",
            verdict="FAIL",
            reason=f"Error processing the image: {e}")

    return row


def main():
    parser = argparse.ArgumentParser(description="Check images against the Smiley brand rules.")
    parser.add_argument("folders", nargs="+", help="Image folders (searched recursively).")
    parser.add_argument("-o", "--output", default="results.csv", help="Output CSV.")
    args = parser.parse_args()

    rows = []
    for folder in args.folders:
        for path in sorted(Path(folder).rglob("*")):
            if path.suffix.lower() in FILE_EXTENSIONS:
                rows.append(review_image(path))

    xlsx_path = os.path.splitext(args.output)[0] + ".xlsx"
    write_csv(columns=COLUMNS, rows=rows, path=args.output)
    write_xlsx(rows=rows, path=xlsx_path, columns=COLUMNS)

    print(f"{len(rows)} images reviewed -> {args.output}, {xlsx_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
