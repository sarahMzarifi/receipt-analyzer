# preprocess.py
import cv2

def binarize(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Resize for better OCR readability
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # 🔹 Noise removal (NEW)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # 🔹 Adaptive threshold (BETTER than fixed threshold)
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )

    return thresh
def deskew(image):
    # Skip deskewing entirely for now
    return image

def crop_receipt(image):
    return image  # Skip cropping — use original