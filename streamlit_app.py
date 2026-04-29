import os
import sys
import time
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(page_title="Card Scanner — OCR", page_icon="📇", layout="centered")

# Hide Streamlit chrome; style the upload widget
st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; max-width: 640px !important; }
[data-testid="stFileUploader"] {
    border: 2px dashed #cbd5e1; border-radius: 14px;
    background: #fafbff; padding: 4px;
}
[data-testid="stFileUploader"]:hover { border-color: #3b5bdb; background: #eef2ff; }
div.stButton > button {
    width: 100%; padding: 14px;
    background: linear-gradient(135deg,#1e3a8a,#3b5bdb) !important;
    color: #fff !important; border: none !important; border-radius: 13px !important;
    font-size: 15px !important; font-weight: 700 !important;
    box-shadow: 0 4px 16px rgba(59,91,219,.35) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#1e3a8a 0%,#3b5bdb 60%,#6366f1 100%);
            padding:36px 24px 60px;text-align:center;margin:-1rem -1rem 0;border-radius:0 0 0 0">
  <div style="display:inline-block;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.25);
              color:#e0e7ff;font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
              padding:5px 14px;border-radius:20px;margin-bottom:14px;font-family:Inter,sans-serif">
    ✦ AI-Powered OCR
  </div>
  <h1 style="font-size:30px;font-weight:800;color:#fff;margin:0 0 10px;font-family:Inter,sans-serif">
    📇 Card Scanner
  </h1>
  <p style="font-size:14px;color:rgba(255,255,255,.7);max-width:340px;margin:0 auto;
            line-height:1.6;font-family:Inter,sans-serif">
    Instantly extract contact details from any visiting card using smart OCR.
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def preprocess(image: Image.Image) -> Image.Image:
    w, h = image.size
    if max(w, h) > 2400:
        s = 2400 / max(w, h)
        image = image.resize((int(w * s), int(h * s)), Image.LANCZOS)
        w, h = image.size
    if max(w, h) < 1200:
        s = 1200 / max(w, h)
        image = image.resize((int(w * s), int(h * s)), Image.LANCZOS)
    g = image.convert("L")
    g = ImageEnhance.Contrast(g).enhance(2.0)
    g = ImageEnhance.Sharpness(g).enhance(2.0)
    g = g.filter(ImageFilter.SHARPEN)
    return g.convert("RGB")


def tesseract_lines(image: Image.Image) -> list:
    import pytesseract
    from pytesseract import Output
    d = pytesseract.image_to_data(image, output_type=Output.DICT)
    groups: dict = {}
    for i in range(len(d["text"])):
        word = d["text"][i].strip()
        conf = float(d["conf"][i])
        if conf < 0 or not word:
            continue
        key = (d["block_num"][i], d["par_num"][i], d["line_num"][i])
        if key not in groups:
            groups[key] = {
                "words": [], "confs": [],
                "l": d["left"][i], "t": d["top"][i],
                "r": d["left"][i] + d["width"][i],
                "b": d["top"][i]  + d["height"][i],
            }
        g = groups[key]
        g["words"].append(word)
        g["confs"].append(conf)
        g["r"] = max(g["r"], d["left"][i] + d["width"][i])
        g["b"] = max(g["b"], d["top"][i]  + d["height"][i])
        g["l"] = min(g["l"], d["left"][i])
        g["t"] = min(g["t"], d["top"][i])
    lines = []
    for key in sorted(groups):
        g = groups[key]
        conf = round(sum(g["confs"]) / len(g["confs"]) / 100, 4)
        l, t, r, b = g["l"], g["t"], g["r"], g["b"]
        lines.append({"text": " ".join(g["words"]),
                      "bbox": [[l,t],[r,t],[r,b],[l,b]],
                      "confidence": conf})
    return lines


def build_result_html(result: dict, proc_ms: int, overall: float) -> str:
    data  = result["data"]
    confs = result["confidence"]

    FIELDS = [
        ("name",        "👤", "Name",        "#eff6ff"),
        ("designation", "💼", "Designation", "#f0fdf4"),
        ("company",     "🏢", "Company",     "#fef3c7"),
        ("phone",       "📞", "Phone",       "#ecfdf5"),
        ("email",       "✉️", "Email",       "#fdf4ff"),
        ("website",     "🌐", "Website",     "#f0f9ff"),
        ("address",     "📍", "Address",     "#fff7ed"),
    ]

    def bar_color(v):
        return "#3b5bdb" if v >= 0.8 else "#f59e0b" if v >= 0.6 else "#ef4444"

    def fmt_val(key, items):
        if key == "phone":
            return "<br>".join(f'<a href="tel:{v}" style="color:#3b5bdb;text-decoration:none;font-weight:600">{v}</a>' for v in items)
        if key == "email":
            return "<br>".join(f'<a href="mailto:{v}" style="color:#3b5bdb;text-decoration:none;font-weight:600">{v}</a>' for v in items)
        if key == "website":
            def _a(v):
                h = v if v.startswith("http") else "https://" + v
                return f'<a href="{h}" target="_blank" style="color:#3b5bdb;text-decoration:none;font-weight:600">{v}</a>'
            return "<br>".join(_a(v) for v in items)
        return "<br>".join(str(v) for v in items)

    rows = ""
    for key, icon, label, bg in FIELDS:
        val = data.get(key)
        if val is None:
            continue
        items = val if isinstance(val, list) else [val]
        display = fmt_val(key, items)
        fc = confs.get(key)
        conf_html = ""
        if fc is not None:
            pct = round(fc * 100)
            col = bar_color(fc)
            conf_html = f"""
            <div style="display:flex;align-items:center;gap:7px;margin-top:6px">
              <div style="height:4px;border-radius:4px;background:#f1f5f9;width:72px;overflow:hidden">
                <div style="height:100%;border-radius:4px;width:{pct}%;background:{col}"></div>
              </div>
              <span style="font-size:10px;color:#cbd5e1;font-weight:600">{pct}% confidence</span>
            </div>"""
        rows += f"""
        <div style="display:flex;align-items:flex-start;gap:14px;padding:14px 24px;
                    border-bottom:1px solid #f1f5f9">
          <div style="width:38px;height:38px;border-radius:10px;background:{bg};
                      display:flex;align-items:center;justify-content:center;
                      font-size:17px;flex-shrink:0">{icon}</div>
          <div style="flex:1;min-width:0">
            <div style="font-size:10px;color:#94a3b8;text-transform:uppercase;
                        letter-spacing:.08em;font-weight:700;margin-bottom:3px">{label}</div>
            <div style="font-size:14px;color:#1e293b;font-weight:500;
                        word-break:break-word;line-height:1.5">{display}</div>
            {conf_html}
          </div>
        </div>"""

    if not rows:
        rows = """<div style="text-align:center;padding:40px 24px;color:#94a3b8;font-size:14px">
                    <div style="font-size:40px;margin-bottom:12px">😕</div>
                    No fields detected — try a clearer photo.
                  </div>"""

    overall_pct = round(overall * 100)
    overall_col = bar_color(overall)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Inter', sans-serif; background: transparent; }}
  a:hover {{ text-decoration: underline !important; }}
</style>
</head>
<body>
<div style="background:#fff;border-radius:20px;overflow:hidden;
            box-shadow:0 4px 24px rgba(0,0,0,.09),0 1px 4px rgba(0,0,0,.05)">
  <!-- Header -->
  <div style="background:linear-gradient(135deg,#1e3a8a,#3b5bdb);
              padding:20px 24px;display:flex;align-items:center;justify-content:space-between">
    <div style="display:flex;align-items:center;gap:10px">
      <div style="width:36px;height:36px;background:rgba(255,255,255,.15);border-radius:10px;
                  display:flex;align-items:center;justify-content:center;font-size:18px">📋</div>
      <div>
        <div style="font-size:15px;font-weight:700;color:#fff">Extracted Info</div>
        <div style="font-size:11px;color:rgba(255,255,255,.6)">Contact details from card</div>
      </div>
    </div>
    <span style="background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.3);
                 color:#fff;font-size:11px;font-weight:600;padding:4px 12px;border-radius:20px">
      ✓ Success
    </span>
  </div>
  <!-- Fields -->
  {rows}
  <!-- Footer -->
  <div style="display:flex;justify-content:space-between;font-size:11px;color:#cbd5e1;
              padding:14px 24px;border-top:1px solid #f1f5f9;font-weight:500">
    <span style="color:{overall_col}">⬤ Overall confidence: {overall_pct}%</span>
    <span>⚡ {proc_ms} ms</span>
  </div>
</div>
</body>
</html>"""


# ── Upload + scan UI ──────────────────────────────────────────────────────────

uploaded = st.file_uploader(
    "📤 Drop card image here or click to browse",
    type=["jpg", "jpeg", "png", "webp"],
)

if uploaded:
    col1, col2 = st.columns([1, 1])
    with col1:
        image = Image.open(uploaded).convert("RGB")
        st.image(image, use_container_width=True)
    with col2:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        scan = st.button("🔍  Scan Card", width='stretch')

    if scan:
        with st.spinner("Running OCR…"):
            t0 = time.time()
            lines = tesseract_lines(preprocess(image))
            from extractor import extract_fields
            result = extract_fields(lines)
            proc_ms = int((time.time() - t0) * 1000)

        overall = sum(l["confidence"] for l in lines) / len(lines) if lines else 0.0
        html_doc = build_result_html(result, proc_ms, overall)

        # Count detected fields to size the iframe height
        n_fields = len(result["data"])
        height = 120 + n_fields * 80 + 60  # header + fields + footer

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.html(html_doc)
