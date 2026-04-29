FROM python:3.11-slim

WORKDIR /app

# System libraries required by OpenCV (used internally by EasyOCR)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements-backend.txt .
RUN pip install --no-cache-dir -r requirements-backend.txt

# Pre-download EasyOCR English model into the image so cold starts are fast
RUN python -c "import bidi, bidi.algorithm; \
    import sys; \
    bidi.get_display = bidi.algorithm.get_display; \
    import easyocr; \
    easyocr.Reader(['en'], gpu=False, verbose=False)"

# Copy application files
COPY main.py extractor.py ./

# Hugging Face Spaces requires port 7860
EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
