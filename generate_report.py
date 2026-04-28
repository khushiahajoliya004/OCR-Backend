"""
Run: python generate_report.py card1.jpg card2.png card3.jpg
Opens a formatted HTML report in your browser — print it to PDF from there.
"""

import sys
import json
import base64
import datetime
import webbrowser
import urllib.request
import urllib.error
from pathlib import Path

API_URL  = "http://127.0.0.1:8000/api/v1/ocr"
API_KEY  = "test123"
OUT_FILE = "ocr_report.html"


def call_api(image_path: Path) -> dict:
    boundary = "----FormBoundary7MA4YWxkTrZu0gW"
    with open(image_path, "rb") as f:
        file_data = f.read()

    suffix = image_path.suffix.lower()
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
            "png": "image/png", "webp": "image/webp"}.get(suffix.lstrip("."), "image/jpeg")

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{image_path.name}"\r\n'
        f"Content-Type: {mime}\r\n\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "x-api-key": API_KEY,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()}
    except Exception as e:
        return {"error": str(e)}


def image_to_base64(path: Path) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def confidence_color(val: float) -> str:
    if val >= 0.8:
        return "#2ecc71"
    if val >= 0.6:
        return "#f39c12"
    return "#e74c3c"


def render_card(idx: int, image_path: Path, result: dict) -> str:
    if "error" in result:
        return f"""
        <div class="card error">
          <h2>Test {idx} — {image_path.name}</h2>
          <p class="err">Error: {result['error']}</p>
        </div>"""

    data   = result.get("data", {})
    conf   = result.get("confidence", {})
    warns  = result.get("warnings", [])
    low    = result.get("low_confidence_fields", [])
    raw    = result.get("raw", {})
    overall = conf.get("overall", 0)
    img64  = image_to_base64(image_path)
    ext    = image_path.suffix.lstrip(".")
    mime   = "jpeg" if ext in ("jpg", "jpeg") else ext

    fields_html = ""
    field_order = ["name", "designation", "company", "phone", "email", "website", "address"]
    for field in field_order:
        val = data.get(field)
        fc  = conf.get(field)
        if val is None:
            display = '<span class="null">null</span>'
            badge   = ""
        else:
            display = ", ".join(val) if isinstance(val, list) else str(val)
            badge   = (f'<span class="badge" style="background:{confidence_color(fc)}">'
                       f'{fc:.0%}</span>') if fc else ""
        fields_html += f"""
        <tr>
          <td class="field-name">{field}</td>
          <td>{display}</td>
          <td>{badge}</td>
        </tr>"""

    low_html = ""
    if low:
        items = " ".join(
            f'<span class="low-badge">{l["field"]} ({l["confidence"]:.4f})</span>' for l in low
        )
        low_html = f'<div class="low-conf"><strong>Low confidence fields:</strong> {items}</div>'

    warn_html = ""
    if warns:
        warn_html = f'<div class="warning">⚠ {warns[0]}</div>'

    raw_text = raw.get("text", "").replace("<", "&lt;").replace(">", "&gt;")

    return f"""
    <div class="card">
      <h2>Test {idx} — <span class="fname">{image_path.name}</span></h2>
      <div class="card-body">
        <div class="left">
          <img src="data:image/{mime};base64,{img64}" alt="{image_path.name}">
          <div class="meta">
            <b>Request ID:</b> {result.get('request_id','—')}<br>
            <b>Processing time:</b> {result.get('processing_time_ms','—')} ms<br>
            <b>OCR engine:</b> {result.get('ocr_engine','easyocr')}<br>
            <b>Overall confidence:</b>
            <span class="badge" style="background:{confidence_color(overall)}">{overall:.0%}</span>
          </div>
          {warn_html}
          {low_html}
        </div>
        <div class="right">
          <h3>Extracted Fields</h3>
          <table>
            <thead><tr><th>Field</th><th>Value</th><th>Confidence</th></tr></thead>
            <tbody>{fields_html}</tbody>
          </table>
          <h3>Raw OCR Text</h3>
          <pre class="raw">{raw_text}</pre>
          <h3>Full JSON Response</h3>
          <pre class="json">{json.dumps(result, indent=2)}</pre>
        </div>
      </div>
    </div>"""


