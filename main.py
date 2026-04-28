import os
import io
import uuid
import time

from fastapi import FastAPI, File, UploadFile, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import easyocr
import numpy as np
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Visiting Card OCR API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Loaded once at startup — first run downloads ~100MB model
reader = easyocr.Reader(["en"], gpu=False, verbose=False)

VALID_API_KEYS = set(os.getenv("API_KEYS", "test123").split(","))
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


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

    image_np = np.array(image)

    try:
        results = reader.readtext(image_np)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")

    lines = [
        {
            "text": text,
            "bbox": [[int(p[0]), int(p[1])] for p in bbox],
            "confidence": round(float(confidence), 4),
        }
        for (bbox, text, confidence) in results
    ]

    avg_confidence = (
        round(sum(l["confidence"] for l in lines) / len(lines), 4) if lines else 0.0
    )

    return {
        "status": "success",
        "request_id": str(uuid.uuid4()),
        "processing_time_ms": int((time.time() - start) * 1000),
        "text": "\n".join(l["text"] for l in lines),
        "lines": lines,
        "confidence": avg_confidence,
    }
