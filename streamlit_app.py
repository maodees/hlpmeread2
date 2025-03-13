import streamlit as st
import numpy as np
import pytesseract
#import easyocr
from gtts import gTTS
from PIL import Image
from transformers import pipeline
from deep_translator import GoogleTranslator
import time
import base64
import streamlit.components.v1 as components
import torch
import cv2
import os

# test
# Dictionary of letters with clear structure
letters = {
    "letter1": {
        "title": "CPF Matched Retirement Savings Scheme Notice",
        "content": """
        Central Provident Fund Board
        238B Thomson Road
        #08-00 Tower B Novena Square
        Singapore 307685

        11 March 2025

        Mr Peter Sim
        Block 123 Tampines Street 11
        #08-234
        Singapore 521123

        Dear Mr Sim,

        We are pleased to inform you about the CPF Matched Retirement Savings Scheme (MRSS), which aims to help seniors build their retirement savings.

        Under this scheme, the Government will match every dollar of cash top-up made to your CPF Retirement Account, up to $3,000 per year. This means if you contribute $3,000 to your Retirement Account in a calendar year, you will receive an additional $3,000 from the Government.

        To be eligible, you must:
        - Be aged 55 to 70 years old
        - Have CPF Retirement Account savings below the Basic Retirement Sum
        - Have an average monthly income not exceeding $4,000
        - Own property with an annual value not exceeding $13,000

        The matching will be automatically credited to your Retirement Account by the Government in the following year after your cash top-up.

        For more information or assistance, please:
        - Visit www.cpf.gov.sg
        - Call 1800-227-1188
        - Visit any CPF Service Centre

        Thank you for your attention to this matter.

        Yours sincerely,

        Mary Lim
        Director
        Retirement Savings Department
        CPF Board
        """,
        "level": "Official"
    },
    "letter2": {
        "title": "Budget 2025 Benefits Notification",
        "content": """
        Ministry of Finance
        100 High Street
        #10-01 The Treasury
        Singapore 179434

        11 March 2025

        Ms Sandra Tan
        Block 456 Serangoon Avenue 3
        #15-432
        Singapore 550456

        Dear Ms Tan,

        RE: Your Budget 2025 Benefits

        We are writing to inform you about your eligibility for various support measures under Budget 2025.

        Based on your assessments for Year of Assessment 2024, you qualify for:

        1. Cost-of-Living Special Payment
           - One-off cash payment of $800
           - To be credited to your bank account by April 2025

        2. CDC Vouchers
           - $500 worth of vouchers
           - Digital vouchers will be available via your Singpass app
           - Can be used at participating heartland merchants and supermarkets

        3. GST Assurance Package
           - Additional $300 cash payment
           - To be disbursed in July 2025

        To receive these benefits:
        - Ensure your bank account details are updated on your Singpass app
        - Link your CDC Vouchers via go.gov.sg/cdcv
        - No action required for GST Assurance Package

        For more information about Budget 2025 benefits:
        - Visit www.singaporebudget.gov.sg
        - Call 1800-222-2888
        - Email budget2025@mof.gov.sg

        Thank you for your continued support for Singapore's progress.

        Yours sincerely,

        James Wong
        Director
        Budget Policy Division
        Ministry of Finance
        """,
        "level": "Official"
    }
}

def get_letter_content(letter_id):
    """
    Get and display letter content based on letter ID
    
    Args:
        letter_id (str): The ID of the letter
        
    Returns:
        str: Combined title and content if letter exists, error message if it doesn't
    """
    print(f"in url = 1")
    
    # Get query parameters if letter_id is not provided
    if not letter_id:
        query_params = st.experimental_get_query_params()
        letter_id = query_params.get('letter', [None])[0]

        # Check if letter exists and return content
        if letter_id and letter_id in letters:
            letter = letters[letter_id]
            title = letter["title"]
            content = letter["content"]
    
            # Store in session state for later use
            st.session_state['current_title'] = title
            st.session_state['current_content'] = content
    
            # Display content
            #st.header(title)
            #st.markdown(content)
    
            # Return combined text
            return f"{title}\n\n{content}"
        else:
            error_message = "Letter not found. Available letters: " + ", ".join(letters.keys())
            st.info("Please scan a valid letter QR code")
            st.write("Available letters:", list(letters.keys()))
            return error_message