def build_html(cards_html: str, count: int) -> str:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>OCR API Test Report</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: Arial, sans-serif; background: #f4f6f9; color: #333; padding: 30px; }}
  h1 {{ font-size: 26px; margin-bottom: 4px; }}
  .subtitle {{ color: #666; font-size: 14px; margin-bottom: 30px; }}
  .card {{ background: #fff; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,.1);
           margin-bottom: 40px; padding: 24px; page-break-inside: avoid; }}
  .card h2 {{ font-size: 18px; border-bottom: 2px solid #3498db; padding-bottom: 8px; margin-bottom: 16px; }}
  .fname {{ color: #3498db; }}
  .card-body {{ display: flex; gap: 24px; }}
  .left {{ width: 280px; flex-shrink: 0; }}
  .left img {{ width: 100%; border-radius: 6px; border: 1px solid #ddd; margin-bottom: 12px; }}
  .meta {{ font-size: 13px; line-height: 1.8; background: #f8f9fa; padding: 10px;
           border-radius: 6px; margin-bottom: 10px; }}
  .right {{ flex: 1; overflow: hidden; }}
  .right h3 {{ font-size: 14px; color: #555; margin: 16px 0 8px; text-transform: uppercase;
              letter-spacing: .5px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
  th {{ background: #3498db; color: #fff; padding: 8px 12px; text-align: left; }}
  td {{ padding: 8px 12px; border-bottom: 1px solid #eee; vertical-align: top; }}
  .field-name {{ font-weight: bold; width: 110px; color: #555; }}
  .null {{ color: #aaa; font-style: italic; }}
  .badge {{ display: inline-block; color: #fff; padding: 2px 8px; border-radius: 12px;
            font-size: 12px; font-weight: bold; }}
  .low-badge {{ display: inline-block; background: #e74c3c; color: #fff; padding: 2px 8px;
               border-radius: 12px; font-size: 12px; margin: 2px; }}
  .low-conf {{ background: #fdecea; border-left: 3px solid #e74c3c; padding: 8px 12px;
              border-radius: 4px; font-size: 13px; margin-top: 8px; }}
  .warning {{ background: #fff8e1; border-left: 3px solid #f39c12; padding: 8px 12px;
             border-radius: 4px; font-size: 13px; margin-top: 8px; }}
  pre.raw {{ background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 6px;
            padding: 12px; font-size: 12px; white-space: pre-wrap; word-break: break-word;
            max-height: 150px; overflow-y: auto; }}
  pre.json {{ background: #1e1e1e; color: #d4d4d4; border-radius: 6px; padding: 12px;
             font-size: 11px; white-space: pre-wrap; word-break: break-word;
             max-height: 300px; overflow-y: auto; }}
  .error {{ border-left: 4px solid #e74c3c; }}
  .err {{ color: #e74c3c; font-weight: bold; }}
  .summary {{ background: #fff; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,.1);
             padding: 16px 24px; margin-bottom: 30px; display: flex; gap: 40px; }}
  .stat {{ text-align: center; }}
  .stat .val {{ font-size: 32px; font-weight: bold; color: #3498db; }}
  .stat .lbl {{ font-size: 13px; color: #888; }}
  @media print {{
    body {{ background: #fff; padding: 10px; }}
    pre.json {{ max-height: none; }}
    pre.raw {{ max-height: none; }}
  }}
</style>
</head>
<body>
<h1>Visiting Card OCR API — Test Report</h1>
<p class="subtitle">Generated: {now} &nbsp;|&nbsp; API: http://127.0.0.1:8000/api/v1/ocr &nbsp;|&nbsp; Cards tested: {count}</p>
<div class="summary">
  <div class="stat"><div class="val">{count}</div><div class="lbl">Cards Tested</div></div>
  <div class="stat"><div class="val">EasyOCR</div><div class="lbl">OCR Engine</div></div>
  <div class="stat"><div class="val">v1.0.0</div><div class="lbl">API Version</div></div>
</div>
{cards_html}
</body>
</html>"""


def main():
    paths = [Path(p) for p in sys.argv[1:]]
    if not paths:
        print("Usage: python generate_report.py card1.jpg card2.png ...")
        print("Example: python generate_report.py test_card.png")
        sys.exit(1)

    valid = [p for p in paths if p.exists()]
    missing = [p for p in paths if not p.exists()]
    if missing:
        print(f"Warning: files not found: {[str(p) for p in missing]}")
    if not valid:
        print("No valid image files found.")
        sys.exit(1)

    print(f"Testing {len(valid)} card(s)...")
    cards_html = ""
    for i, path in enumerate(valid, 1):
        print(f"  [{i}/{len(valid)}] {path.name} ...", end=" ", flush=True)
        result = call_api(path)
        cards_html += render_card(i, path, result)
        status = "error" if "error" in result else f"confidence={result.get('confidence',{}).get('overall','?')}"
        print(status)

    html = build_html(cards_html, len(valid))
    out = Path(OUT_FILE)
    out.write_text(html, encoding="utf-8")
    print(f"\nReport saved: {out.resolve()}")
    webbrowser.open(out.resolve().as_uri())
    print("Opened in browser — use Ctrl+P → Save as PDF to export.")


if __name__ == "__main__":
    main()
