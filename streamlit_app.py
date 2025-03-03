import streamlit as st
import easyocr
import numpy as np
from gtts import gTTS
from PIL import Image
from transformers import pipeline
from deep_translator import GoogleTranslator
import time
import base64
import streamlit.components.v1 as components

# Function to convert image to base64
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        st.error(f"Logo image not found at: {image_path}")
        return None

HEADER_TRANSLATIONS = {
    "zh-CN": {
        "title": "收到看不懂的信件吗？",
        "subtitle": "我们可以帮您翻译和解释信件内容，让您了解信件的含义和接下来该怎么做",
        "prompt": "我想要理解我的信件内容：",
        "continue": "继续 →",
        "upload_title": "拍照或上传图片",  # Switched order
        "upload_button": "上传图片",
        "camera_button": "拍照"
    },
    "ms": {
        "title": "Ada surat yang anda tidak faham?",
        "subtitle": "Kami boleh menterjemah dan menerangkan surat anda supaya anda tahu maksudnya dan apa yang perlu dilakukan seterusnya",
        "prompt": "Saya ingin memahami surat saya dalam:",
        "continue": "Teruskan →",
        "upload_title": "Ambil Gambar atau Muat Naik Imej",  # Switched order
        "upload_button": "Muat Naik Imej",
        "camera_button": "Ambil Gambar"
    },
    "ta": {
        "title": "புரியாத கடிதம் உள்ளதா?",
        "subtitle": "உங்கள் கடிதங்களை மொழிபெயர்த்து விளக்க முடியும், அதன் பொருளையும் அடுத்து என்ன செய்ய வேண்டும் என்பதையும் நீங்கள் அறிந்து கொள்ளலாம்",
        "prompt": "என் கடிதங்களை புரிந்துகொள்ள விரும்புகிறேன்:",
        "continue": "தொடரவும் →",
        "upload_title": "புகைப்படம் எடுக்கவும் அல்லது படத்தை பதிவேற்றவும்",  # Switched order
        "upload_button": "படத்தை பதிவேற்றவும்",
        "camera_button": "புகைப்படம் எடுக்கவும்"
    },
    "en": {
        "title": "Have a letter that you don't understand?",
        "subtitle": "We can translate and explain your letters to you so you know what they mean and what to do next",
        "prompt": "I want to understand my letters in:",
        "continue": "Continue →",
        "upload_title": "Take a Picture or Upload an Image",  # Switched order
        "upload_button": "Upload Image",
        "camera_button": "Take a Picture"
    }
}


