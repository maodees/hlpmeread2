import streamlit as st
import easyocr
import numpy as np
from gtts import gTTS
from PIL import Image
from transformers import pipeline
from deep_translator import GoogleTranslator
import cv2

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

def scan_image(frame):
    # Initialize QR code detector
    qr_detector = cv2.QRCodeDetector()

    # Scan for QR codes
    retval, decoded_info, points, _ = qr_detector.detectAndDecodeMulti(frame)
    
    if retval:
        for s, p in zip(decoded_info, points):
            if s:
                st.write(f"QR Code detected: {s}")
                # Draw polygon around the QR code
                frame = cv2.polylines(frame, [p.astype(int)], True, (0, 255, 0), 2)

    # Scan for text using EasyOCR
    results = reader.readtext(frame)
    extracted_text = ""
    for (bbox, text, prob) in results:
        extracted_text += text + "\n"
        # Draw bounding box for the text
        top_left = tuple(map(int, bbox[0]))
        bottom_right = tuple(map(int, bbox[2]))
        cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

    return frame, extracted_text

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
        img_array = np.array(image)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        frame, extracted_text = scan_image(img_array)
else:
    cap = cv2.VideoCapture(0)
    stframe = st.empty()
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame, extracted_text = scan_image(frame)
        stframe.image(frame, channels="BGR")
        if st.button('Capture'):
            break
    cap.release()

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