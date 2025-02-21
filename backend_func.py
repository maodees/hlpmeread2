import streamlit as st
import easyocr
import numpy as np
from gtts import gTTS
from PIL import Image
from transformers import pipeline
from deep_translator import GoogleTranslator
import cv2
import validators  # Added to check for URLs
import time

# Function to auto-rotate an image based on its EXIF data
def auto_rotate_image(image: Image) -> Image:
    try:
        exif = image._getexif()
        if exif is not None:
            for tag, value in exif.items():
                if tag == 274:  # Orientation tag
                    if value == 3:
                        image = image.rotate(180, expand=True)
                    elif value == 6:
                        image = image.rotate(270, expand=True)
                    elif value == 8:
                        image = image.rotate(90, expand=True)
                    break
    except (AttributeError, KeyError, IndexError):
        pass  # No EXIF data, do nothing
    return image

# Function to extract QR Code info using OpenCV and check for URL
def extract_qr_code(image: Image) -> str:
    image_cv = np.array(image)
    gray = cv2.cvtColor(image_cv, cv2.COLOR_RGB2GRAY)  # Convert to grayscale
    qr_detector = cv2.QRCodeDetector()
    retval, decoded_info, points, straight_qrcode = qr_detector.detectAndDecodeMulti(gray)

    if retval:
        # Filter out URLs and reject QR codes that point to a website
        for data in decoded_info:
            if validators.url(data):  # Check if the data is a valid URL
                return "Invalid QR code: Website redirection is not allowed"
        return decoded_info  # List of QR code data found
    return None

