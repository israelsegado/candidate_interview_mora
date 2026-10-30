import cv2 as cv
import numpy as np
import os
import matplotlib.pyplot as plt
from IPython.display import Image, display

root = os.getcwd()

face_example = os.path.join(root, "faces/Approved/blue.png")
face_dir = os.path.join(root, "faces/Approved")

processed_dir = os.path.join(root, "Procesados")
os.makedirs(processed_dir, exist_ok=True)

hsv_processed = os.path.join(processed_dir, "hsv")
os.makedirs(hsv_processed, exist_ok=True)

def process_HSV_image(image, img_path: str):
    img = cv.imread(img_path)

    imgHSV = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    imgRecortada = imgHSV[:, :, 2]

    ret,imgOtsu = cv.threshold(imgRecortada,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)

    return ret, imgOtsu

def build_contours(bw_image):
    _, imgTh = cv.threshold(bw_image, 127, 255, cv.THRESH_BINARY_INV)
    contours, _ = cv.findContours(imgTh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    face = max(contours, key=cv.contourArea)
    return imgTh, contours, face

BnW_images = []

for image in os.listdir(face_dir):
    img_path = os.path.join(face_dir, image)
    ret, img = process_HSV_image(image=image, img_path=img_path)

    BnW_images.append(img)
    
    cv.imwrite(os.path.join(hsv_processed, image), img)


imgTh, contours, face = build_contours(BnW_images[8])
#--------------------------------------------------------------------------------------------------
filling = np.zeros_like(imgTh)
cv.drawContours(filling, [face], -1, 255, thickness=cv.FILLED)

connectivity = 8
num_labels, labels, stats, centroids = cv.connectedComponentsWithStats(imgTh , connectivity=connectivity , ltype=cv.CV_32S)

face_area = cv.countNonZero(filling)

candidates = []
for i in range(1, num_labels):
    cx, cy = centroids[i]
    cx, cy = int(round(cx)), int(round(cy))
    if filling[cy, cx] > 0:
        candidates.append((i, stats[i, cv.CC_STAT_AREA]))

print(candidates)

if cv.waitKey(0) & 0xFF == ord('q'):
    cv.destroyAllWindows()