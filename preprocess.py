# preprocess.py
import cv2

def binarize(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Light resize for readability
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # Simple thresholding
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return thresh

def deskew(image):
    # Skip deskewing entirely for now
    return image

def crop_receipt(image):
    return image  # Skip cropping — use original