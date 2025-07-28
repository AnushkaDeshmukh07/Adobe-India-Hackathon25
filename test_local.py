import subprocess
import json
import os

def test_extractor():
    # Test with a sample PDF
    pdf_file = "test.pdf"  # Place your test PDF here
    
    if not os.path.exists(pdf_file):
        print("Please place a test PDF file named 'test.pdf' in the project directory")
        return
    
    # Run the extractor
    result = subprocess.run([
        "python", "src/pdf_processor.py", pdf_file
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Extraction successful!")
        print("Output:")
        print(result.stdout)
        
        # Check if output file exists
        if os.path.exists("output/structure.json"):
            with open("output/structure.json", 'r') as f:
                data = json.load(f)
                print(f"\n📊 Results Summary:")
                print(f"Title: {data.get('title', 'N/A')}")
                print(f"Number of headings: {len(data.get('outline', []))}")
                
                # Show first few headings
                print("\n📑 First 5 headings:")
                for i, heading in enumerate(data.get('outline', [])[:5]):
                    print(f"  {i+1}. [{heading['level']}] {heading['text']} (page {heading['page']})")
        
    else:
        print("❌ Extraction failed!")
        print("Error:", result.stderr)

if __name__ == "__main__":
    test_extractor()