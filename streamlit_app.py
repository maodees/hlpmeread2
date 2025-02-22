import streamlit as st
from backend_func import process_image, auto_rotate_image, get_language
from PIL import Image
# Set Streamlit page configuration
st.set_page_config(page_title="Help Me Read", layout="wide")
# UI Header
st.markdown("<h1 style='text-align: center; color: #ff6f61;'>📝 Help Me Read</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem;'>No information will be collected or stored. This app is for your privacy and convenience.</p>", unsafe_allow_html=True)


# Language Selection and Input Method

st.sidebar.title("🗣️ Language Selection & Input Method")
languages = {"Blank": "NA", "Chinese": "zh-CN", "Malay": "ms", "Tamil": "ta"}
#target_language = st.sidebar.selectbox("Select your language for translation", list(languages.keys()))
index = next((i for i, d in enumerate(languages) if get_language() in d), None)
target_language = st.sidebar.selectbox("Select your language for translation", list(languages.keys()), index)
input_method = st.sidebar.radio("Choose input method", ("Upload Image", "Use Camera"))

if target_language != "Blank":
    image = None

    # Image Upload or Camera Capture
    if input_method == "Upload Image":
        uploaded_file = st.sidebar.file_uploader("Upload an Image (or Scan QR)", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
    elif input_method == "Use Camera":
        camera_image = st.camera_input("Take a picture")
        if camera_image is not None:
            image = Image.open(camera_image)

    if image is not None:
        st.image(image, caption="Processed Image", width=600)
        image = auto_rotate_image(image)

        # Process image (OCR, QR code detection, translation, TTS)
        result = process_image(image, languages[target_language])
        if isinstance(result, str):
            # Display QR Code information
            st.write(result)

        else:
            # Display Extracted Text
            extracted_text, summarized_text, translated_text = result
            st.subheader("Extracted Text:")
            st.write(extracted_text)
            st.subheader("Summary:")
            st.write(summarized_text)
            st.subheader(f"Translated Text ({target_language}):")
            st.write(translated_text)

            # Audio Generation
            st.audio("output.mp3", format="audio/mp3")
            st.download_button("Download Audio", "output.mp3", file_name="speech.mp3")