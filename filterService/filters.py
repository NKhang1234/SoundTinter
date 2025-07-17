import cv2
import numpy as np
from scipy.interpolate import UnivariateSpline

# === Filter Implementations ===

def apply_grayscale(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def apply_blur(image: np.ndarray) -> np.ndarray:
    return cv2.GaussianBlur(image, (15, 15), 0)

def apply_sepia(image: np.ndarray) -> np.ndarray:
    kernel = np.array([[0.272, 0.534, 0.131],
                       [0.349, 0.686, 0.168],
                       [0.393, 0.769, 0.189]])
    sepia = cv2.transform(image, kernel)
    return np.clip(sepia, 0, 255).astype(np.uint8)

def apply_gotham(image: np.ndarray) -> np.ndarray:
    # LUT Tables for Gotham filter
    midtone_contrast_increase = UnivariateSpline(
        x=[0, 25, 51, 76, 102, 128, 153, 178, 204, 229, 255],
        y=[0, 13, 25, 51, 76, 128, 178, 204, 229, 242, 255]
    )(range(256)).astype(np.uint8)

    lowermids_increase = UnivariateSpline(
        x=[0, 16, 32, 48, 64, 80, 96, 111, 128, 143, 159, 175, 191, 207, 223, 239, 255],
        y=[0, 18, 35, 64, 81, 99, 107, 112, 121, 143, 159, 175, 191, 207, 223, 239, 255]
    )(range(256)).astype(np.uint8)

    uppermids_decrease = UnivariateSpline(
        x=[0, 16, 32, 48, 64, 80, 96, 111, 128, 143, 159, 175, 191, 207, 223, 239, 255],
        y=[0, 16, 32, 48, 64, 80, 96, 111, 128, 140, 148, 160, 171, 187, 216, 236, 255]
    )(range(256)).astype(np.uint8)

    # Apply Gotham filter
    blue, green, red = cv2.split(image)
    red = cv2.LUT(red, midtone_contrast_increase)
    blue = cv2.LUT(blue, lowermids_increase)
    blue = cv2.LUT(blue, uppermids_decrease)

    return cv2.merge((blue, green, red))

def apply_warm(image: np.ndarray) -> np.ndarray:
    # LUT Tables
    increase_table = UnivariateSpline(x=[0, 64, 128, 255], y=[0, 75, 155, 255])(range(256)).astype(np.uint8)
    decrease_table = UnivariateSpline(x=[0, 64, 128, 255], y=[0, 45, 95, 255])(range(256)).astype(np.uint8)

    # Apply Warm filter
    blue, green, red = cv2.split(image)
    red = cv2.LUT(red, increase_table)
    blue = cv2.LUT(blue, decrease_table)

    return cv2.merge((blue, green, red))

def apply_cold(image: np.ndarray) -> np.ndarray:
    # LUT Tables
    increase_table = UnivariateSpline(x=[0, 64, 128, 255], y=[0, 75, 155, 255])(range(256)).astype(np.uint8)
    decrease_table = UnivariateSpline(x=[0, 64, 128, 255], y=[0, 45, 95, 255])(range(256)).astype(np.uint8)

    # Apply Cold filter
    blue, green, red = cv2.split(image)
    red = cv2.LUT(red, decrease_table)
    blue = cv2.LUT(blue, increase_table)

    return cv2.merge((blue, green, red))

# === Filter Map ===
FILTER_MAP = {
    "grayscale": apply_grayscale,
    "blur": apply_blur,
    "sepia": apply_sepia,
    "gotham": apply_gotham,
    "warm": apply_warm,
    "cold": apply_cold
}
