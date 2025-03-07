import streamlit as st
from paddleocr import PaddleOCR
from PIL import Image
import io

# Initialize the PaddleOCR model
ocr = PaddleOCR(use_angle_cls=True, lang='en')  # Use `en` for English. Change language code if needed.

st.title("OCR with PaddleOCR")

# File uploader to upload an image
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Open the image using PIL
    image = Image.open(uploaded_file)
    
    # Convert the uploaded image to a format compatible with PaddleOCR
    image_path = "uploaded_image.jpg"
    image.save(image_path)

    # Perform OCR using PaddleOCR
    result = ocr.ocr(image_path, cls=True)

    # Display the image with OCR results
    st.image(image, caption="Uploaded Image", use_column_width=True)
    
    # Extract and display the text from the result
    extracted_text = "\n".join([line[1][0] for line in result[0]])

    if extracted_text:
        st.success("Extracted Text:")
        st.write(extracted_text)
    else:
        st.warning("No text detected in the image.")
