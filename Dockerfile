FROM python:3.11-slim

WORKDIR /app

ENV OMP_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1
ENV MKL_NUM_THREADS=1

# System libraries required by OpenCV (used internally by PaddleOCR)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements-backend.txt .
RUN pip install --no-cache-dir -r requirements-backend.txt

# Bake PaddleOCR models into the image — no runtime downloads
RUN python -c "from paddleocr import PaddleOCR; PaddleOCR(use_angle_cls=False, lang='en', use_gpu=False, show_log=False); print('Models ready')"

# Copy application files
COPY main.py extractor.py ./

# Hugging Face Spaces requires port 7860
EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
