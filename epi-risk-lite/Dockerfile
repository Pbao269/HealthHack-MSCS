FROM python:3.11-slim

# Install system dependencies for camelot (cv2, ghostscript)
RUN apt-get update && apt-get install -y \
    ghostscript \
    python3-tk \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy application code
COPY app ./app
COPY README.md ./

# Create necessary directories
RUN mkdir -p models/latest data

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

