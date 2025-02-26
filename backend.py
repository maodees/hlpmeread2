import easyocr
import numpy as np
from gtts import gTTS
from PIL import Image
from transformers import pipeline
from deep_translator import GoogleTranslator
import cv2
from utils import extract_qr_code, auto_rotate_image

# OCR Processing
def extract_text_from_image(image: np.ndarray) -> str:
    reader = easyocr.Reader(['en'])
    results = reader.readtext(image)
    return "\n".join([res[1] for res in results])

# Text Summarization
def summarize_text(text: str) -> str:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    return summarizer(text, max_length=150, min_length=50, do_sample=False)[0]["summary_text"]

# Translation
def translate_text(text: str, target_lang: str) -> str:
    translator = GoogleTranslator(source="en", target=target_lang)
    return translator.translate(text)

# Text-to-Speech
def generate_speech(text: str, lang: str) -> None:
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save("output.mp3")

# Full Processing Pipeline
def process_image(image, target_language: str):
    image_pil = Image.open(image)
    image_pil = auto_rotate_image(image_pil)
    img_array = np.array(image_pil)

    # QR Code Detection
    qr_info = extract_qr_code(image_pil)
    if qr_info:
        return qr_info, "", ""

    # Text Processing
    extracted_text = extract_text_from_image(img_array)
    summarized_text = summarize_text(extracted_text)
    translated_text = translate_text(summarized_text, target_language)

    # Generate Speech
    generate_speech(translated_text, target_language)

    return extracted_text, summarized_text, translated_text
