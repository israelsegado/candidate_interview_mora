import cv2 as cv
import pytesseract

from src.core.config import MIN_CONF

def detect_text(img_bgr, face_filling=None):
    img = img_bgr.copy()
    if face_filling is not None:
        img[face_filling > 0] = 255

    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

    words = []
    for t, c in zip(data["text"], data["conf"]):
        if len(t.strip()) >= 2 and float(c) >= MIN_CONF:
            words.append(t.strip())
    return len(words) > 0, words