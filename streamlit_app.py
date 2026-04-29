import streamlit as st
from PIL import Image
import numpy as np

# python-bidi 0.4.x puts get_display in bidi.algorithm, but easyocr 1.7.x
# expects it at the top-level bidi module. Patch before easyocr imports it.
import bidi
import bidi.algorithm
if not hasattr(bidi, 'get_display'):
    bidi.get_display = bidi.algorithm.get_display

st.title("OCR Full Test App")

uploaded_file = st.file_uploader("Upload image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image)

    if st.button("Run OCR"):
        with st.spinner("Loading OCR..."):
            import easyocr

            reader = easyocr.Reader(["en"], gpu=False)
            result = reader.readtext(np.array(image))

            st.write(result)
