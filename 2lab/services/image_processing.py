import cv2
import numpy as np


def binarize_image(image: np.ndarray, algorithm: str) -> np.ndarray:
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    if algorithm == "otsu":
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    elif algorithm == "bradley":
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
    elif algorithm == "niblack":
        binary = cv2.ximgproc.niBlackThreshold(gray, 255, cv2.THRESH_BINARY, 15,
                                               -0.2, cv2.THRESH_BINARY)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    return binary