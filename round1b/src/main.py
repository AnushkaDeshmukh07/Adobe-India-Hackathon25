#!/usr/bin/env python3
import os
import json
import time
import warnings
from datetime import datetime
from pdf_processor import PDFProcessor
from text_analyzer import TextAnalyzer
from output_formatter import OutputFormatter
from context_inferer import DynamicContextInferer

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

def main():
    print("🚀 Starting PDF Processing System...")
    print("=" * 50)
    
    base_dir = os.path.dirname(__file__)
    input_dir = os.path.abspath(os.path.join(base_dir, "../input_pdfs"))
    output_dir = os.path.abspath(os.path.join(base_dir, "../output"))

    # Initialize components
    pdf_processor = PDFProcessor()
    text_analyzer = TextAnalyzer()
    output_formatter = OutputFormatter()
    context_inferer = DynamicContextInferer()

    # Look for input files
    if not os.path.exists(input_dir):
        print(f"❌ Input directory not found: {input_dir}")
        return 0.0
        
    input_files = [os.path.join(input_dir, file)
                   for file in os.listdir(input_dir) if file.endswith('.pdf')]

    if not input_files:
        print("❌ No PDF files found in input directory")
        return 0.0

    print(f"📄 Found {len(input_files)} PDF files:")
    for file in input_files:
        print(f"  - {os.path.basename(file)}")
    print()

    start_time = time.time()

    # Read and join all texts from PDFs for context inference
    print("🔍 Analyzing document content for context...")
    all_texts = []
    for file in input_files:
        text = pdf_processor.extract_raw_text(file)
        if text:
            all_texts.append(text)
    
    combined_text = "\n".join(all_texts)
    print(f"📊 Total text length: {len(combined_text)} characters")

    # Automatically infer persona and job using the improved inferer
    persona, job_description = context_inferer.infer_persona_and_job(combined_text)

    print(f"\n🎭 Detected Persona: {persona}")
    print(f"💼 Job Description: {job_description}")
    print()

    # Process all PDFs
    print("⚙️  Processing PDF files...")
    all_documents = []
    for pdf_path in input_files:
        print(f"  Processing: {os.path.basename(pdf_path)}")
        doc_data = pdf_processor.process_pdf(pdf_path)
        if doc_data:
            all_documents.append(doc_data)

    # Analyze and rank sections
    if all_documents:
        print(f"\n🧠 Analyzing content with AI...")
        analyzed_results = text_analyzer.analyze_documents(
            all_documents, persona, job_description
        )

        # Format output
        output_data = output_formatter.format_output(
            analyzed_results, input_files, persona, job_description
        )

        # Save output
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "challenge1b_output.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        processing_time = time.time() - start_time
        
        print(f"\n✅ Processing completed successfully!")
        print(f"⏱️  Processing time: {processing_time:.2f} seconds")
        print(f"📁 Output saved to: {output_path}")
        print(f"📋 Extracted {len(output_data['extracted_sections'])} sections")
        print(f"🔍 Generated {len(output_data['subsection_analysis'])} subsections")
        
        return processing_time
    else:
        print("❌ No documents were successfully processed")
        return 0.0

if __name__ == "__main__":
    overall_start = time.time()
    duration = main()
    overall_end = time.time()
    print(f"\n🏁 Total execution time: {overall_end - overall_start:.2f} seconds")
    print("=" * 50)