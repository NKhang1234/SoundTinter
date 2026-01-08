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

def apply_clarendon(image: np.ndarray) -> np.ndarray:
    """High contrast, cool highlights."""
    img = image.astype(np.float32)
    # Increase contrast
    img = cv2.convertScaleAbs(img, alpha=1.3, beta=0)
    # Add slight cool tint
    b, g, r = cv2.split(img)
    b = cv2.add(b, 10)
    r = cv2.subtract(r, 10)
    return cv2.merge((b, g, r)).clip(0, 255).astype(np.uint8)

def apply_lark(image: np.ndarray) -> np.ndarray:
    """Bright, slightly desaturated."""
    img = cv2.convertScaleAbs(image, alpha=1.1, beta=15)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] *= 0.8  # reduce saturation
    hsv[..., 2] *= 1.1  # increase brightness
    hsv = np.clip(hsv, 0, 255).astype(np.uint8)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def apply_juno(image: np.ndarray) -> np.ndarray:
    """Warm, saturated look emphasizing reds and yellows."""
    img = image.astype(np.float32)
    b, g, r = cv2.split(img)
    r = cv2.add(r, 25)
    g = cv2.add(g, 10)
    b = cv2.subtract(b, 10)
    merged = cv2.merge((b, g, r))
    return cv2.convertScaleAbs(merged, alpha=1.15, beta=0)

def apply_reyes(image: np.ndarray) -> np.ndarray:
    """Creamy faded vintage style."""
    img = cv2.convertScaleAbs(image, alpha=1.05, beta=10)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] *= 0.7  # reduce saturation
    hsv[..., 2] *= 1.1  # brighten
    hsv = np.clip(hsv, 0, 255).astype(np.uint8)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def apply_valencia(image: np.ndarray) -> np.ndarray:
    """Warm tint and slight fade."""
    img = cv2.convertScaleAbs(image, alpha=1.05, beta=20)
    b, g, r = cv2.split(img)
    r = cv2.add(r, 20)
    b = cv2.add(b, 10)
    merged = cv2.merge((b, g, r))
    return cv2.addWeighted(img, 0.9, merged, 0.1, 0)

def apply_xpro2(image: np.ndarray) -> np.ndarray:
    """Cross-processed cinematic look with vignette."""
    img = cv2.convertScaleAbs(image, alpha=1.2, beta=10)
    b, g, r = cv2.split(img)
    g = cv2.add(g, 10)
    b = cv2.add(b, 15)
    merged = cv2.merge((b, g, r))

    # Create vignette
    rows, cols = merged.shape[:2]
    kernel_x = cv2.getGaussianKernel(cols, 200)
    kernel_y = cv2.getGaussianKernel(rows, 200)
    kernel = kernel_y * kernel_x.T
    mask = 255 * kernel / np.linalg.norm(kernel)
    vignette = np.copy(merged)
    for i in range(3):
        vignette[:, :, i] = vignette[:, :, i] * mask
    return np.clip(vignette, 0, 255).astype(np.uint8)

def apply_amaro(image: np.ndarray) -> np.ndarray:
    """Soft vintage look: bright center, faded shadows."""
    img = cv2.convertScaleAbs(image, alpha=1.1, beta=10)
    overlay = np.full_like(img, (255, 250, 240))  # warm tint
    blended = cv2.addWeighted(img, 0.8, overlay, 0.2, 0)
    return cv2.GaussianBlur(blended, (3, 3), 0)

def apply_lofi(image: np.ndarray) -> np.ndarray:
    """High contrast and saturation for bold colors."""
    img = cv2.convertScaleAbs(image, alpha=1.3, beta=10)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] *= 1.3  # boost saturation
    hsv = np.clip(hsv, 0, 255).astype(np.uint8)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def apply_nashville(image: np.ndarray) -> np.ndarray:
    """Warm pink tone with low contrast."""
    img = cv2.convertScaleAbs(image, alpha=1.05, beta=10)
    b, g, r = cv2.split(img)
    r = cv2.add(r, 30)
    b = cv2.add(b, 10)
    merged = cv2.merge((b, g, r))
    return cv2.addWeighted(img, 0.9, merged, 0.1, 0)

def apply_willow(image: np.ndarray) -> np.ndarray:
    """Soft monochrome with warm tint."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sepia = cv2.merge((gray, gray, gray))
    sepia = cv2.convertScaleAbs(sepia, alpha=1.1, beta=15)
    return cv2.applyColorMap(sepia, cv2.COLORMAP_BONE)

def apply_gingham(image: np.ndarray) -> np.ndarray:
    """Faded pastel tone."""
    img = cv2.convertScaleAbs(image, alpha=1.05, beta=10)
    overlay = np.full_like(img, (245, 240, 230))
    blended = cv2.addWeighted(img, 0.85, overlay, 0.15, 0)
    hsv = cv2.cvtColor(blended, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] *= 0.8  # reduce saturation
    hsv[..., 2] *= 1.05  # lift brightness
    return cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)

def apply_hudson(image: np.ndarray) -> np.ndarray:
    """Cool tone, cinematic look."""
    img = cv2.convertScaleAbs(image, alpha=1.1, beta=5)
    b, g, r = cv2.split(img)
    b = cv2.add(b, 25)
    r = cv2.subtract(r, 15)
    merged = cv2.merge((b, g, r))
    return cv2.addWeighted(img, 0.8, merged, 0.2, 0)

def apply_earlybird(image: np.ndarray) -> np.ndarray:
    """Old photo style with sepia tone and vignette."""
    sepia = apply_sepia(image)
    rows, cols = sepia.shape[:2]
    kernel_x = cv2.getGaussianKernel(cols, 200)
    kernel_y = cv2.getGaussianKernel(rows, 200)
    kernel = kernel_y * kernel_x.T
    mask = 255 * kernel / np.linalg.norm(kernel)
    vignette = np.copy(sepia)
    for i in range(3):
        vignette[:, :, i] = vignette[:, :, i] * mask
    return np.clip(vignette, 0, 255).astype(np.uint8)

def apply_aden(image: np.ndarray) -> np.ndarray:
    """Bright pastel filter with slight desaturation."""
    img = cv2.convertScaleAbs(image, alpha=1.05, beta=15)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] *= 0.75  # reduce saturation
    hsv[..., 2] *= 1.05  # brighten
    hsv = np.clip(hsv, 0, 255).astype(np.uint8)
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    overlay = np.full_like(bgr, (230, 240, 255))  # slight cool tint
    return cv2.addWeighted(bgr, 0.9, overlay, 0.1, 0)

# === Filter Map ===
FILTER_MAP = {
    "grayscale": apply_grayscale,
    "blur": apply_blur,
    "sepia": apply_sepia,
    "gotham": apply_gotham,
    "warm": apply_warm,
    "cold": apply_cold,
    "clarendon": apply_clarendon,
    "lark": apply_lark,
    "juno": apply_juno,
    "reyes": apply_reyes,
    "valencia": apply_valencia,
    "xpro2": apply_xpro2,
    "amaro": apply_amaro,
    "lofi": apply_lofi,
    "nashville": apply_nashville,
    "willow": apply_willow,
    "gingham": apply_gingham,
    "hudson": apply_hudson,
    "earlybird": apply_earlybird,
    "aden": apply_aden,
}
