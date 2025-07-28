```markdown
# PDF Structure Extractor

A project developed for **Adobe India Hackathon 2025 (Round 1A)**. This solution extracts structured content (headings, paragraphs, sections) from unstructured PDF files using deep learning and NLP techniques.

## 🧠 Objective

To automate the process of understanding the layout and hierarchy of content within PDFs for further intelligent document processing.

---

## 🚀 Features

- Detects and classifies headings (H1, H2, H3, etc.)
- Preserves the logical structure of PDF content
- Outputs in a readable JSON format
- Supports batch processing of PDF files
- Easily extendable to downstream applications (e.g., summarization, classification)

---

## 🗂️ Project Structure

```

pdf-structure-extractor/
├── round 1a/                # Outputs for round 1a
├── src/                     # Core logic and inference scripts
├── models/                  # Pretrained models (excluded from GitHub due to size)
├── pdfs/                    # Input PDFs
├── test\_local.py            # Sample test runner
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container setup (optional)
└── README.md                # Project documentation

````

---

## ⚙️ Installation

1. Clone the repo:

   ```bash
   git clone https://github.com/AnushkaDeshmukh07/Adobe-India-Hackathon25.git
   cd Adobe-India-Hackathon25
````

2. Create a virtual environment:

   ```bash
   python3 -m venv venv310
   source venv310/bin/activate  # On Windows: venv310\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## 🧪 How to Run

```bash
python test_local.py
```

* Outputs are saved in `round 1a/`
* Edit `test_local.py` to change input PDFs or model behavior

---

## 📁 Sample Output Format (JSON)

```json
{
  "document": "test1.pdf",
  "structure": [
    {
      "type": "heading",
      "level": "H1",
      "text": "1. Introduction"
    },
    {
      "type": "paragraph",
      "text": "This document contains..."
    },
    ...
  ]
}
```

---

## ⚠️ Notes

* Large files like `.venv/` and `.safetensors` are excluded from this repository. Please download them separately or refer to the model setup documentation.

---

## 📦 Optional: Run in Docker

```bash
docker build -t pdf-extractor .
docker run -v $(pwd):/app pdf-extractor
```

---

## 🙋‍♀️ Author

**Anushka Deshmukh**
Student, Computer Engineering
[GitHub Profile](https://github.com/AnushkaDeshmukh07)

---



