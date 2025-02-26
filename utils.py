import numpy as np
import cv2
import base64
import validators
from PIL import Image
from streamlit_js_eval import get_browser_language

# Auto-Rotate Image
def auto_rotate_image(image: Image) -> Image:
    try:
        exif = image._getexif()
        if exif is not None:
            orientation = exif.get(274)
            if orientation == 3:
                image = image.rotate(180, expand=True)
            elif orientation == 6:
                image = image.rotate(270, expand=True)
            elif orientation == 8:
                image = image.rotate(90, expand=True)
    except AttributeError:
        pass
    return image

# QR Code Extraction
def extract_qr_code(image: Image) -> str:
    img_cv = np.array(image)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
    qr_detector = cv2.QRCodeDetector()
    retval, decoded_info, _, _ = qr_detector.detectAndDecodeMulti(gray)
    
    if retval:
        for data in decoded_info:
            if validators.url(data):
                return "Invalid QR code: Website redirection is not allowed"
        return " | ".join(decoded_info)
    return None

# Get Base64 for Images (Used for logo rendering)
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None

# Get Browser Language
def get_language():
    lang = get_browser_language()
    return {"en": "English", "zh": "Chinese", "ms": "Malay", "ta": "Tamil"}.get(lang, "Unknown")
