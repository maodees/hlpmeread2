import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image

# Streamlit title
st.title("QR Code Scanner")

# File uploader for image
uploaded_file = st.file_uploader("Upload a QR Code Image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Open the image using PIL
    image = Image.open(uploaded_file)
    
    # Display the uploaded image
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Decode QR Code using pyzbar
    decoded_objects = decode(image)
    if decoded_objects:
        for obj in decoded_objects:
            # Display the decoded data
            st.success(f"Decoded QR Code Data: {obj.data.decode('utf-8')}")
    else:
        st.warning("No QR Code detected.")
