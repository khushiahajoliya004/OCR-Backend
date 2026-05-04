import os
import io
import uuid
import time

from fastapi import FastAPI, File, UploadFile, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from paddleocr import PaddleOCR
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from dotenv import load_dotenv
from extractor import extract_fields, clean_text

load_dotenv()

app = FastAPI(title="Visiting Card OCR API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

reader = PaddleOCR(use_angle_cls=False, lang="en", use_gpu=False, show_log=False)

VALID_API_KEYS = set(os.getenv("API_KEYS", "test123").split(","))
MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MIN_DIMENSION = 800
LOW_QUALITY_THRESHOLD = 0.5


def preprocess_image(image: Image.Image) -> Image.Image:
    w, h = image.size
    if max(w, h) < MIN_DIMENSION:
        scale = MIN_DIMENSION / max(w, h)
        image = image.resize((int(w * scale), int(h * scale)), Image.BILINEAR)
    gray = image.convert("L")
    gray = ImageEnhance.Contrast(gray).enhance(1.5)
    return gray.convert("RGB")


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0", "ocr_engine": "paddleocr"}


@app.post("/api/v1/ocr")
async def ocr_scan(
    file: UploadFile = File(...),
    x_api_key: str = Header(...),
):
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use JPG, PNG, or WEBP.")

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Max 5 MB.")

    start = time.time()

    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Cannot read image file.")

    image = preprocess_image(image)
    image_np = np.array(image)

    try:
        results = reader.ocr(image_np)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")

    lines = []
    for item in (results[0] or []):
        bbox, (text, confidence) = item
        lines.append({
            "text": clean_text(text),
            "bbox": [[int(p[0]), int(p[1])] for p in bbox],
            "confidence": round(float(confidence), 4),
        })

    overall_confidence = (
        round(sum(l["confidence"] for l in lines) / len(lines), 4) if lines else 0.0
    )

    extracted = extract_fields(lines)

    warnings = []
    if overall_confidence < LOW_QUALITY_THRESHOLD:
        warnings.append(
            "Low image quality detected. Results may be inaccurate. "
            "Try a clearer, higher-resolution photo."
        )

    return {
        "status": "success",
        "request_id": str(uuid.uuid4()),
        "processing_time_ms": int((time.time() - start) * 1000),
        "ocr_engine": "paddleocr",
        "data": extracted["data"],
        "confidence": {
            "overall": overall_confidence,
            **extracted["confidence"],
        },
        "low_confidence_fields": extracted["low_confidence_fields"],
        "warnings": warnings,
        "raw": {
            "text": "\n".join(l["text"] for l in lines),
            "lines": lines,
        },
    }
