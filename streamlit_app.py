import streamlit as st
import easyocr
import numpy as np
from gtts import gTTS
from PIL import Image, ExifTags
from transformers import pipeline
from deep_translator import GoogleTranslator

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

# Streamlit App Title
st.title("📝 Help Me Read")

# File uploader
uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    # Auto-rotate the image
    image = auto_rotate_image(image)
    
    img_array = np.array(image)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    # OCR Processing
    reader = easyocr.Reader(['en'])
    with st.spinner("Extracting text..."):
        results = reader.readtext(img_array)
    
    extracted_text = "\n".join([res[1] for res in results])
    st.subheader("Extracted Text:")
    
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
