import cv2 as cv

def process_HSV_image(img_path: str):
    img = cv.imread(img_path)

    imgHSV = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    v_layer_image = imgHSV[:, :, 2]

    _,imgOtsu = cv.threshold(v_layer_image,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)

    return imgOtsu

def build_contours(mask):
    _, imgTh = cv.threshold(mask, 127, 255, cv.THRESH_BINARY_INV)
    contours, _ = cv.findContours(imgTh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    face = max(contours, key=cv.contourArea)
    
    return imgTh, contours, face