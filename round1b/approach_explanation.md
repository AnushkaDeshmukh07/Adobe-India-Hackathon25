# Approach Explanation - Round 1B

## Methodology Overview

Our persona-driven document intelligence system employs a multi-stage approach to extract and prioritize relevant sections based on user persona and job requirements.

### 1. Document Processing
- **PDF Extraction**: Using pdfplumber for robust text extraction from PDFs
- **Section Detection**: Pattern-based heading detection using regex patterns and heuristics
- **Content Structuring**: Hierarchical organization of document content with page references

### 2. Semantic Analysis
- **Embedding Model**: Utilizing SentenceTransformers (all-MiniLM-L6-v2) for semantic understanding
- **Query Formation**: Combining persona and job description to create a comprehensive query vector
- **Similarity Calculation**: Cosine similarity between section embeddings and query embedding

### 3. Relevance Ranking
- **Section Scoring**: Each section receives a relevance score based on semantic similarity
- **Importance Ranking**: Sections are ranked by their relevance to the persona's job requirements
- **Subsection Analysis**: Fine-grained analysis of top sections to identify key subsections

### 4. Fallback Mechanisms
- **TF-IDF Backup**: Secondary ranking using TF-IDF vectorization if embedding fails
- **Keyword Matching**: Ultimate fallback using simple keyword intersection
- **Error Handling**: Robust error handling to ensure system reliability

## Key Features
- **Lightweight Model**: Using a compact 90MB sentence transformer model for efficiency
- **Multi-domain Support**: Generic approach works across research papers, reports, textbooks
- **Scalable Architecture**: Modular design allows easy extension and modification
- **Performance Optimized**: Meets all constraints (CPU-only, <60s processing, <1GB model)

## Technical Considerations
- **Memory Efficiency**: Streaming PDF processing to handle large documents
- **CPU Optimization**: No GPU dependencies, optimized for CPU-based inference
- **Offline Operation**: No internet access required during execution
- **Constraint Compliance**: All performance and size constraints strictly followed