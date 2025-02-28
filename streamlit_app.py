import streamlit as st
import time
from backend import process_image, get_browser_language, get_base64_image, auto_rotate_image
from PIL import Image

# Load Logo
logo_b64 = get_base64_image("assets/HMR_Logo.png")

# UI Styling and Branding
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
    </style>
    <div class="header-container">
        <img src="data:image/png;base64,{logo_b64}" class="logo">
        <h1 class="header-text">HelpMeRead</h1>
    </div>
""", unsafe_allow_html=True)

# Session state for navigation
if "screen" not in st.session_state:
    st.session_state.screen = "language_selection"
if "target_language" not in st.session_state:
    st.session_state.target_language = None
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "results" not in st.session_state:
    st.session_state.results = None

# Language Selection
def render_language_selection():
    st.subheader("Select Your Language")
    
    language_map = {"中文": "zh-CN", "Bahasa Melayu": "ms", "தமிழ்": "ta", "English": "en"}
    for lang, code in language_map.items():
        if st.button(lang, use_container_width=True):
            st.session_state.target_language = code
            st.session_state.screen = "image_upload"
            st.rerun()

# Image Upload
def render_image_upload():
    st.subheader("Upload an Image or Take a Picture")
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.session_state.uploaded_file = image
        st.session_state.screen = "processing"
        st.rerun()

# Processing
def render_processing():
    st.markdown("<h5 style='text-align: center;'>Processing your image...</h5>", unsafe_allow_html=True)

    progress_placeholder = st.empty()
    
    for percent in [20, 50, 80, 100]:
        progress_placeholder.progress(percent)
        time.sleep(1)

    image = st.session_state.uploaded_file
    image = auto_rotate_image(image)
    results = process_image(image, st.session_state.target_language)
    
    st.session_state.results = results
    st.session_state.screen = "results"
    st.rerun()

# Results
def render_results():
    extracted_text, summarized_text, translated_text = st.session_state.results
    
    with st.expander("Extracted Text"):
        st.write(extracted_text)

    with st.expander("Summary"):
        st.write(summarized_text)

    st.subheader("Translated Text:")
    st.write(translated_text)

    st.download_button("Download Translation", translated_text, file_name="translation.txt", mime="text/plain")
    
    st.audio("output.mp3", format="audio/mp3")

    if st.button("Restart"):
        st.session_state.screen = "language_selection"
        st.session_state.uploaded_file = None
        st.session_state.results = None
        st.rerun()

# Navigation Logic
if st.session_state.screen == "language_selection":
    render_language_selection()
elif st.session_state.screen == "image_upload":
    render_image_upload()
elif st.session_state.screen == "processing":
    render_processing()
elif st.session_state.screen == "results":
    render_results()


