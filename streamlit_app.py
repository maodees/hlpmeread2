import streamlit as st
import cv2
import numpy as np
from pyzbar.pyzbar import decode

st.title("QR Code Scanner from Image")

uploaded_file = st.file_uploader("Upload a QR Code Image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Convert to OpenCV format
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    # Decode QR code using pyzbar
    decoded_objects = decode(img)

    if decoded_objects:
        for obj in decoded_objects:
            st.success(f"Decoded QR Code: {obj.data.decode('utf-8')}")
    else:
        st.error("No QR code detected.")
