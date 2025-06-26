# Use a slim Python base image
FROM python:3.10-slim

# Install system dependencies for OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python packages
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose Streamlit default port
EXPOSE 8501

# Streamlit entry point
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
