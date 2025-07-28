FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./

# Install core dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install CPU version of torch manually
RUN pip install --no-cache-dir torch==2.0.1+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html

# Download NLTK data
RUN python -m nltk.downloader punkt stopwords

# Copy entire app
COPY . .

CMD ["python", "src/main.py"]
