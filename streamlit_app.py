import os
import sys
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(page_title="Visiting Card OCR", page_icon="📇", layout="wide")
st.title("📇 Visiting Card OCR")
st.caption("Upload a visiting card to extract contact details.")


def preprocess_image(image: Image.Image) -> Image.Image:
    MIN_DIM = 1200
    w, h = image.size
    if max(w, h) < MIN_DIM:
        scale = MIN_DIM / max(w, h)
        image = image.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    gray = image.convert("L")
    gray = ImageEnhance.Contrast(gray).enhance(2.0)
    gray = ImageEnhance.Sharpness(gray).enhance(2.0)
    gray = gray.filter(ImageFilter.SHARPEN)
    return gray.convert("RGB")


def run_tesseract(image: Image.Image) -> list:
    import pytesseract
    from pytesseract import Output

    data = pytesseract.image_to_data(image, output_type=Output.DICT)
    groups: dict = {}
    for i in range(len(data["text"])):
        word = data["text"][i].strip()
        conf = float(data["conf"][i])
        if conf < 0 or not word:
            continue
        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        if key not in groups:
            groups[key] = {
                "words": [],
                "left": data["left"][i],
                "top": data["top"][i],
                "right": data["left"][i] + data["width"][i],
                "bottom": data["top"][i] + data["height"][i],
                "confs": [],
            }
        g = groups[key]
        g["words"].append(word)
        g["right"] = max(g["right"], data["left"][i] + data["width"][i])
        g["bottom"] = max(g["bottom"], data["top"][i] + data["height"][i])
        g["left"] = min(g["left"], data["left"][i])
        g["top"] = min(g["top"], data["top"][i])
        g["confs"].append(conf)

    lines = []
    for key in sorted(groups):
        g = groups[key]
        if not g["words"]:
            continue
        l, t, r, b = g["left"], g["top"], g["right"], g["bottom"]
        conf = round(sum(g["confs"]) / len(g["confs"]) / 100.0, 4)
        bbox = [[l, t], [r, t], [r, b], [l, b]]
        lines.append({"text": " ".join(g["words"]), "bbox": bbox, "confidence": conf})
    return lines


FIELD_ICONS = {
    "name": ("👤", "Name"),
    "designation": ("💼", "Designation"),
    "company": ("🏢", "Company"),
    "phone": ("📞", "Phone"),
    "email": ("✉️", "Email"),
    "website": ("🌐", "Website"),
    "address": ("📍", "Address"),
}

uploaded_file = st.file_uploader(
    "Upload card image", type=["jpg", "jpeg", "png", "webp"]
)

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    col_img, col_result = st.columns([1, 1])

    with col_img:
        st.image(image, caption="Uploaded Card", use_container_width=True)

    with col_result:
        if st.button("Extract Contact Info", type="primary", use_container_width=True):
            with st.spinner("Running OCR..."):
                try:
                    processed = preprocess_image(image)
                    lines = run_tesseract(processed)

                    from extractor import extract_fields
                    result = extract_fields(lines)
                    data = result["data"]

                    if not data:
                        st.warning("No fields detected — try a clearer, higher-resolution photo.")
                    else:
                        st.success("Extraction complete!")
                        for field, (icon, label) in FIELD_ICONS.items():
                            val = data.get(field)
                            if val is None:
                                continue
                            if isinstance(val, list):
                                display = "  \n".join(val)
                            else:
                                display = str(val)
                            st.markdown(f"**{icon} {label}**")
                            st.markdown(
                                f"<div style='background:#f0f2f6;padding:8px 12px;"
                                f"border-radius:6px;margin-bottom:8px'>{display}</div>",
                                unsafe_allow_html=True,
                            )

                        with st.expander("Raw OCR text"):
                            st.text("\n".join(l["text"] for l in lines))

                except Exception as e:
                    st.error(f"OCR failed: {e}")
                    st.info("Make sure the image is a clear photo of a visiting card.")
