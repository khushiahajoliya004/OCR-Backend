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
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements-backend.txt .
RUN pip install --no-cache-dir -r requirements-backend.txt

# Download PaddleOCR models directly — avoids PaddlePaddle segfault during build
RUN mkdir -p /root/.paddleocr/whl/det/en/en_PP-OCRv3_det_infer \
             /root/.paddleocr/whl/rec/en/en_PP-OCRv3_rec_infer && \
    wget -q https://paddleocr.bj.bcebos.com/PP-OCRv3/english/en_PP-OCRv3_det_infer.tar -O /tmp/det.tar && \
    tar -xf /tmp/det.tar -C /root/.paddleocr/whl/det/en/ && \
    wget -q https://paddleocr.bj.bcebos.com/PP-OCRv3/english/en_PP-OCRv3_rec_infer.tar -O /tmp/rec.tar && \
    tar -xf /tmp/rec.tar -C /root/.paddleocr/whl/rec/en/ && \
    rm /tmp/det.tar /tmp/rec.tar

# Copy application files
COPY main.py extractor.py ./

# Hugging Face Spaces requires port 7860
EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
