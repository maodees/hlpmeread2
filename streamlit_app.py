import streamlit as st
import cv2
import numpy as np
from streamlit_webrtc import VideoProcessorBase, webrtc_streamer

class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.detector = cv2.QRCodeDetector()
    
    def recv(self, frame):
        # Convert the frame to numpy array for processing
        img = frame.to_ndarray(format="bgr24")
        
        # Convert to grayscale for better detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect and decode QR code
        data, bbox, _ = self.detector.detectAndDecode(gray)
        
        if data:
            # Draw bounding box around QR code
            if bbox is not None:
                n = len(bbox)
                for j in range(n):
                    cv2.line(img, tuple(bbox[j][0]), tuple(bbox[(j + 1) % n][0]), (0, 255, 0), 3)
            
            # Display QR code text on the frame
            cv2.putText(img, data, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        
        return frame

st.title("Real-Time QR Code Scanner with Webcam")

webrtc_streamer(key="example", video_processor_factory=VideoProcessor)
