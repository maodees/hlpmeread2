import streamlit as st
import cv2
import numpy as np

st.title("QR Code Scanner 📷")

uploaded_file = st.file_uploader("Upload a QR Code Image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Convert to OpenCV format
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    # QR Code Detector
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(img)

    if data:
        st.success(f"Decoded QR Code: {data}")
    else:
        st.error("No QR code detected. Try another image.")

