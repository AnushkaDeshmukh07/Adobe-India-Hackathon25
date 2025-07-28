import os
import re
from typing import List, Dict, Any

try:
    import pdfplumber
    PDF_LIBRARY = 'pdfplumber'
except ImportError:
    try:
        import PyPDF2
        PDF_LIBRARY = 'PyPDF2'
    except ImportError:
        raise ImportError("Neither pdfplumber nor PyPDF2 is available")

class PDFProcessor:
    def __init__(self):
        self.heading_patterns = [
            r'^[A-Z][A-Z\s]{2,}$',  # ALL CAPS headings
            r'^\d+\.?\s+[A-Z]',     # Numbered headings
            r'^[A-Z][a-z]+.*:$',    # Title case with colon
            r'^\s*[IVX]+\.\s+',     # Roman numerals
            r'^\s*[A-Z]\.\s+',      # Letter headings
        ]

    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Process PDF and extract structured content"""
        try:
            doc_data = {
                'filename': os.path.basename(pdf_path),
                'sections': [],
                'full_text': ''
            }

            if PDF_LIBRARY == 'pdfplumber':
                return self._process_with_pdfplumber(pdf_path, doc_data)
            else:
                return self._process_with_pypdf2(pdf_path, doc_data)

        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            return None

    def extract_raw_text(self, pdf_path: str) -> str:
        """Extract entire text from PDF file (used for persona/job inference)"""
        try:
            full_text = ''
            if PDF_LIBRARY == 'pdfplumber':
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            full_text += text + '\n'
            else:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            full_text += text + '\n'
            return full_text.strip()
        except Exception as e:
            print(f"Error reading raw text from {pdf_path}: {e}")
            return ""

    def _process_with_pdfplumber(self, pdf_path: str, doc_data: Dict) -> Dict[str, Any]:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    doc_data['full_text'] += text + '\n'
                    sections = self._extract_sections(text, page_num)
                    doc_data['sections'].extend(sections)
        return doc_data

    def _process_with_pypdf2(self, pdf_path: str, doc_data: Dict) -> Dict[str, Any]:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                if text:
                    doc_data['full_text'] += text + '\n'
                    sections = self._extract_sections(text, page_num)
                    doc_data['sections'].extend(sections)
        return doc_data

    def _extract_sections(self, text: str, page_num: int) -> List[Dict[str, Any]]:
        sections = []
        lines = text.split('\n')
        current_section = None
        current_content = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if self._is_heading(line):
                if current_section and current_content:
                    current_section['content'] = ' '.join(current_content)
                    if len(current_section['content'].strip()) > 50:
                        sections.append(current_section)

                current_section = {
                    'title': line,
                    'page': page_num,
                    'content': '',
                    'level': self._determine_heading_level(line)
                }
                current_content = []
            else:
                if current_section:
                    current_content.append(line)
                else:
                    current_section = {
                        'title': f"Content from page {page_num}",
                        'page': page_num,
                        'content': '',
                        'level': 'H1'
                    }
                    current_content = [line]

        if current_section and current_content:
            current_section['content'] = ' '.join(current_content)
            if len(current_section['content'].strip()) > 50:
                sections.append(current_section)

        return sections

    def _is_heading(self, line: str) -> bool:
        if len(line) < 3 or len(line) > 100:
            return False

        for pattern in self.heading_patterns:
            if re.match(pattern, line):
                return True

        if line.isupper() and len(line.split()) <= 8:
            return True

        if line.endswith(':') and len(line.split()) <= 6:
            return True

        common_titles = [
            'introduction', 'conclusion', 'overview', 'history', 'attractions',
            'restaurants', 'hotels', 'activities', 'things to do', 'cultural'
        ]

        if any(title in line.lower() for title in common_titles):
            return True

        return False

    def _determine_heading_level(self, heading: str) -> str:
        if re.match(r'^\d+\.?\s+', heading):
            return 'H1'
        elif re.match(r'^\d+\.\d+\.?\s+', heading):
            return 'H2'
        elif re.match(r'^\d+\.\d+\.\d+\.?\s+', heading):
            return 'H3'
        elif heading.isupper():
            return 'H1'
        else:
            return 'H2'