# Example usage:
# text = get_letter_content("letter1")  # Will return and display the CPF letter
# text = get_letter_content("letter2")  # Will return and display the Budget letter
# text = get_letter_content("invalid_letter")  # Will return and display error message


#Change OCR reader
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def enhance_image_for_qr(image):
    """Enhance image for better QR code detection"""
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
        
    # Apply different preprocessing techniques
    # 1. Basic thresholding
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    
    # 2. Adaptive thresholding
    adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    # 3. Otsu's thresholding
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # 4. Contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    return [gray, binary, adaptive, otsu, enhanced]

def detect_qr_code(image):
    """Try multiple methods to detect QR code"""
    # Initialize QR code detector
    qr_detector = cv2.QRCodeDetector()
    
    # Try original image first
    retval, decoded_info, points, straight_qrcode = qr_detector.detectAndDecodeMulti(image)
    if retval and decoded_info and any(decoded_info):
        return decoded_info[0]
    
    # Get enhanced versions of the image
    enhanced_images = enhance_image_for_qr(image)
    
    # Try different image sizes
    scales = [1.5, 2.0, 0.5]  # Try larger and smaller versions
    
    # Try each enhanced image
    for enhanced in enhanced_images:
        # Try original size
        retval, decoded_info, points, straight_qrcode = qr_detector.detectAndDecodeMulti(enhanced)
        if retval and decoded_info and any(decoded_info):
            return decoded_info[0]
            
        # Try different scales
        for scale in scales:
            width = int(enhanced.shape[1] * scale)
            height = int(enhanced.shape[0] * scale)
            resized = cv2.resize(enhanced, (width, height))
            
            retval, decoded_info, points, straight_qrcode = qr_detector.detectAndDecodeMulti(resized)
            if retval and decoded_info and any(decoded_info):
                return decoded_info[0]
    
    return None

def perform_ocr(image):
    try:
        # Convert to PIL Image if not already
        if not isinstance(image, Image.Image):
            image = Image.open(image)
        
        # Convert to RGB if image is in RGBA format
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        
        # Convert PIL Image to numpy array
        img_array = np.array(image)
        
        #try:
            # Try enhanced QR detection
        #    qr_result = detect_qr_code(img_array)
            
        #    if qr_result:
                # QR code found
        #        print("QR Code detected. Content:")
        #        print("-" * 50)
        #        print(f"Output text: {qr_result}")
        #        print("-" * 50)
        #        return qr_result
                
        #except Exception as qr_error:
        #    print(f"QR detection error: {str(qr_error)}")
            # Continue to OCR if QR detection fails
        
        # Convert to grayscale
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Apply thresholding to improve OCR accuracy
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Convert back to PIL Image
        binary_pil = Image.fromarray(binary)
        
        # OCR configuration
        custom_config = r'--oem 3 --psm 1'
        
        # Perform OCR
        text = pytesseract.image_to_string(binary_pil, lang='eng', config=custom_config)
        
        print("OCR Result:")
        print("-" * 50)
        print(f"Output text: {text.strip()}")
        print("-" * 50)
        
        return text.strip()
            
    except Exception as e:
        error_message = f"Error in image processing: {str(e)}"
        print("-" * 50)
        print(f"Error: {error_message}")
        print("-" * 50)
        return str(e)

# Example usage:
# result = perform_ocr('path_to_image.png')

# end OCR reader