# Get base64 encoded logo (replace 'logo.png' with your actual filename)
logo_b64 = get_base64_image("logo.svg")
if logo_b64:
    # Get the translations based on selected language, default to English
    selected_lang = st.session_state.get('target_language', 'en')
    translations = HEADER_TRANSLATIONS.get(selected_lang, HEADER_TRANSLATIONS['en'])

    st.markdown(f"""
        <style>
        .header-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .logo {{
            width: 184px;
            height: 55px;
            align-items: center;
        }}
        .header-text {{
            text-align: center;
            margin: 0;
            padding: 0;
        }}
        </style>
        
        <div class="header-container">
            <img src="data:image/svg+xml;base64,{logo_b64}" class="logo">
        </div>
            <h5 class="header-text">{translations['title']}</h5>
            <h6 class="header-text">{translations['subtitle']}</h6>
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

def render_language_selection():
    # Get translations
    selected_lang = st.session_state.get('target_language', 'en')
    translations = HEADER_TRANSLATIONS.get(selected_lang, HEADER_TRANSLATIONS['en'])

    st.markdown("""
        <style>
        /* Center all content */
        .block-container {
            max-width: 1000px !important;
            padding-top: 2rem !important;
            padding-bottom: 0rem !important;
        }

        /* Force horizontal layout and center content */
        [data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-wrap: nowrap !important;
            justify-content: center !important;
            gap: 15px !important;
            margin: 0 auto !important;
            padding: 0 !important;
            width: 343px !important;  /* Set fixed width to match button grid */
        }

        /* Fixed width columns */
        [data-testid="stColumn"] {
            display: inline-block !important;
            width: 164px !important;
            min-width: 164px !important;
            max-width: 164px !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* Button container */
        .button-container {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            gap: 15px !important;
            margin: 0 auto !important;
            width: 343px !important;
        }

        /* Language button styling */
        .stButton > button {
            width: 164px !important;
            height: 80px !important;
            padding: 16px !important;
            border-radius: 8px !important;
            border: 2px solid white !important;
            background: transparent !important;
            color: white !important;
            font-size: 18px !important;
            font-weight: bold !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2) !important;
            transition: all 0.3s ease-in-out !important;
        }

        /* Continue button styling */
        .continue-button .stButton > button {
            width: 343px !important;
            height: 80px !important;
            background: white !important;
            color: #1B8DFF !important;
            border: none !important;
            border-radius: 8px !important;
            font-size: 24px !important;
            font-weight: bold !important;
        }

        /* Hover effects */
        .stButton > button:hover {
            transform: scale(1.05) !important;
            box-shadow: 0px 6px 10px rgba(0, 0, 0, 0.3) !important;
        }

        .stButton > button:focus {
            background: #EAF3FF !important;
            color: #1B8DFF !important;
            border: 2px solid #1B8DFF !important;
            font-weight: bold !important;
        }

        /* Prompt text styling */
        .custom-text {
            font-size: 20px;
            text-align: center;
            margin-bottom: 20px;
            color: white;
        }

        /* Center continue button container */
        .continue-button {
            display: flex !important;
            justify-content: center !important;
            margin-top: 20px !important;
            width: 100% !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Display prompt text
    st.markdown(f'<p class="custom-text">{translations["prompt"]}</p>', unsafe_allow_html=True)

  # Language buttons container
    with st.container():
        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        
        # First row of language buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("中文", key="language_zh", use_container_width=True):
                st.session_state.target_language = "zh-CN"
                st.rerun()
        with col2:
            if st.button("Bahasa Melayu", key="language_ms", use_container_width=True):
                st.session_state.target_language = "ms"
                st.rerun()

        # Second row of language buttons
        col3, col4 = st.columns(2)
        with col3:
            if st.button("தமிழ்", key="language_ta", use_container_width=True):
                st.session_state.target_language = "ta"
                st.rerun()
        with col4:
            if st.button("English", key="language_en", use_container_width=True):
                st.session_state.target_language = "en"
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # Add minimal spacing between containers
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Continue button container
    if st.session_state.target_language:
        with st.container():
            st.markdown("""
                <style>
                /* Continue Button styles */
                .continue-wrapper {
                    display: flex;
                    justify-content: center;
                    width: 100%;
                    margin-top: 10px;
                }
                div.stButton > button:last-child {
                    width: 343px !important;
                    height: 80px !important;
                }
                </style>
                <div class="continue-wrapper">
            """, unsafe_allow_html=True)
            
            # Center the continue button using columns
            col1, col2, col3 = st.columns([1, 2, 1])
            with st.container():
                if st.button(translations["continue"], key="continue_button", use_container_width=True):
                    st.session_state.screen = "image_upload"
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
          
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
    st.markdown(f'<p class="custom-text">{translations["upload_title"]}</p>', unsafe_allow_html=True)
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

    update_progress(25, "Processing...")

    # Step 2: Summarization
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=-1)  # Force CPU only
    st.session_state.summary_text = summarizer(
        st.session_state.extracted_text, max_length=150, min_length=50, do_sample=False
    )[0]["summary_text"]

    update_progress(70, "Summarizing...")

    # Step 3: Translation
    st.session_state.translated_text = GoogleTranslator(
        source="en", target=st.session_state.target_language
    ).translate(st.session_state.summary_text)

    update_progress(90, "Translating...")

    # Step 4: Completion
    update_progress(100, "Done!")

    # Finalizing
    time.sleep(1)
    st.session_state.screen = "results"
    st.rerun()


# Results Screen
def render_results():

    st.subheader(f"Translated Text ({native_language}):")
    st.markdown(f"<div class='text-container'>{st.session_state.translated_text}</div>", unsafe_allow_html=True)
    #st.download_button("Download Translation", st.session_state.translated_text, file_name="translation.txt", mime="text/plain")

    # Generate and save audio file
    tts = gTTS(text=st.session_state.translated_text, lang=st.session_state.target_language, slow=False)
    audio_path = "output.mp3"
    tts.save(audio_path)


# Generate and save the audio file
    audio_path = "output.mp3"
    tts = gTTS(text=st.session_state.translated_text, lang=st.session_state.target_language, slow=False)
    tts.save(audio_path)

    # Convert the audio file to base64 once
    with open(audio_path, "rb") as f:
        audio_base64 = base64.b64encode(f.read()).decode()

    # HTML snippet for auto-play and play button.
    html_code = f"""
    <html>
    <head>
        <script>
        // Function to replay the audio from the beginning
        function playAgain() {{
            var audio = document.getElementById("autoplay_audio");
            if (audio) {{
            audio.currentTime = 0;
            audio.play();
            }}
        }}
        // Use a slight delay to auto-play the audio once the element exists
        setTimeout(function() {{
            var audio = document.getElementById("autoplay_audio");
            if (audio) {{
            audio.play();
            }}
        }}, 1000);
        </script>
    </head>
    <body>
        <!-- Hidden audio element -->
        <audio id="autoplay_audio" style="display:none;">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        Your browser does not support the audio element.
        </audio>
        <!-- Custom Play Again button -->
        <button onclick="playAgain()" style="
            display: block;
            width: 100%;
            padding: 15px;
            font-size: 18px;
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            margin-top: 10px;">
        🔊 Play Again
        </button>
    </body>
    </html>
    """

    components.html(html_code, height=80)

    # Restart Button
    st.button("Restart", on_click=lambda: st.session_state.update({"screen": "image_upload", "uploaded_file": None}))

    # Hide extracted text and summary in an expander
    with st.expander("Show Extracted Text and Summary"):
        st.markdown("### Extracted Text")
        st.markdown(f"<div class='text-container'>{st.session_state.extracted_text}</div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### Summary")
        st.markdown(f"<div class='text-container'>{st.session_state.summary_text}</div>", unsafe_allow_html=True)
 

# Render the appropriate screen
if st.session_state.screen == "language_selection":
    render_language_selection()
elif st.session_state.screen == "image_upload":
    render_image_upload()
elif st.session_state.screen == "processing":
    render_processing()
elif st.session_state.screen == "results":
    render_results()




#----------Change log-------------
#22 Feb:(RK)
#Change general UI based on mockup

#24 Feb:(RK)
#Change to 4 screens. Select Lang-> Upload/Cam -> Process -> Results
#Add restart button on the results screen.

#25 Feb:(RK)
#Include a progress bar with percentage value in Process screen
#Add logo on the front page

#28 Feb: (RK)
#Re-arranged 1st screen language buttons
#Enable auto play of audio once translation is completed.
#Change to large play audio again button.
#Hide extracted text and summary at the bottom of the last screen(For testing purpose)