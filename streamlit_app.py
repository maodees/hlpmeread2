import streamlit as st
import easyocr
import numpy as np
from gtts import gTTS
from PIL import Image
from transformers import pipeline
from deep_translator import GoogleTranslator
import time
import base64

# Function to convert image to base64
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        st.error(f"Logo image not found at: {image_path}")
        return None

# Get base64 encoded logo (replace 'logo.png' with your actual filename)
logo_b64 = get_base64_image("HMR_Logo.png")
if logo_b64:
    st.markdown(f"""
        <style>
        .header-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .logo {{
            width: 70px;
            height: 70px;
            margin-left: -1cm;
        }}
        .header-text {{
            text-align: center;
            margin: 0;
            padding: 0;
        }}
        </style>
        
        <div class="header-container">
            <img src="data:image/png;base64,{logo_b64}" class="logo">
            <h1 class="header-text">HelpMeRead</h1>
        </div>
            <h2 class="header-text">Have a letter that you don’t understand?</h2>
            <h6 class="header-text">We can translate and explain your letters to you so you know what they mean and what to do next.</h6>
    """, unsafe_allow_html=True)
else:
    st.header("Help Me Read")  # Fallback if logo fails to load

# Inject custom CSS for styling
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #1E2A38, #2C3E50) !important;
        color: white !important;
    }
    .stApp {
        background: linear-gradient(135deg, #1E2A38, #2C3E50) !important;
    }
    .stButton {
        display: flex;
        justify-content: center;
    }
    div.stButton > button {
        width: 100%;
        height: 80px;
        font-size: 24px;
        color: #FFFFFF;
        background-color: #007BFF;
        border: none;
        border-radius: 10px;
        margin: 10px 0;
        cursor: pointer;
    }
    div.stButton > button:hover {
        background-color: #0056b3;
    }
    .progress-container {
        width: 100%;
        background-color: #f0f2f6;
        border-radius: 8px;
        margin: 1rem 0;
        position: relative;
        overflow: hidden;
    }
    .progress-bar {
        width: 0%;
        height: 20px;
        background-color: #2575fc;
        border-radius: 8px;
        transition: width 0.5s ease;
    }
    .progress-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: black;
        font-weight: bold;
    }
    .text-container {
        padding: 1rem;
        background-color: white;
        border-radius: 10px;
        margin: 1rem 0;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for navigation
if "screen" not in st.session_state:
    st.session_state.screen = "language_selection"
if "target_language" not in st.session_state:
    st.session_state.target_language = None
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""
if "summary_text" not in st.session_state:
    st.session_state.summary_text = ""
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""

# Language Selection Screen
def render_language_selection():
    st.subheader("Select Your Language")
    
    st.markdown(
    """
   <style>
        .stButton>button {
            width: 100% !important;  /* Makes sure buttons take full width of column */
            height: 50px !important;
            font-size: 20px !important;
            border-radius: 8px !important;
            border: 2px solid #FFFFFF !important;
            padding: 16px !important;
            margin: 5px !important;  /* Adds space between buttons */
        }
        /* Adjust button spacing */
        .st-emotion-cache-1y4p8pa {
            gap: 10px !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

    # Adjust button size and arrange buttons in two rows
    col1, col2 = st.columns(2)
    with col1:
        if st.button("中文", use_container_width=True):
            st.session_state.target_language = "zh-CN"
            st.session_state.screen = "image_upload"
            st.rerun()
    with col2:
        if st.button("Bahasa Melayu", use_container_width=True):
            st.session_state.target_language = "ms"
            st.session_state.screen = "image_upload"
            st.rerun()

    col3, col4 = st.columns(2)
    with col3:
        if st.button("தமிழ்", use_container_width=True):
            st.session_state.target_language = "ta"
            st.session_state.screen = "image_upload"
            st.rerun()
    with col4:
        if st.button("English", use_container_width=True):
            st.session_state.target_language = "en"
            st.session_state.screen = "image_upload"
            st.rerun()
            
# Define a dictionary to map language codes to their native names
LANGUAGE_MAP = {
    "zh-CN": "中文",
    "ms": "Bahasa Melayu",
    "ta": "தமிழ்",
    "en": "English"
}

# Fetch the native language name from the dictionary
native_language = LANGUAGE_MAP.get(st.session_state.target_language, "Unknown")

# Image Upload Screen
def render_image_upload():
    st.subheader("Upload an Image or Take a Picture")
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        if uploaded_file:
            st.session_state.uploaded_file = uploaded_file
            st.session_state.screen = "processing"
            st.rerun()
    with col2:
        camera_file = st.camera_input("Take a Picture")
        if camera_file:
            st.session_state.uploaded_file = camera_file
            st.session_state.screen = "processing"
            st.rerun()

# Processing Screen
def render_processing():
    st.markdown(
    "<h5 style='text-align: center; color: white;'>Please wait a moment for processing to complete.</h5>",
    unsafe_allow_html=True
)

    # Create an empty placeholder for the progress bar
    progress_placeholder = st.empty()

    # Function to update the progress bar with centered text and spinner
    def update_progress(progress, text):
        progress_placeholder.markdown(f"""
            <style>
                .progress-container {{
                    width: 100%;
                    background-color: #f0f2f6;
                    border-radius: 10px;
                    height: 30px;
                    position: relative;
                    overflow: hidden;
                }}
                .progress-bar {{
                    width: {progress}%;
                    height: 100%;
                    background-color: #2575fc;
                    border-radius: 10px;
                    transition: width 0.5s ease-in-out;
                }}
                .progress-text {{
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    font-weight: bold;
                    color: black;
                    font-size: 14px;
                    z-index: 10;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }}
                .spinner {{
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    border-top: 2px solid black;
                    border-radius: 50%;
                    width: 14px;
                    height: 14px;
                    animation: spin 0.6s linear infinite;
                }}
                @keyframes spin {{
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}
            </style>
            <div class="progress-container">
                <div class="progress-bar"></div>
                <div class="progress-text">
                    <div class="spinner"></div> {progress}% - {text}
                </div>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(1)  # Simulate processing delay

    # Initial Progress (Show bar immediately at 15%)
    update_progress(15, "Initializing...")

    # Step 1: OCR Processing
    image = Image.open(st.session_state.uploaded_file)
    img_array = np.array(image)
    reader = easyocr.Reader(['en'])
    results = reader.readtext(img_array)
    st.session_state.extracted_text = "\n".join([res[1] for res in results])

    update_progress(30, "Extracting text...")

    # Step 2: Summarization
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=-1)  # Force CPU only
    st.session_state.summary_text = summarizer(
        st.session_state.extracted_text, max_length=150, min_length=50, do_sample=False
    )[0]["summary_text"]

    update_progress(70, "Summarizing text...")

    # Step 3: Translation
    st.session_state.translated_text = GoogleTranslator(
        source="en", target=st.session_state.target_language
    ).translate(st.session_state.summary_text)

    update_progress(90, "Translating text...")

    # Step 4: Completion
    update_progress(100, "Done!")

    # Finalizing
    time.sleep(1)
    st.session_state.screen = "results"
    st.rerun()


# Results Screen
def render_results():
    # Auto-collapsed Extracted Text Section
    #with st.expander("Show Extracted Text", expanded=False):
    #    st.markdown(f"{st.session_state.extracted_text}")

    # Summary and Translation remain visible
    #st.markdown(f"**Summary : ** {st.session_state.summary_text}")

     # Hide extracted text and summary in an expander
    with st.expander("Show Extracted Text and Summary"):
        st.markdown("### Extracted Text")
        st.markdown(f"<div class='text-container'>{st.session_state.extracted_text}</div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### Summary")
        st.markdown(f"<div class='text-container'>{st.session_state.summary_text}</div>", unsafe_allow_html=True)
 
    st.subheader(f"Translated Text ({native_language}):")
    st.markdown(f"<div class='text-container'>{st.session_state.translated_text}</div>", unsafe_allow_html=True)
    st.download_button("Download Translation", st.session_state.translated_text, file_name="translation.txt", mime="text/plain")

    # Add Text-to-Speech
    tts = gTTS(text=st.session_state.translated_text, lang=st.session_state.target_language, slow=False)
    tts.save("output.mp3")
    st.audio("output.mp3", format="audio/mp3")

    # Restart Button
    st.button("Restart", on_click=lambda: st.session_state.update({"screen": "image_upload", "uploaded_file": None}))

# Render the appropriate screen
if st.session_state.screen == "language_selection":
    render_language_selection()
elif st.session_state.screen == "image_upload":
    render_image_upload()
elif st.session_state.screen == "processing":
    render_processing()
elif st.session_state.screen == "results":
    render_results()