HEADER_TRANSLATIONS = {
    "zh-CN": {
        "title": "收到看不懂的信件吗？",
        "subtitle": "我们帮助您翻译和解释",
        "prompt": "用以下语言解释：",
        "continue": "继续 →",
        "disclaimer": "系统不会存储任何个人数据或信件",
        "upload_title": "拍照或上传图片",  
        "upload_button": "上传图片",
        "camera_button": "拍照",
        "Processing": "处理中，请稍候。",
        "Summary": "翻译主要内容",
        "Back": "返回",
        "Retry": "再试"
    },
    "ms": {
        "title": "Ada surat yang anda tidak faham?",
        "subtitle": "Kami membantu untuk menterjemah dan menerangkannya kepada anda",
        "prompt": "Terangkan surat saya dalam:",
        "continue": "Teruskan →",
        "disclaimer": "Sistem Tiada data peribadi atau surat akan disimpan",
        "upload_title": "Ambil Gambar atau Muat Naik Imej",
        "upload_button": "Muat Naik Imej",
        "camera_button": "Ambil Gambar",
        "Processing": "Memproses, Sila tunggu.",
        "Summary": "Menterjemah isi utama",
        "Back": "kembali",
        "Retry": "Cuba lagi"
    },
    "ta": {
        "title": "புரியாத கடிதம் உள்ளதா?",
        "subtitle": "அதை உங்களுக்கு மொழிபெயர்க்கவும் விளக்கவும் நாங்கள் உதவுகிறோம்.",
        "prompt": "எனது கடிதத்தை விளக்கவும்",
        "continue": "தொடரவும் →",
        "disclaimer": "அமைப்பு தனிப்பட்ட தரவு அல்லது கடிதங்கள் எதுவும் சேமிக்கப்படாது.",
        "upload_title": "புகைப்படம் எடுக்கவும் அல்லது படத்தை பதிவேற்றவும்", 
        "upload_button": "படத்தை பதிவேற்றவும்",
        "camera_button": "புகைப்படம் எடுக்கவும்",
        "Processing": "செயலாக்கம் நடைபெறுகிறது, தயவுசெய்து காத்திருக்கவும்.",
        "Summary": "முக்கிய உள்ளடக்கத்தை மொழிபெயர்க்கவும்",
        "Back": "திரும்ப",
        "Retry": "மீண்டும் முயற்சிக்கவும்"
    },
    "en": {
        "title": "Have a letter that you don't understand?",
        "subtitle": "We help to translate and explain it to you",
        "prompt": "Explain my letter in:",
        "continue": "Continue →",
        "disclaimer": "No personal data or letters will be stored",
        "upload_title": "Take a Picture or Upload an Image",  # Switched order
        "upload_button": "Upload Image",
        "camera_button": "Take a Picture",
        "Processing": "Processing, Please wait.",
        "Summary": "Translated Summary",
        "Back": "Back",
        "Retry": "Try Again"
    }
}
# Function to convert image to base64
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        st.error(f"Logo image not found at: {image_path}")
        return None
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
              
    .text-container {
        padding: 1rem !Important;
        background-color: white !Important; 
        border-radius: 10px !Important;
        margin: 1rem 0 !Important;
        color: black !Important;
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
            width: 100% !important;
            height: 80px !important;
            padding: 16px !important;
            border-radius: 8px !important;
            border: 2px solid white !important;
            background: white !important;
            color: black !important;
            font-size: 5px !important;
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
            
 
        /* Hover effects */
        .stButton > button:hover {
            transform: scale(1.05) !important;
            box-shadow: 0px 6px 10px rgba(0, 0, 0, 0.3) !important;
        }
        .stButton > button:focus,
        .stButton > button:focus-visible,
        .stButton > button:active {
            background: #EAF3FF !important;
            color: #1B8DFF !important;
            border: 2px solid #1B8DFF !important;
            font-weight: bold !important;
            outline: none !important;
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
    #st.markdown(f'<h5 style="text-align:center; color: white;">{translations["title"]}</h5>', unsafe_allow_html=True)
    #st.markdown(f'<h5 style="text-align:center; color: white; font-size: 28px; margin-left: 30px;">{translations["title"]}</h5>', unsafe_allow_html=True)
    #st.markdown(f'<h6 style="text-align:center; color: white; font-size: 22px; margin-left: 30px;">{translations["subtitle"]}</h6>', unsafe_allow_html=True)
    st.markdown("""
        <style>
        /* Center all content */
        .block-container {
            max-width: 1000px !important;
            padding-top: 5rem !important;  /* This is the key line that shifts everything down */
            padding-bottom: 0rem !important;
            margin-top: 1rem !important;   /* This also adds some additional spacing */
        }

        }
        </style>
    """, unsafe_allow_html=True)
    # Display prompt text
    #st.markdown(f'<p class="custom-text">{translations["prompt"]}</p>', unsafe_allow_html=True)
    #st.markdown(f'<h6 style="text-align:center; color: white; font-size: 16px; margin-left: 30px;">{translations["prompt"]}</h6>', unsafe_allow_html=True)
  # Language buttons container
    with st.container():
        st.markdown('<div class="button-container">', unsafe_allow_html=True)

        # Single column for language buttons
        if st.button("中文", key="language_zh", use_container_width=True):
            st.session_state.target_language = "zh-CN"
            get_letter_content(None)
            if st.session_state.get('current_title', '').strip(): 
                st.session_state.screen = "flushscreen"
                st.rerun()
            else:
                st.session_state.screen = "image_upload"
                st.rerun()

        if st.button("Bahasa Melayu", key="language_ms", use_container_width=True):
            st.session_state.target_language = "ms"
            get_letter_content(None)
            if st.session_state.get('current_title', '').strip(): 
                st.session_state.screen = "flushscreen"
                st.rerun()
            else:
                st.session_state.screen = "image_upload"
                st.rerun()

        if st.button("தமிழ்", key="language_ta", use_container_width=True):
            st.session_state.target_language = "ta"
            get_letter_content(None)
            if st.session_state.get('current_title', '').strip(): 
                st.session_state.screen = "flushscreen"
                st.rerun()
            else:
                st.session_state.screen = "image_upload"
                st.rerun()

        if st.button("English", key="language_en", use_container_width=True):
            st.session_state.target_language = "en"
            get_letter_content(None)
            if st.session_state.get('current_title', '').strip(): 
                st.session_state.screen = "flushscreen"
                st.rerun()
            else:
                st.session_state.screen = "image_upload"
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
    # Continue button container
    #if st.session_state.target_language:
     #   with st.container():
     #       st.markdown("""
     #           <style>
     #           /* Continue Button styles */
     #           .continue-wrapper {
     #               display: flex;
     #               justify-content: center;
     #               width: 100%;
     #               margin-top: 10px;
     #           }
     #           div.stButton > button:last-child {
     #               width: 343px !important;
     #               height: 80px !important;
     #           }
     #           </style>
     #           <div class="continue-wrapper">
     #       """, unsafe_allow_html=True)
            
            # Center the continue button using columns
     #       col1, col2, col3 = st.columns([1, 2, 1])
            #with st.container():
            #    if st.button(translations["continue"], key="continue_button", use_container_width=True):
            #        get_letter_content(None)
            #        if st.session_state.get('current_title', '').strip(): 
            #            st.session_state.screen = "flushscreen"
            #            st.rerun()
            #        else:
            #            st.session_state.screen = "image_upload"
            #            st.rerun()
            #st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <style>
    .footer {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        text-align: center;
        color: white;
        font-size: 16px;
        background-color: transparent;
        padding: 10px;
    }}
    </style>
    <div class="footer">{translations["disclaimer"]}</div> """, unsafe_allow_html=True)

            
          
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
   
    #st.markdown(f'<p class="custom-text">{translations["upload_title"]}</p>', unsafe_allow_html=True)
    st.markdown(f'<h6 style="text-align:center; color: white; font-size: 22px; margin-left: 30px">{translations["upload_title"]}</h6>', unsafe_allow_html=True)
    # File uploader
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        st.session_state.screen = "flushscreen"
        st.rerun()  # Rerun the app to move to the next screen

# Force layout update and push button down using multiple empty <style> tags
    for _ in range(5):  # Add multiple empty <style> tags
        st.markdown("""<style></style>""", unsafe_allow_html=True)

# Reserve space for the Retry button at the bottom
    bottom_container = st.empty()

    # Add the Back button to the bottom container
    with bottom_container.container():  # Use .container() to ensure proper rendering
        # Create columns to center the button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(translations["Back"], key="retry_button", use_container_width=True):
                st.session_state.screen = "language_selection"
                st.rerun()  # Rerun the app to move to the language selection screen
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <style>
    .footer {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        text-align: center;
        color: white;
        font-size: 16px;
        background-color: transparent;
        padding: 10px;
    }}
    </style>
    <div class="footer">{translations["disclaimer"]}</div> """, unsafe_allow_html=True)

