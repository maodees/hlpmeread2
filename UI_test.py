import streamlit as st

# Custom CSS for button styling and layout adjustments
st.markdown(
    """
    <style>
    /* Center align the button container */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: nowrap !important;
        justify-content: center !important;
        gap: 35px !important; /* Horizontal spacing between columns */
        margin: 0 auto !important; /* Center the container horizontally */
        padding: 0 !important;
        width: fit-content !important; /* Fit content width */
    }

    /* Force columns to maintain equal width */
    [data-testid="stColumn"] {
        display: inline-block !important;
        width: 140px !important;
        min-width: 140px !important;
        max-width: 140px !important;
        vertical-align: top;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Remove spacing from buttons */
    [data-testid="stButton"] {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Default button styles */
    .stButton > button {
        width: 164px;
        height: 80px;
        padding: 16px;
        border-radius: 8px;
        border: 2px solid white;
        background: transparent;
        color: white;
        font-size: 18px;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease-in-out;
        cursor: pointer;
    }

    /* Hover effect */
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0px 6px 10px rgba(0, 0, 0, 0.3);
    }

    /* Selected button style */
    .stButton > button:focus {
        background: #EAF3FF !important;
        color: #1B8DFF !important;
        font-size: 20px;
        font-weight: bold;
        border: 2px solid #1B8DFF !important;
    }

    /* Custom text styling */
    .custom-text {
        font-size: 20px;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state for selected language
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "English"

# Language options in two rows
languages = [["中文", "Melayu"], ["தமிழ்", "English"]]

# Render header text
st.markdown('<p class="custom-text">I want to understand my letters in:</p>', unsafe_allow_html=True)

# Function to update selected language
def update_language(lang):
    st.session_state.selected_language = lang

# Render buttons in a two-column layout
for row in languages:
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(row[0], use_container_width=True):
            update_language(row[0])

    with col2:
        if st.button(row[1], use_container_width=True):
            update_language(row[1])

# Display the currently selected language
st.write(f"Selected Language: {st.session_state.selected_language}")