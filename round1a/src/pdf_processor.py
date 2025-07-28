import fitz  # PyMuPDF
import json
import re
from typing import Dict, List, Any, Tuple
import os
from collections import Counter

class PDFStructureExtractor:
    def __init__(self):
        self.heading_patterns = [
            r'^(CHAPTER|Chapter)\s+\d+',
            r'^\d+\.\s+[A-Z][^.]*$',
            r'^\d+\.\d+\s+[A-Z]',
            r'^\d+\.\d+\.\d+\s+[A-Z]',
            r'^[A-Z\s]{5,50}$',
            r'^\d+[\.\)]\s+[A-Z][a-z]+',
        ]
        
        self.header_footer_patterns = [
            r'.International.*Software Testing.*Foundation.',
            r'.Qualifications Board.',
            r'.Version\s+\d+.*Page\s+\d+\s+of\s+\d+.',
            r'.©.*International Software Testing.',
            r'^Page\s+\d+\s+of\s+\d+$',
            r'^\d+$',
            r'^Version.\d{4}.*Page.'
        ]
        
        # Title detection keywords and patterns
        self.title_keywords = [
            'syllabus', 'foundation', 'level', 'extensions', 'overview',
            'certification', 'qualification', 'standard', 'guidelines'
        ]
        
        self.title_patterns = [
            r'.foundation.*level.',
            r'.syllabus.',
            r'.overview.',
            r'.certification.',
            r'.qualification.'
        ]
        
        self.title = ""
        self.title_font_size = 0
        self.title_spans = []
        self.font_size_stats = {}
    
    def extract_structure(self, pdf_path: str) -> Dict[str, Any]:
        try:
            doc = fitz.open(pdf_path)
            self._analyze_font_statistics(doc)
            self.title, self.title_font_size, self.title_spans = self._extract_title_advanced(doc)
            outline = self._extract_headings(doc)
            doc.close()
            return {"title": self.title, "outline": outline}
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return {"title": "", "outline": []}
    
    def _analyze_font_statistics(self, doc):
        """Analyze font size distribution across the document"""
        font_sizes = []
        for page_num in range(min(3, len(doc))):  # Analyze first 3 pages
            page = doc[page_num]
            blocks = page.get_text("dict")
            
            for block in blocks.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            if text and len(text) > 3:
                                font_sizes.append(span.get("size", 12))
        
        self.font_size_stats = Counter(font_sizes)
    
    def _is_header_footer(self, text: str, y_position: float, page_height: float) -> bool:
        if y_position < page_height * 0.1 or y_position > page_height * 0.9:
            for pattern in self.header_footer_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return True
        for pattern in self.header_footer_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _calculate_title_score(self, text: str, font_size: float, position: Tuple[float, float], 
                              page_num: int, total_pages: int) -> float:
        """Calculate a comprehensive score for title detection"""
        score = 0.0
        text_lower = text.lower()
        
        # 1. Font size score (30% weight)
        if self.font_size_stats:
            max_font_size = max(self.font_size_stats.keys())
            font_score = (font_size / max_font_size) * 30
            score += font_score
        
        # 2. Position score (25% weight) - titles usually in upper portion
        y_pos = position[1]
        if page_num == 0:  # First page bonus
            if y_pos < 300:  # Upper portion of page
                score += 25
            elif y_pos < 500:
                score += 15
        
        # 3. Keyword matching (25% weight)
        keyword_matches = sum(1 for keyword in self.title_keywords if keyword in text_lower)
        score += min(keyword_matches * 8, 25)
        
        # 4. Pattern matching (10% weight)
        pattern_matches = sum(1 for pattern in self.title_patterns 
                            if re.search(pattern, text_lower))
        score += min(pattern_matches * 10, 10)
        
        # 5. Text characteristics (10% weight)
        if len(text.split()) >= 2:  # Multi-word titles
            score += 5
        if text.istitle() or text.isupper():  # Proper case or uppercase
            score += 5
        
        # Penalties
        if len(text) < 5:
            score -= 10
        if len(text) > 100:
            score -= 5
        if re.match(r'^\d+[\.\s]', text):  # Starts with number
            score -= 15
        
        return max(0, score)

    def _extract_title_advanced(self, doc) -> Tuple[str, float, List]:
        """Advanced title extraction using multiple mechanisms"""
        if len(doc) == 0:
            return "Unknown Document", 0, []
        
        candidates = []
        
        # Analyze first 2 pages for title candidates
        for page_num in range(min(2, len(doc))):
            page = doc[page_num]
            page_height = page.rect.height
            blocks = page.get_text("dict")
            
            for block in blocks.get("blocks", []):
                if "lines" in block:
                    # Group consecutive spans that might form a title
                    line_groups = []
                    current_group = []
                    
                    for line in block["lines"]:
                        line_text = ""
                        line_font_size = 0
                        line_bbox = None
                        
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            y_pos = span.get("bbox", [0, 0, 0, 0])[1]
                            
                            if self._is_header_footer(text, y_pos, page_height):
                                continue
                                
                            if text:
                                line_text += text + " "
                                line_font_size = max(line_font_size, span.get("size", 12))
                                if line_bbox is None:
                                    line_bbox = span.get("bbox", [0, 0, 0, 0])
                        
                        line_text = line_text.strip()
                        if line_text and line_font_size > 0:
                            if (current_group and 
                                abs(current_group[-1]['bbox'][1] - line_bbox[1]) < 30 and
                                abs(current_group[-1]['font_size'] - line_font_size) < 2):
                                # Same group - merge
                                current_group.append({
                                    'text': line_text,
                                    'font_size': line_font_size,
                                    'bbox': line_bbox,
                                    'page': page_num
                                })
                            else:
                                # New group
                                if current_group:
                                    line_groups.append(current_group)
                                current_group = [{
                                    'text': line_text,
                                    'font_size': line_font_size,
                                    'bbox': line_bbox,
                                    'page': page_num
                                }]
                    
                    if current_group:
                        line_groups.append(current_group)
                    
                    # Evaluate each group as potential title
                    for group in line_groups:
                        combined_text = " ".join([item['text'] for item in group]).strip()
                        avg_font_size = sum([item['font_size'] for item in group]) / len(group)
                        first_bbox = group[0]['bbox']
                        
                        if len(combined_text) >= 5:
                            score = self._calculate_title_score(
                                combined_text, avg_font_size, 
                                (first_bbox[0], first_bbox[1]), 
                                page_num, len(doc)
                            )
                            
                            candidates.append({
                                'text': combined_text,
                                'font_size': avg_font_size,
                                'score': score,
                                'spans': group,
                                'page': page_num
                            })
        
        # Select best candidate
        if candidates:
            best_candidate = max(candidates, key=lambda x: x['score'])
            
            # Special handling for "Foundation Level Extensions" type titles
            title_text = best_candidate['text']
            
            # Look for related title parts nearby
            related_parts = []
            for candidate in candidates:
                if (candidate != best_candidate and 
                    candidate['page'] == best_candidate['page'] and
                    abs(candidate['spans'][0]['bbox'][1] - best_candidate['spans'][0]['bbox'][1]) < 100):
                    
                    # Check if it's a related part (like "Overview" for "Foundation Level Extensions")
                    candidate_lower = candidate['text'].lower()
                    if any(keyword in candidate_lower for keyword in ['overview', 'summary', 'introduction']):
                        related_parts.append(candidate)
            
            # Merge related parts
            all_parts = [best_candidate] + related_parts
            all_parts.sort(key=lambda x: x['spans'][0]['bbox'][1])  # Sort by Y position
            
            final_title = " - ".join([part['text'] for part in all_parts])
            
            return (final_title, best_candidate['font_size'], best_candidate['spans'])
        
        return "Unknown Document", 12, []

    def _is_title_text(self, text: str, font_size: float) -> bool:
        """Check if given text matches our extracted title"""
        if not self.title or not text:
            return False
        
        # Direct match
        if text.strip() == self.title.strip():
            return True
        
        # Check if text is part of title
        title_parts = self.title.split(" - ")
        for part in title_parts:
            if text.strip() == part.strip():
                return True
        
        # Check individual words for partial matches
        text_words = set(text.lower().split())
        title_words = set(self.title.lower().split())
        
        if len(text_words) >= 2 and len(text_words.intersection(title_words)) >= len(text_words) * 0.8:
            return True
        
        return False

    def _extract_headings(self, doc) -> List[Dict[str, Any]]:
        headings = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_height = page.rect.height
            blocks = page.get_text("dict")
            
            current_heading = None
            for block in blocks.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        line_font_size = 0
                        line_y_pos = 0
                        
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            y_pos = span.get("bbox", [0, 0, 0, 0])[1]
                            
                            if self._is_header_footer(text, y_pos, page_height):
                                continue
                                
                            line_text += text + " "
                            line_font_size = max(line_font_size, span.get("size", 12))
                            line_y_pos = y_pos
                        
                        line_text = line_text.strip()
                        if not line_text:
                            continue
                        
                        # Skip if this is the title or part of title
                        if self._is_title_text(line_text, line_font_size):
                            continue
                        
                        if self._is_heading(line_text, line_font_size):
                            heading_level = self._determine_heading_level(line_text, line_font_size)
                            
                            if (current_heading and 
                                abs(current_heading["y_pos"] - line_y_pos) < 20 and
                                current_heading["level"] == heading_level):
                                current_heading["text"] += " " + line_text
                            else:
                                if current_heading:
                                    headings.append({
                                        "level": current_heading["level"],
                                        "text": current_heading["text"],
                                        "page": current_heading["page"]
                                    })
                                current_heading = {
                                    "text": line_text,
                                    "level": heading_level,
                                    "page": page_num,
                                    "y_pos": line_y_pos
                                }
            
            if current_heading:
                headings.append({
                    "level": current_heading["level"],
                    "text": current_heading["text"],
                    "page": current_heading["page"]
                })
                current_heading = None
        
        return self._clean_and_sort_headings(headings)
    
    def _is_heading(self, text: str, font_size: float) -> bool:
        if len(text) < 3 or len(text) > 200:
            return False
        if re.match(r'^[\d\s\.\-_]+$', text):
            return False
        if font_size < 11:
            return False
        
        # Don't treat title as heading
        if self._is_title_text(text, font_size):
            return False
        
        for pattern in self.heading_patterns:
            if re.match(pattern, text):
                return True
        
        if font_size >= 13:  # Lowered threshold
            if text.isupper() and len(text.split()) <= 10:
                return True
            if text[0].isupper() and not text.endswith('.'):
                return True
        
        return False

    def _determine_heading_level(self, text: str, font_size: float) -> str:
        # Skip title-level classification
        if self._is_title_text(text, font_size):
            return "SKIP"
        
        # More sophisticated heading level detection
        if re.match(r'^(CHAPTER|Chapter)', text):
            return "H1"
        
        # Use font size relative to document statistics
        if self.font_size_stats:
            font_sizes = sorted(self.font_size_stats.keys(), reverse=True)
            
            # Skip title font size
            available_sizes = [fs for fs in font_sizes if fs != self.title_font_size]
            
            if len(available_sizes) >= 1:
                if font_size >= available_sizes[0] - 1:  # Largest non-title
                    return "H1"
                elif len(available_sizes) >= 2 and font_size >= available_sizes[1] - 1:
                    return "H2"
                else:
                    return "H3"
        
        # Fallback pattern-based detection
        if re.match(r'^\d+\.\s+', text) and font_size >= 14:
            return "H1"
        elif re.match(r'^\d+\.\d+\s+', text):
            return "H2"
        elif re.match(r'^\d+\.\d+\.\d+\s+', text):
            return "H3"
        elif font_size >= 14:
            return "H1"
        elif font_size >= 12:
            return "H2"
        else:
            return "H3"
    
    def _clean_and_sort_headings(self, headings: List[Dict]) -> List[Dict]:
        seen = set()
        unique_headings = []
        
        for heading in headings:
            if "y_pos" in heading:
                del heading["y_pos"]
            
            # Skip items marked for skipping
            if heading.get("level") == "SKIP":
                continue
            
            key = (heading["text"], heading["page"])
            if key not in seen:
                seen.add(key)
                unique_headings.append(heading)
        
        return sorted(unique_headings, key=lambda x: x["page"])

def main():
    extractor = PDFStructureExtractor()
    pdf_folder = "pdfs"
    output_folder = "output"

    if not os.path.exists(pdf_folder):
        print(f"Error: PDF folder '{pdf_folder}' not found")
        return

    os.makedirs(output_folder, exist_ok=True)

    for file_name in os.listdir(pdf_folder):
        if file_name.lower().endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, file_name)
            print(f"Processing: {pdf_path}")
            
            result = extractor.extract_structure(pdf_path)
            
            json_file_name = os.path.splitext(file_name)[0] + "_structure.json"
            output_path = os.path.join(output_folder, json_file_name)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"Saved: {output_path}")

if __name__ == "__main__":
    main()