#Flush screen for QR code flow
def render_flushscreen():
    # First, create a full-screen white/custom color overlay
    st.markdown("""
        <style>
        #root > div:first-child {
            background: linear-gradient(135deg, #1E2A38, #2C3E50) !important;
        }
        .fullscreen-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: linear-gradient(135deg, #1E2A38, #2C3E50);
            z-index: 999999;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        </style>
        <div class="fullscreen-overlay"></div>
        """, unsafe_allow_html=True)
    # Clear all existing elements
    st.empty()
    for _ in range(10):  # Multiple empty calls to ensure clearing
        st.empty()
    time.sleep(0.5)  # 1 second delay
    st.session_state.screen = "processing"
    st.rerun()


# Processing Screen
def render_processing():
    st.markdown(f'<h5 style="text-align: center; color: white; margin-left: 30px;">{translations["Processing"]}</h5>', unsafe_allow_html=True)
    st.markdown(f"""
    <style>
    .footer {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        text-align: center;
        color: white;
        font-size: 16px;
        background-color: transparent;
        padding: 10px;
    }}
    </style>
    <div class="footer">{translations["disclaimer"]}</div> """, unsafe_allow_html=True)
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
    #image = Image.open(st.session_state.uploaded_file)
    #img_array = np.array(image)
    #st.session_state.extracted_text = "\n".join([res[1] for res in results])
    
    
    if st.session_state.get('current_title', '').strip():
        print("scan qr hard code")
        st.session_state.extracted_text = st.session_state.get('current_content', '')
    else:
        print("upload image")
        image = Image.open(st.session_state.uploaded_file)
        img_array = np.array(image)
        st.session_state.extracted_text = perform_ocr(image)
   
    update_progress(25, "Processing...")
    # Step 2: Summarization
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=0 if torch.cuda.is_available() else -1) #TAP ON GPU
    #st.session_state.summary_text = summarizer(st.session_state.extracted_text, max_length=150, min_length=50, do_sample=False)[0]["summary_text"]
    # For more concise summaries:
    st.session_state.summary_text = summarizer(
    st.session_state.extracted_text,
    max_length=200,
    min_length=75,
    num_beams=4,
    length_penalty=1.5,
    no_repeat_ngram_size=3,
    early_stopping=True,
    do_sample=False,
    temperature=0.2
)[0]["summary_text"]
    update_progress(70, "Summarizing...")
    # Step 3: Translation
    print("in translator")
    print(st.session_state.target_language)
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
    #st.subheader(f"{translations['Summary']}:")
    st.markdown(f'<h6 style="text-align: left; color: white;">{translations["Summary"]} :</h6>', unsafe_allow_html=True)
    st.session_state.translated_text = st.session_state.translated_text.replace("美元", "新元")
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
            padding: 25px;
            font-size: 18px;
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            margin-top: 25px;">
        🔊 
        </button>
    </body>
    </html>
    """
    components.html(html_code, height=100)
# Display the Restart button only at the end of the process
    # Continue button container
    if st.session_state.target_language:
                 
            # Center the continue button using columns
            col1, col2, col3 = st.columns([1, 1, 1])
            with st.container():
                if st.button(translations["Retry"], key="button-container", use_container_width=True):
                    #st.session_state.screen = "language_selection"
                    #st.rerun()
                    st.markdown('<meta http-equiv="refresh" content="0; url=https://read-for-me.com">', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
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
elif st.session_state.screen == "flushscreen":
    render_flushscreen()
elif st.session_state.screen == "image_upload":
    render_image_upload()
elif st.session_state.screen == "processing":
    render_processing()
elif st.session_state.screen == "results":
    render_results()