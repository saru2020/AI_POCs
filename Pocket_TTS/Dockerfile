FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
# Install pocket-tts without deps first to avoid conflicts
# Then install other dependencies (requirements.txt doesn't include pocket-tts)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir pocket-tts --no-deps && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir "huggingface-hub[cli]"

# Copy application files
COPY src/ /app/src/
COPY docs/ /app/docs/

# Create directories for input/output/models
RUN mkdir -p /app/input /app/output /app/models

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV HUGGINGFACE_HUB_CACHE=/app/.cache/huggingface

# Make script executable
RUN chmod +x /app/src/pocket_tts_demo.py

# Default command
ENTRYPOINT ["python", "src/pocket_tts_demo.py"]
CMD ["--help"]
