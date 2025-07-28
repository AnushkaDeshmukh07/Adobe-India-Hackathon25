#!/bin/bash

# PDF Processing System - Run Script
# This script builds and runs the PDF processor in Docker

set -e

echo "🚀 PDF Processing System"
echo "========================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if input directory exists
if [ ! -d "input_pdfs" ]; then
    echo "📁 Creating input_pdfs directory..."
    mkdir -p input_pdfs
fi

# Check if there are any PDF files
if [ -z "$(ls -A input_pdfs/*.pdf 2>/dev/null)" ]; then
    echo "⚠️  No PDF files found in input_pdfs/ directory"
    echo "   Please add your PDF files to the input_pdfs/ directory and run again."
    exit 1
fi

# Count PDF files
pdf_count=$(ls input_pdfs/*.pdf 2>/dev/null | wc -l)
echo "📄 Found $pdf_count PDF file(s)"

# Create output directory
mkdir -p output

# Build Docker image
echo "🔨 Building Docker image..."
docker build -t pdf-processor . --no-cache

# Run the container
echo "🏃 Running PDF processor..."
docker run --rm \
    -v "$(pwd)/input_pdfs:/app/input_pdfs" \
    -v "$(pwd)/output:/app/output" \
    --network none \
    pdf-processor

echo "✅ Processing complete! Check the output/ directory for results."