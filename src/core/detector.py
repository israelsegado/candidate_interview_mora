import cv2 as cv
import numpy as np

from src.core.config import NOISE_PERCENTAGE, CONNECTIVITY, MIN_MOUTH_WIDTH_RATIO

def process_HSV_image(img_path: str) -> tuple:
    """
    Takes an image and ir returns the same binarized image and its contours.
    """
    img = cv.imread(img_path)

    imgHSV = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    v_layer_image = imgHSV[:, :, 2]

    _, imgBinarized = cv.threshold(v_layer_image,0,255,cv.THRESH_BINARY_INV+cv.THRESH_OTSU)
    contours, _ = cv.findContours(imgBinarized, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    return imgBinarized, contours

def face_features(binarized_img, face_contour) -> dict:
    """
    Extract relevant features of an image. Returning a dictionary with the information.
    """
    filling = np.zeros_like(binarized_img)
    cv.drawContours(filling, [face_contour], -1, 255, thickness=cv.FILLED)

    num_labels, labels, stats, centroids = cv.connectedComponentsWithStats(binarized_img , connectivity=CONNECTIVITY , ltype=cv.CV_32S)

    face_area = cv.countNonZero(filling)

    candidates = []
    for i in range(1, num_labels):
        cx, cy = centroids[i]
        cx, cy = int(round(cx)), int(round(cy))
        if filling[cy, cx] > 0:
            candidates.append((i, stats[i, cv.CC_STAT_AREA]))

    if not candidates:
        return {"components": {
                    "num_labels": num_labels, 
                    "labels": labels, 
                    "stats": stats, 
                    "centroids": centroids
                },
                "face_features": {
                    "outer_ring": None, 
                    "eyes": [], 
                    "mouth": None, 
                    "face_area": face_area
                    }
                }

    outer_ring = max(candidates, key=lambda num: num[1])
    candidates = [num for num in candidates if num != outer_ring]

    filtered_candidates = [num for num in candidates if num[1] > NOISE_PERCENTAGE*face_area]

    if not filtered_candidates:
        return {"components": {
                    "num_labels": num_labels, 
                    "labels": labels, 
                    "stats": stats, 
                    "centroids": centroids
                },
                "face_features": {
                    "outer_ring": outer_ring, 
                    "eyes": [], 
                    "mouth": None, 
                    "face_area": face_area
                    }
                }

    mouth_candidate = max(filtered_candidates, key=lambda num: stats[num[0], cv.CC_STAT_WIDTH])
 
    face_width = stats[outer_ring[0], cv.CC_STAT_WIDTH]
    mouth_width = stats[mouth_candidate[0], cv.CC_STAT_WIDTH]

    mouth = mouth_candidate if mouth_width > (face_width * MIN_MOUTH_WIDTH_RATIO) else None
    eyes = [num for num in filtered_candidates if num != mouth]

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