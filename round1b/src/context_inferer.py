import re
from typing import Tuple, Dict, List, Optional
from collections import Counter

class DynamicContextInferer:
    def __init__(self):
        # Domain-specific keywords with weights
        self.domain_keywords = {
            'finance': {
                'keywords': ['revenue', 'profit', 'loss', 'financial', 'investment', 'market', 'stock', 
                            'earnings', 'budget', 'cash flow', 'balance sheet', 'income statement', 
                            'roi', 'expenses', 'assets', 'liabilities', 'dividend', 'growth', 'analysis'],
                'weight': 2.0
            },
            'travel': {
                'keywords': ['travel', 'trip', 'vacation', 'tourist', 'hotel', 'restaurant', 'city', 
                            'destination', 'guide', 'attraction', 'culture', 'food', 'cuisine', 
                            'accommodation', 'visit', 'explore', 'sightseeing', 'itinerary'],
                'weight': 2.0
            },
            'chemistry': {
                'keywords': ['reaction', 'compound', 'molecule', 'chemistry', 'organic', 'synthesis', 
                            'catalyst', 'equation', 'chemical', 'bond', 'acid', 'base', 'solution', 
                            'laboratory', 'experiment', 'formula', 'element'],
                'weight': 2.0
            },
            'research': {
                'keywords': ['research', 'study', 'analysis', 'methodology', 'data', 'results', 
                            'conclusion', 'hypothesis', 'experiment', 'survey', 'literature', 
                            'review', 'academic', 'scientific', 'journal', 'publication'],
                'weight': 1.8
            },
            'technology': {
                'keywords': ['software', 'algorithm', 'neural network', 'machine learning', 'ai', 
                            'artificial intelligence', 'computer', 'programming', 'code', 'database', 
                            'system', 'network', 'technology', 'digital', 'automation'],
                'weight': 1.8
            },
            'medical': {
                'keywords': ['patient', 'treatment', 'diagnosis', 'medical', 'health', 'disease', 
                            'symptoms', 'therapy', 'medicine', 'clinical', 'hospital', 'doctor', 
                            'pharmaceutical', 'drug', 'healthcare'],
                'weight': 1.8
            },
            'education': {
                'keywords': ['student', 'course', 'curriculum', 'learning', 'education', 'teaching', 
                            'school', 'university', 'exam', 'grade', 'assignment', 'lecture', 
                            'textbook', 'knowledge', 'skill'],
                'weight': 1.5
            },
            'legal': {
                'keywords': ['law', 'legal', 'court', 'judge', 'attorney', 'contract', 'agreement', 
                            'regulation', 'compliance', 'lawsuit', 'litigation', 'statute', 
                            'jurisdiction', 'evidence', 'testimony'],
                'weight': 1.8
            }
        }
        
        # Persona templates based on domains
        self.persona_templates = {
            'finance': [
                "Investment Analyst",
                "Financial Advisor",
                "Business Analyst",
                "Portfolio Manager",
                "Financial Planner"
            ],
            'travel': [
                "Travel Planner",
                "Tour Guide",
                "Travel Consultant",
                "Vacation Coordinator",
                "Destination Expert"
            ],
            'chemistry': [
                "Chemistry Student",
                "Research Chemist",
                "Laboratory Technician",
                "Chemical Engineer",
                "Organic Chemistry Researcher"
            ],
            'research': [
                "Research Analyst",
                "Academic Researcher",
                "Data Scientist",
                "Research Assistant",
                "PhD Researcher"
            ],
            'technology': [
                "Software Developer",
                "Data Scientist",
                "AI Researcher",
                "Systems Analyst",
                "Technical Consultant"
            ],
            'medical': [
                "Medical Student",
                "Healthcare Professional",
                "Clinical Researcher",
                "Medical Analyst",
                "Healthcare Consultant"
            ],
            'education': [
                "Student",
                "Educator",
                "Academic Advisor",
                "Curriculum Developer",
                "Learning Specialist"
            ],
            'legal': [
                "Legal Analyst",
                "Paralegal",
                "Legal Researcher",
                "Contract Specialist",
                "Compliance Officer"
            ]
        }
        
        # Job description templates
        self.job_templates = {
            'finance': [
                "Analyze financial performance, trends, and investment opportunities.",
                "Evaluate market conditions and provide investment recommendations.",
                "Assess financial risks and develop strategic plans.",
                "Review financial statements and prepare analytical reports."
            ],
            'travel': [
                "Plan comprehensive trips including accommodation, activities, and local guidance.",
                "Create detailed itineraries for optimal travel experiences.",
                "Research destinations and provide travel recommendations.",
                "Coordinate group travel arrangements and activities."
            ],
            'chemistry': [
                "Study chemical reactions, compounds, and molecular structures.",
                "Prepare for examinations on organic chemistry topics and mechanisms.",
                "Analyze chemical processes and experimental results.",
                "Research chemical synthesis and reaction pathways."
            ],
            'research': [
                "Conduct comprehensive literature reviews and data analysis.",
                "Prepare research summaries focusing on methodologies and findings.",
                "Analyze academic papers and extract key insights.",
                "Synthesize research findings for academic or professional purposes."
            ],
            'technology': [
                "Develop and implement technical solutions and algorithms.",
                "Analyze system requirements and design specifications.",
                "Research emerging technologies and best practices.",
                "Create technical documentation and implementation guides."
            ],
            'medical': [
                "Analyze medical research and clinical findings.",
                "Study patient care protocols and treatment methodologies.",
                "Review healthcare literature and best practices.",
                "Examine medical procedures and diagnostic techniques."
            ],
            'education': [
                "Develop learning materials and educational content.",
                "Analyze curriculum requirements and learning objectives.",
                "Create study guides and educational resources.",
                "Review academic materials for comprehension and retention."
            ],
            'legal': [
                "Analyze legal documents and regulatory requirements.",
                "Research case law and legal precedents.",
                "Review contracts and compliance documentation.",
                "Examine legal procedures and statutory requirements."
            ]
        }

    def infer_persona_and_job(self, text: str) -> Tuple[str, str]:
        """Dynamically infer persona and job based on text content"""
        if not text or len(text.strip()) < 50:
            return "General User", "Extract and summarize the most relevant insights from the documents."
        
        # Clean and prepare text
        clean_text = self._clean_text(text)
        
        # Calculate domain scores
        domain_scores = self._calculate_domain_scores(clean_text)
        
        # Debug: Print domain scores
        print(f"Domain scores: {domain_scores}")
        
        # Get the top domain
        top_domain = max(domain_scores.items(), key=lambda x: x[1])
        print(f"Top domain: {top_domain}")
        
        # Lower threshold for better detection and add fallback logic
        if top_domain[1] < 0.01:  # Much lower threshold
            # Try to detect based on common patterns
            fallback_result = self._fallback_detection(clean_text)
            if fallback_result:
                return fallback_result
            return "General User", "Extract and summarize the most relevant insights from the documents."
        
        # Select persona and job based on top domain
        domain_name = top_domain[0]
        persona = self._select_persona(domain_name, clean_text)
        job_description = self._select_job_description(domain_name, clean_text)
        
        print(f"Selected persona: {persona}")
        print(f"Selected job: {job_description}")
        
        return persona, job_description

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text

    def _calculate_domain_scores(self, text: str) -> Dict[str, float]:
        """Calculate relevance scores for each domain"""
        words = text.split()
        word_count = len(words)
        
        if word_count == 0:
            return {domain: 0.0 for domain in self.domain_keywords.keys()}
        
        domain_scores = {}
        
        for domain, config in self.domain_keywords.items():
            keywords = config['keywords']
            weight = config['weight']
            
            # Count keyword matches
            matches = sum(1 for word in words if word in keywords)
            
            # Calculate weighted score
            base_score = matches / word_count
            weighted_score = base_score * weight
            
            domain_scores[domain] = weighted_score
        
        return domain_scores

    def _select_persona(self, domain: str, text: str) -> str:
        """Select appropriate persona based on domain and text content"""
        personas = self.persona_templates.get(domain, ["General User"])
        
        # Simple heuristic based on text characteristics
        if 'student' in text or 'exam' in text or 'study' in text:
            # Prefer student/learning personas
            student_personas = [p for p in personas if 'student' in p.lower() or 'researcher' in p.lower()]
            if student_personas:
                return student_personas[0]
        
        if 'analysis' in text or 'report' in text or 'review' in text:
            # Prefer analyst personas
            analyst_personas = [p for p in personas if 'analyst' in p.lower() or 'advisor' in p.lower()]
            if analyst_personas:
                return analyst_personas[0]
        
        # Default to first persona in the list
        return personas[0]

    def _fallback_detection(self, text: str) -> Optional[Tuple[str, str]]:
        """Fallback detection for common patterns"""
        text_lower = text.lower()
        
        # Travel detection patterns
        travel_indicators = ['france', 'city', 'cities', 'restaurant', 'hotel', 'tourism', 
                           'culture', 'tradition', 'cuisine', 'attraction', 'destination',
                           'guide', 'visit', 'explore', 'sightseeing', 'vacation']
        travel_count = sum(1 for word in travel_indicators if word in text_lower)
        
        # Business/Finance detection
        business_indicators = ['revenue', 'financial', 'business', 'company', 'market', 
                             'profit', 'analysis', 'investment', 'growth', 'performance']
        business_count = sum(1 for word in business_indicators if word in text_lower)
        
        # Academic/Research detection  
        academic_indicators = ['research', 'study', 'academic', 'paper', 'journal', 
                             'methodology', 'literature', 'findings', 'conclusion']
        academic_count = sum(1 for word in academic_indicators if word in text_lower)
        
        # Medical detection
        medical_indicators = ['patient', 'medical', 'health', 'treatment', 'clinical',
                            'diagnosis', 'therapy', 'medicine', 'healthcare']
        medical_count = sum(1 for word in medical_indicators if word in text_lower)
        
        # Technology detection
        tech_indicators = ['software', 'algorithm', 'programming', 'system', 'network',
                         'technology', 'computer', 'data', 'artificial intelligence']
        tech_count = sum(1 for word in tech_indicators if word in text_lower)
        
        # Determine best match
        counts = {
            'travel': travel_count,
            'finance': business_count,
            'research': academic_count,
            'medical': medical_count,
            'technology': tech_count
        }
        
        max_count = max(counts.values())
        if max_count >= 3:  # At least 3 domain-specific words
            best_domain = max(counts.items(), key=lambda x: x[1])[0]
            persona = self._select_persona(best_domain, text)
            job = self._select_job_description(best_domain, text)
            print(f"Fallback detection found: {best_domain} (score: {max_count})")
            return persona, job
        
        return None

    def _select_job_description(self, domain: str, text: str) -> str:
        """Select appropriate job description based on domain and text content"""
        jobs = self.job_templates.get(domain, ["Extract and summarize the most relevant insights from the documents."])
        
        # Simple heuristic based on text characteristics
        if 'analysis' in text or 'analyze' in text:
            analysis_jobs = [j for j in jobs if 'analy' in j.lower()]
            if analysis_jobs:
                return analysis_jobs[0]
        
        if 'plan' in text or 'planning' in text:
            planning_jobs = [j for j in jobs if 'plan' in j.lower()]
            if planning_jobs:
                return planning_jobs[0]
        
        if 'study' in text or 'research' in text:
            research_jobs = [j for j in jobs if 'research' in j.lower() or 'study' in j.lower()]
            if research_jobs:
                return research_jobs[0]
        
        # Default to first job in the list
        return jobs[0]

# For backward compatibility
def infer_persona_and_job(text: str) -> Tuple[str, str]:
    """Backward compatible function"""
    inferer = DynamicContextInferer()
    return inferer.infer_persona_and_job(text)