from skimage.morphology import skeletonize
import numpy as np
import cv2 as cv

from src.core.config import MIN_BRANCH, MAX_BRANCH

def crop_and_skeletonized_mouth(features: dict[dict]):
    feature_components = features["components"]
    face_features = features["face_features"]

    mouth_idx = face_features["mouth"][0]
    mouth_mask = (feature_components["labels"] == mouth_idx).astype(np.uint8) * 255

    face_stats = feature_components["stats"]
    x, y, w, h = face_stats[mouth_idx, :4]
    mouth_crop = mouth_mask[y:y+h, x:x+w]

    skel = skeletonize(mouth_crop > 0)
    return skel

def dimple_information(skeleton):
    sk = (skeleton > 0).astype(np.uint8)

    neighbors = cv.filter2D(src=sk, ddepth=-1, kernel=np.ones((3, 3)), borderType=cv.BORDER_CONSTANT) - sk

    cross = ((sk==1) & (neighbors>=3)).astype(np.uint8)
    num_crosses, _, _, crosses_centroids = cv.connectedComponentsWithStats(image=cross, connectivity=8)

    endpoints = ((sk==1) & (neighbors==1)).astype(np.uint8)
    y_endpoint, x_endpoint = np.nonzero(endpoints)

    dimples = {
        "crosses": {
            "num": num_crosses,
            "centroids": crosses_centroids
        },
        "endpoints": {
            "y_coor": y_endpoint,
            "x_coor": x_endpoint
        }
    }

    return dimples

def assign_branches(dimples: dict, size: int):
    num_crosses = dimples["crosses"]["num"]
    crosses_centroids = dimples["crosses"]["centroids"]

    x_ep = dimples["endpoints"]["x_coor"]
    y_ep = dimples["endpoints"]["y_coor"]

    branches = {c: [] for c in range(1, num_crosses)}
    for k in range(len(x_ep)):
        best_cross, best_distance = None, None
        for c in range(1, num_crosses):
            cx, cy = crosses_centroids[c]
            distance = ((x_ep[k] - cx)**2 + (y_ep[k] - cy)**2) ** 0.5

            if best_distance is None or distance < best_distance:
                best_cross, best_distance = c, distance
        if best_cross is not None and (MIN_BRANCH <= best_distance/size <= MAX_BRANCH):
            branches[best_cross].append((x_ep[k], y_ep[k]))

    return branches

def classify_branches(branches, crosses_centroids, w, h):
    x_center, y_center = w/2, h/2
    states = []
    for c, points in branches.items():
        cx, cy = crosses_centroids[c]
        dx, dy = x_center - cx, y_center - cy #distancia de cada rama al centro de la boca

        sides = [dx * (py - cy) - dy * (px - cx) for (px, py) in points]

        if len(points) >= 2 and (max(sides) > 0 > min(sides)):
            states.append("Complete")
        elif len(points) >= 1:
            states.append("Half")

    completes = states.count("Complete")
    if completes == 2:
        return True, "completed"
    else:
        return False, f"completed are: {completes} of 2 states: {states}"
