import os
from datetime import datetime
from typing import List, Dict, Any

class OutputFormatter:
    def format_output(self, analyzed_results: Dict, input_files: List[str], 
                     persona: str, job_description: str) -> Dict[str, Any]:
        """Format the output according to challenge1b_output.json specification"""
        
        output = {
            "metadata": {
                "input_documents": [os.path.basename(f) for f in input_files],
                "persona": persona,
                "job_to_be_done": job_description,
                "processing_timestamp": datetime.now().isoformat()
            },
            "extracted_sections": [],
            "subsection_analysis": []
        }
        
        # Format main sections (top 15)
        sections = analyzed_results.get('sections', [])
        for section in sections[:15]:
            formatted_section = {
                "document": section['document'],
                "section_title": section['title'],
                "importance_rank": section['importance_rank'],
                "page_number": section['page']
            }
            output["extracted_sections"].append(formatted_section)
        
        # Format subsections (top 20)
        subsections = analyzed_results.get('subsections', [])
        for subsection in subsections[:20]:
            formatted_subsection = {
                "document": subsection['document'],
                "refined_text": subsection['refined_text'],
                "page_number": subsection['page_number']
            }
            output["subsection_analysis"].append(formatted_subsection)
        
        return output