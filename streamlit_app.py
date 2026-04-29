import streamlit as st
from PIL import Image
import numpy as np

st.title("OCR Full Test App")

uploaded_file = st.file_uploader("Upload image", type=["jpg","png","jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image)

    if st.button("Run OCR"):
        with st.spinner("Loading OCR..."):
            import easyocr  # import inside to delay memory usage

            reader = easyocr.Reader(["en"], gpu=False)
            result = reader.readtext(np.array(image))

            st.write(result)