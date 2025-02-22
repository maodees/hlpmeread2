import easyocr
import numpy as np
from gtts import gTTS
from PIL import Image
from transformers import pipeline
from deep_translator import GoogleTranslator
import cv2
import validators
import time
import streamlit as st
from streamlit_js_eval import get_browser_language

# Function to auto-rotate image based on EXIF data
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
# Function to extract QR Code info using OpenCV

def extract_qr_code(image: Image) -> str:
    image_cv = np.array(image)
    gray = cv2.cvtColor(image_cv, cv2.COLOR_RGB2GRAY)
    qr_detector = cv2.QRCodeDetector()
    retval, decoded_info, points, straight_qrcode = qr_detector.detectAndDecodeMulti(gray)

    if retval:
        for data in decoded_info:
            if validators.url(data):
                return "Invalid QR code: Website redirection is not allowed"
        return decoded_info
    return None

# Function for OCR text extraction
def extract_text_from_image(image: np.ndarray) -> str:
    reader = easyocr.Reader(['en'])
    results = reader.readtext(image)
    return "\n".join([res[1] for res in results])

# Function for text summarization
def summarize_text(text: str) -> str:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    return summarizer(text, max_length=150, min_length=50, do_sample=False)[0]["summary_text"]

# Function for translation
def translate_text(text: str, target_lang: str) -> str:
    translator = GoogleTranslator(source="en", target=target_lang)
    return translator.translate(text)
# Function for text-to-speech conversion
def generate_speech(text: str, lang: str) -> None:
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save("output.mp3")

# Main function to handle the image upload and processing
def process_image(image: Image, target_language: str) -> None:
    img_array = np.array(image)
    # QR Code Detection
    qr_info = extract_qr_code(image)

    if qr_info:
        return "QR Code Information: " + " | ".join(qr_info)
    else:
        extracted_text = extract_text_from_image(img_array)
        summarized_text = summarize_text(extracted_text)
        translated_text = translate_text(summarized_text, target_language) 
        # Audio Generation
        generate_speech(translated_text, target_language)
        return extracted_text, summarized_text, translated_text

def get_language():
     lang= get_browser_language()
     #st.write(lang)
     match lang[0]:
        case "en":
            return "English"
        case "zh":
            return "Chinese"
        case "ms":
            return "Malay"
        case "ta":
            return "Tamil"
        case _:
            return "Blank"
