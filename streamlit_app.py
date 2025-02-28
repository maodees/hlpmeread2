import streamlit as st

# Custom CSS to force no wrapping, remove gaps, and eliminate extra padding/margins
st.markdown(
    """
    <style>
    /* Prevent columns from wrapping and remove gaps */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 0px;
    }
    /* Remove padding/margin on the column containers */
    [data-testid="stColumn"] {
        padding: 0 !important;
        margin: 0 !important;
    }
    /* Remove margin/padding on the button container */
    [data-testid="stButton"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    /* Adjust the buttons themselves */
    .stButton>button {
        width: 70%;   /* Adjust width as needed */
        margin: 0 !important;  /* Remove extra margin */
        font-size: 12px;
        padding: 4px 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def render_language_selection():
    st.subheader("Select Your Language")

    # First row of buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("English"):
            st.session_state.target_language = "en"
            st.write("You selected English!")
    with col2:
        if st.button("中文"):
            st.session_state.target_language = "zh-CN"
            st.write("You selected Chinese!")

    # Second row of buttons
    col3, col4 = st.columns(2)
    with col3:
        if st.button("Español"):
            st.session_state.target_language = "es"
            st.write("You selected Spanish!")
    with col4:
        if st.button("Français"):
            st.session_state.target_language = "fr"
            st.write("You selected French!")

render_language_selection()
