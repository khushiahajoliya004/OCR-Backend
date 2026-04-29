import os
import sys
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(page_title="Card Scanner — OCR", page_icon="📇", layout="centered")

# ── Inject CSS matching index.html ────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

.hero {
  background: linear-gradient(135deg,#1e3a8a 0%,#3b5bdb 60%,#6366f1 100%);
  padding: 36px 24px 64px; text-align: center;
}
.hero-badge {
  display: inline-block;
  background: rgba(255,255,255,.15); border: 1px solid rgba(255,255,255,.25);
  color: #e0e7ff; font-size: 11px; font-weight: 600; letter-spacing: .06em;
  text-transform: uppercase; padding: 5px 14px; border-radius: 20px; margin-bottom: 16px;
}
.hero h1 { font-size: 32px; font-weight: 800; color: #fff; margin-bottom: 10px; }
.hero p  { font-size: 14px; color: rgba(255,255,255,.7); max-width: 360px; margin: 0 auto; line-height: 1.6; }

.page-body { max-width: 540px; margin: -36px auto 48px; padding: 0 16px; }
.card {
  background: #fff; border-radius: 20px; padding: 28px;
  box-shadow: 0 4px 24px rgba(0,0,0,.09), 0 1px 4px rgba(0,0,0,.05);
  margin-bottom: 20px;
}

/* Streamlit file uploader → drop-zone look */
[data-testid="stFileUploader"] {
  border: 2px dashed #cbd5e1; border-radius: 14px;
  background: #fafbff; padding: 8px;
}
[data-testid="stFileUploader"]:hover { border-color: #3b5bdb; background: #eef2ff; }
[data-testid="stFileUploaderDropzone"] { background: transparent !important; }

/* Primary button */
div.stButton > button[kind="primary"] {
  width: 100%; padding: 15px; margin-top: 4px;
  background: linear-gradient(135deg,#1e3a8a,#3b5bdb) !important;
  color: #fff !important; border: none !important; border-radius: 13px !important;
  font-size: 15px !important; font-weight: 700 !important; letter-spacing: .02em;
  box-shadow: 0 4px 16px rgba(59,91,219,.35) !important;
  transition: all .25s !important;
}
div.stButton > button[kind="primary"]:hover { box-shadow: 0 8px 24px rgba(59,91,219,.45) !important; }

/* Result card components */
.result-header {
  background: linear-gradient(135deg,#1e3a8a,#3b5bdb);
  padding: 20px 24px; border-radius: 16px 16px 0 0;
  display: flex; align-items: center; justify-content: space-between;
}
.result-header-left { display: flex; align-items: center; gap: 10px; }
.result-header-icon {
  width: 36px; height: 36px; background: rgba(255,255,255,.15);
  border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px;
}
.result-title   { font-size: 15px; font-weight: 700; color: #fff; }
.result-sub     { font-size: 11px; color: rgba(255,255,255,.6); }
.badge-ok {
  background: rgba(255,255,255,.18); border: 1px solid rgba(255,255,255,.3);
  color: #fff; font-size: 11px; font-weight: 600; padding: 4px 12px; border-radius: 20px;
}
.result-body { background: #fff; border-radius: 0 0 16px 16px; overflow: hidden; }
.field-row {
  display: flex; align-items: flex-start; gap: 14px;
  padding: 14px 24px; border-bottom: 1px solid #f1f5f9;
}
.field-row:last-child { border-bottom: none; }
.field-icon {
  width: 38px; height: 38px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center; font-size: 17px; flex-shrink: 0;
}
.icon-name        { background:#eff6ff; }
.icon-designation { background:#f0fdf4; }
.icon-company     { background:#fef3c7; }
.icon-phone       { background:#ecfdf5; }
.icon-email       { background:#fdf4ff; }
.icon-website     { background:#f0f9ff; }
.icon-address     { background:#fff7ed; }
.field-body { flex: 1; min-width: 0; }
.field-label {
  font-size: 10px; color: #94a3b8; text-transform: uppercase;
  letter-spacing: .08em; font-weight: 700; margin-bottom: 3px;
}
.field-value { font-size: 14px; color: #1e293b; font-weight: 500; word-break: break-word; line-height: 1.5; }
.field-value a { color: #3b5bdb; text-decoration: none; font-weight: 600; }
.conf-row { display: flex; align-items: center; gap: 7px; margin-top: 6px; }
.conf-bar { height: 4px; border-radius: 4px; background: #f1f5f9; width: 72px; overflow: hidden; }
.conf-fill { height: 100%; border-radius: 4px; }
.conf-lbl  { font-size: 10px; color: #cbd5e1; font-weight: 600; }
.meta-row {
  display: flex; justify-content: space-between; font-size: 11px; color: #cbd5e1;
  padding: 14px 24px; border-top: 1px solid #f1f5f9; font-weight: 500;
}
.warn-box {
  background: #fffbeb; border: 1px solid #fde68a; border-radius: 12px;
  padding: 12px 16px; font-size: 12px; color: #92400e; margin-bottom: 14px; font-weight: 500;
}
.no-data { text-align: center; padding: 40px 24px; color: #94a3b8; font-size: 14px; font-weight: 500; }
.no-data-icon { font-size: 40px; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-badge">✦ AI-Powered OCR</div>
  <h1>📇 Card Scanner</h1>
  <p>Instantly extract contact details from any visiting card using smart OCR.</p>
</div>
<div class="page-body">
<div class="card">
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

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
                "words": [], "confs": [],
                "left": data["left"][i], "top": data["top"][i],
                "right": data["left"][i] + data["width"][i],
                "bottom": data["top"][i] + data["height"][i],
            }
        g = groups[key]
        g["words"].append(word)
        g["confs"].append(conf)
        g["right"]  = max(g["right"],  data["left"][i] + data["width"][i])
        g["bottom"] = max(g["bottom"], data["top"][i]  + data["height"][i])
        g["left"]   = min(g["left"],   data["left"][i])
        g["top"]    = min(g["top"],    data["top"][i])
    lines = []
    for key in sorted(groups):
        g = groups[key]
        if not g["words"]:
            continue
        l, t, r, b = g["left"], g["top"], g["right"], g["bottom"]
        conf = round(sum(g["confs"]) / len(g["confs"]) / 100.0, 4)
        lines.append({
            "text": " ".join(g["words"]),
            "bbox": [[l, t], [r, t], [r, b], [l, b]],
            "confidence": conf,
        })
    return lines


def conf_color(v: float) -> str:
    if v >= 0.8: return "#3b5bdb"
    if v >= 0.6: return "#f59e0b"
    return "#ef4444"


def render_results(extracted: dict, proc_ms: int) -> str:
    data  = extracted["data"]
    confs = extracted["confidence"]

    FIELDS = [
        ("name",        "👤", "Name",        "icon-name",        False),
        ("designation", "💼", "Designation", "icon-designation", False),
        ("company",     "🏢", "Company",     "icon-company",     False),
        ("phone",       "📞", "Phone",       "icon-phone",       True),
        ("email",       "✉️", "Email",       "icon-email",       True),
        ("website",     "🌐", "Website",     "icon-website",     True),
        ("address",     "📍", "Address",     "icon-address",     False),
    ]

    if not data:
        return """
        <div class="result-body">
          <div class="no-data">
            <div class="no-data-icon">😕</div>
            No contact information detected.<br>Try a clearer or higher-resolution image.
          </div>
        </div>"""

    rows = ""
    for key, icon, label, cls, is_list in FIELDS:
        val = data.get(key)
        if val is None:
            continue
        items = val if isinstance(val, list) else [val]
        if key == "phone":
            display = "<br>".join(f'<a href="tel:{v}">{v}</a>' for v in items)
        elif key == "email":
            display = "<br>".join(f'<a href="mailto:{v}">{v}</a>' for v in items)
        elif key == "website":
            def _href(v):
                h = v if v.startswith("http") else "https://" + v
                return f'<a href="{h}" target="_blank">{v}</a>'
            display = "<br>".join(_href(v) for v in items)
        else:
            display = "<br>".join(items)

        fc = confs.get(key)
        conf_html = ""
        if fc is not None:
            pct = round(fc * 100)
            col = conf_color(fc)
            conf_html = f"""
            <div class="conf-row">
              <div class="conf-bar"><div class="conf-fill" style="width:{pct}%;background:{col}"></div></div>
              <span class="conf-lbl">{pct}% confidence</span>
            </div>"""

        rows += f"""
        <div class="field-row">
          <div class="field-icon {cls}">{icon}</div>
          <div class="field-body">
            <div class="field-label">{label}</div>
            <div class="field-value">{display}</div>
            {conf_html}
          </div>
        </div>"""

    overall = extracted.get("confidence", {}).get("overall", "")
    overall_html = f"⬤ Overall confidence: {round(overall*100)}%" if overall else ""

    return f"""
    <div class="result-header">
      <div class="result-header-left">
        <div class="result-header-icon">📋</div>
        <div>
          <div class="result-title">Extracted Info</div>
          <div class="result-sub">Contact details from card</div>
        </div>
      </div>
      <span class="badge-ok">✓ Success</span>
    </div>
    <div class="result-body">{rows}</div>
    <div class="meta-row">
      <span>{overall_html}</span>
      <span>⚡ {proc_ms} ms</span>
    </div>"""


# ── Upload section ────────────────────────────────────────────────────────────

uploaded = st.file_uploader(
    "📤  Drop card image here or click to browse",
    type=["jpg", "jpeg", "png", "webp"],
    label_visibility="visible",
)

if uploaded:
    image = Image.open(uploaded).convert("RGB")
    st.image(image, use_container_width=True)

    if st.button("🔍  Scan Card", type="primary", use_container_width=True):
        import time
        with st.spinner("Running OCR…"):
            t0 = time.time()
            processed = preprocess_image(image)
            lines = run_tesseract(processed)
            from extractor import extract_fields
            result = extract_fields(lines)
            proc_ms = int((time.time() - t0) * 1000)

        result["confidence"]["overall"] = (
            sum(l["confidence"] for l in lines) / len(lines) if lines else 0.0
        )

        html = render_results(result, proc_ms)
        st.markdown(f'<div style="margin-top:20px">{html}</div>', unsafe_allow_html=True)

st.markdown("</div></div>", unsafe_allow_html=True)
