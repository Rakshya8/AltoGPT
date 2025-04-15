FROM python:3.10-slim

WORKDIR /app
# COPY . .
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 && \
    pip install huggingface-hub transformers accelerate 
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]