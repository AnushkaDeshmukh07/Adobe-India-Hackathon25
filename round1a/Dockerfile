# Use Python 3.9 slim as base image with explicit platform
FROM python:3.9-slim


# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main script
COPY enhanced_pdf_extractor.py .

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# Run the extraction script
CMD ["python", "enhanced_pdf_extractor.py"]