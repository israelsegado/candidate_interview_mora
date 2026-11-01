import cv2 as cv
import numpy as np

from src.core.config import NOISE_PERCENTAGE, CONNECTIVITY

def process_HSV_image(img_path: str):
    img = cv.imread(img_path)

    imgHSV = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    v_layer_image = imgHSV[:, :, 2]

    _, imgBinarized = cv.threshold(v_layer_image,0,255,cv.THRESH_BINARY_INV+cv.THRESH_OTSU)
    contours, _ = cv.findContours(imgBinarized, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    return imgBinarized, contours

def face_features(binarized_img, contour):
    face = max(contour, key=cv.contourArea)
    filling = np.zeros_like(binarized_img)
    cv.drawContours(filling, [face], -1, 255, thickness=cv.FILLED)

    num_labels, labels, stats, centroids = cv.connectedComponentsWithStats(binarized_img , connectivity=CONNECTIVITY , ltype=cv.CV_32S)

    face_area = cv.countNonZero(filling)

    candidates = []
    for i in range(1, num_labels):
        cx, cy = centroids[i]
        cx, cy = int(round(cx)), int(round(cy))
        if filling[cy, cx] > 0:
            candidates.append((i, stats[i, cv.CC_STAT_AREA]))

    outer_ring = max(candidates, key=lambda num: num[1])
    candidates = [num for num in candidates if num is not outer_ring]

    filtered_candidates = [num for num in candidates if num[1] > NOISE_PERCENTAGE*face_area]

    if not filtered_candidates:
        print("FAIL")

    mouth = max(filtered_candidates, key=lambda num: stats[num[0], cv.CC_STAT_WIDTH])
    eyes = [num for num in filtered_candidates if num is not mouth]

    if len(eyes) == 2:
        print("PASS")
    else:
        print("FAIL")

    features_info = {
        "components": {
            "num_labels": num_labels,
            "labels": labels,
            "stats": stats,
            "centroids": centroids
        },
        "face_features": {
            "outer_ring": outer_ring,
            "eyes": eyes,
            "mouth": mouth,
            "face_area": face_area
        }
    }

    return features_info