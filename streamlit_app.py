import streamlit as st

st.markdown("""
<style>
/* Prevent horizontal blocks from wrapping */
[data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
    gap: 0px !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Force columns to be inline-block with fixed width */
[data-testid="stColumn"] {
    display: inline-block !important;
    width: 140px !important;      /* fixed width for each column */
    min-width: 140px !important;
    max-width: 140px !important;
    vertical-align: top;
    margin: 0 !important;
    padding: 0 !important;
}

/* Remove default vertical spacing in vertical blocks */
[data-testid="stVerticalBlock"] > div {
    margin: 0 !important;
    padding: 0 !important;
}

/* Remove spacing from the button container */
[data-testid="stButton"] {
    margin: 0 !important;
    padding: 0 !important;
}

/* Button styling */
.stButton > button {
    width: 120px !important;      /* fixed small width for the button */
    font-size: 12px;
    padding: 2px 4px;
    margin: 0 !important;
}
</style>
""", unsafe_allow_html=True)

st.subheader("Select Your Language")

# Create two rows manually using st.columns; with the fixed-width columns, two will remain side by side
row1 = st.columns(2)
with row1[0]:
    if st.button("English"):
        st.session_state.target_language = "en"
with row1[1]:
    if st.button("中文"):
        st.session_state.target_language = "zh-CN"

row2 = st.columns(2)
with row2[0]:
    if st.button("Español"):
        st.session_state.target_language = "es"
with row2[1]:
    if st.button("Français"):
        st.session_state.target_language = "fr"
