import streamlit as st
import easyocr
import numpy as np
from gtts import gTTS
from PIL import Image, ImageEnhance
from transformers import pipeline
from deep_translator import GoogleTranslator
import cv2

# Function to auto-rotate an image based on its EXIF data
def auto_rotate_image(image: Image) -> Image:
    # ... (keep this function as is)

def preprocess_image(image):
    # Convert to grayscale
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    # Denoise the image
    denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
    
    return Image.fromarray(denoised)

def scan_image(image):
    # Preprocess the image
    processed_image = preprocess_image(image)
    
    # Scan for text using EasyOCR
    results = reader.readtext(np.array(processed_image))
    extracted_text = ""
    for (_, text, _) in results:
        extracted_text += text + "\n"
    return extracted_text, processed_image

# Streamlit App Title
st.title("📝 Help Me Read")

# Initialize the EasyOCR reader
reader = easyocr.Reader(['en'])

# Choose input method
input_method = st.radio("Choose input method", ("Upload Image", "Use Camera"))

if input_method == "Upload Image":
    uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        image = auto_rotate_image(image)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        extracted_text, processed_image = scan_image(image)
        st.image(processed_image, caption="Processed Image", use_container_width=True)
else:
    camera_image = st.camera_input("Take a picture", key="camera")
    if camera_image is not None:
        image = Image.open(camera_image)
        
        # Image enhancement options
        st.subheader("Image Enhancement Options")
        brightness = st.slider("Brightness", 0.5, 2.0, 1.0, 0.1)
        contrast = st.slider("Contrast", 0.5, 2.0, 1.0, 0.1)
        sharpness = st.slider("Sharpness", 0.5, 2.0, 1.0, 0.1)
        
        # Apply enhancements
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(brightness)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast)
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(sharpness)
        
        st.image(image, caption="Enhanced Image", use_container_width=True)
        extracted_text, processed_image = scan_image(image)
        st.image(processed_image, caption="Processed Image", use_container_width=True)

if 'extracted_text' in locals() and extracted_text:
    st.subheader("Extracted Text:")
    st.write(extracted_text)

    # Summarization
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summarized_text = summarizer(extracted_text, max_length=150, min_length=50, do_sample=False)[0]["summary_text"]
    st.subheader("Summary:")
    st.write(summarized_text)
    st.download_button("Download Summary", summarized_text, file_name="summary.txt")

    # Translation
    languages = {"Blank": "NA", "Chinese": "zh-CN", "Malay": "ms", "Tamil": "ta", "Cantonese": "zh-yue"}
    target_language = st.selectbox("Select target language", list(languages.keys()))
    
    if target_language != "Blank":
        translator = GoogleTranslator(source="en", target=languages[target_language])
        translated_text = translator.translate(summarized_text)
        st.subheader(f"Translated Text ({target_language}):")
        st.write(translated_text)
        st.download_button("Download Translation", translated_text, file_name="translation.txt")

        # Text-to-Speech
        tts = gTTS(text=translated_text, lang=languages[target_language], slow=False)
        tts.save("output.mp3")
        st.audio("output.mp3", format="audio/mp3")
        
        with open("output.mp3", "rb") as file:
            st.download_button("Download Audio", file, file_name="speech.mp3")