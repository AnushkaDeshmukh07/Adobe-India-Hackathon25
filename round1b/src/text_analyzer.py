import re
import numpy as np
from typing import List, Dict, Any
import os

# Import with fallbacks
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("scikit-learn not available, using fallback methods")

# Use lightweight models for offline operation
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("sentence-transformers not available, using fallback methods")

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import sent_tokenize, word_tokenize
    NLTK_AVAILABLE = True
    
    # Set NLTK data path to local directory
    nltk_data_path = os.path.join(os.path.dirname(__file__), 'nltk_data')
    if os.path.exists(nltk_data_path):
        nltk.data.path.insert(0, nltk_data_path)
    
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
    except LookupError:
        print("NLTK data not found, using basic text processing")
        NLTK_AVAILABLE = False
except ImportError:
    NLTK_AVAILABLE = False
    print("NLTK not available, using basic text processing")

class TextAnalyzer:
    def __init__(self):
        # Initialize components based on availability
        self.model = None
        self.model_loaded = False
        
        # Load lightweight model only if available and needed
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                import warnings
                warnings.filterwarnings("ignore", category=FutureWarning)
                
                # Use a smaller, faster model
                model_name = 'all-MiniLM-L6-v2'  # ~90MB model
                self.model = SentenceTransformer(model_name)
                self.model_loaded = True
                print(f"Loaded sentence transformer model: {model_name}")
            except Exception as e:
                print(f"Failed to load sentence transformer: {e}")
                self.model = None
        
        # Initialize stop words
        if NLTK_AVAILABLE:
            try:
                self.stop_words = set(stopwords.words('english'))
            except:
                self.stop_words = self._get_default_stopwords()
        else:
            self.stop_words = self._get_default_stopwords()
        
        # Initialize TF-IDF vectorizer
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(
                max_features=500,  # Reduced for speed
                stop_words='english',
                ngram_range=(1, 2),
                max_df=0.8,
                min_df=2
            )
        else:
            self.vectorizer = None
    
    def _get_default_stopwords(self):
        """Default stopwords list for when NLTK is not available"""
        return set([
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 
            'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 
            'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        ])
    
    def analyze_documents(self, documents: List[Dict], persona: str, job_description: str) -> Dict[str, Any]:
        """Analyze documents and rank sections based on persona and job"""
        
        # Combine persona and job for query vector
        query_text = f"{persona} {job_description}"
        
        # Extract all sections from all documents
        all_sections = []
        for doc in documents:
            for section in doc['sections']:
                section['document'] = doc['filename']
                all_sections.append(section)
        
        if not all_sections:
            return {'sections': [], 'subsections': []}
        
        print(f"Analyzing {len(all_sections)} sections...")
        
        # Calculate relevance scores
        section_scores = self._calculate_section_relevance(all_sections, query_text)
        
        # Rank sections
        ranked_sections = self._rank_sections(all_sections, section_scores)
        
        # Extract and rank subsections from top sections
        top_sections = ranked_sections[:min(15, len(ranked_sections))]
        ranked_subsections = self._extract_and_rank_subsections(top_sections, query_text)
        
        return {
            'sections': ranked_sections,
            'subsections': ranked_subsections
        }
    
    def _calculate_section_relevance(self, sections: List[Dict], query: str) -> List[float]:
        """Calculate relevance scores for sections"""
        section_texts = []
        for section in sections:
            # Combine title and content for better matching
            combined_text = f"{section['title']} {section['content']}"
            section_texts.append(combined_text)
        
        if not section_texts:
            return []
        
        # Try semantic similarity first (if model is loaded)
        if self.model_loaded and self.model is not None:
            try:
                print("Using semantic similarity...")
                return self._semantic_similarity(section_texts, query)
            except Exception as e:
                print(f"Semantic similarity error: {e}, falling back to TF-IDF")
        
        # Fallback to TF-IDF
        if SKLEARN_AVAILABLE and self.vectorizer is not None:
            print("Using TF-IDF similarity...")
            return self._tfidf_similarity(section_texts, query)
        
        # Ultimate fallback - keyword matching
        print("Using keyword similarity...")
        return [self._keyword_similarity(text, query) for text in section_texts]
    
    def _semantic_similarity(self, texts: List[str], query: str) -> List[float]:
        """Semantic similarity using sentence transformers"""
        try:
            # Encode query and texts in batches for efficiency
            query_embedding = self.model.encode([query], show_progress_bar=False)
            
            # Process texts in batches to manage memory
            batch_size = 32
            all_similarities = []
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_embeddings = self.model.encode(batch_texts, show_progress_bar=False)
                
                # Calculate cosine similarity for this batch
                batch_similarities = cosine_similarity(query_embedding, batch_embeddings)[0]
                all_similarities.extend(batch_similarities)
            
            # Normalize scores to 0-1 range
            similarities = np.array(all_similarities)
            if len(similarities) > 1:
                min_sim = similarities.min()
                max_sim = similarities.max()
                if max_sim > min_sim:
                    similarities = (similarities - min_sim) / (max_sim - min_sim)
            
            return similarities.tolist()
            
        except Exception as e:
            print(f"Error in semantic similarity: {e}")
            raise e
    
    def _tfidf_similarity(self, texts: List[str], query: str) -> List[float]:
        """TF-IDF similarity calculation"""
        try:
            all_texts = texts + [query]
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # Get similarity between query and each text
            query_vector = tfidf_matrix[-1]
            text_vectors = tfidf_matrix[:-1]
            
            similarities = cosine_similarity(query_vector, text_vectors)[0]
            return similarities.tolist()
            
        except Exception as e:
            print(f"TF-IDF error: {e}")
            # Ultimate fallback - keyword matching
            return [self._keyword_similarity(text, query) for text in texts]
    
    def _keyword_similarity(self, text: str, query: str) -> float:
        """Enhanced keyword-based similarity"""
        # Basic tokenization
        text_words = set(word.lower() for word in re.findall(r'\b\w+\b', text) if len(word) > 2)
        query_words = set(word.lower() for word in re.findall(r'\b\w+\b', query) if len(word) > 2)
        
        # Remove stop words
        text_words -= self.stop_words
        query_words -= self.stop_words
        
        if not query_words:
            return 0.0
        
        intersection = text_words & query_words
        
        # Enhanced scoring with domain-specific boost
        domain_keywords = {
            'travel': ['travel', 'trip', 'visit', 'plan', 'tourism', 'tourist', 'vacation', 
                      'destination', 'guide', 'explore', 'attraction', 'activity', 'restaurant', 
                      'hotel', 'city', 'culture', 'food', 'cuisine', 'history'],
            'finance': ['revenue', 'profit', 'financial', 'investment', 'market', 'analysis', 
                       'budget', 'cost', 'income', 'growth', 'performance'],
            'research': ['research', 'study', 'analysis', 'methodology', 'data', 'results', 
                        'findings', 'literature', 'academic', 'scientific'],
            'technology': ['technology', 'software', 'system', 'network', 'algorithm', 
                          'programming', 'development', 'innovation'],
            'education': ['education', 'learning', 'student', 'course', 'curriculum', 
                         'teaching', 'knowledge', 'skill']
        }
        
        # Base similarity score
        base_score = len(intersection) / len(query_words)
        
        # Apply domain boost
        domain_boost = 0.0
        for domain, keywords in domain_keywords.items():
            domain_matches = len(intersection & set(keywords))
            if domain_matches > 0:
                domain_boost += domain_matches * 0.15
        
        # Combine base score and domain boost
        final_score = min(base_score + domain_boost, 1.0)
        
        return final_score
    
    def _rank_sections(self, sections: List[Dict], scores: List[float]) -> List[Dict]:
        """Rank sections by relevance score"""
        if len(sections) != len(scores):
            return sections
        
        # Combine sections with scores and sort
        section_score_pairs = list(zip(sections, scores))
        section_score_pairs.sort(key=lambda x: x[1], reverse=True)
        
        # Add importance rank and relevance score
        ranked_sections = []
        for i, (section, score) in enumerate(section_score_pairs):
            section_copy = section.copy()
            section_copy['importance_rank'] = i + 1
            section_copy['relevance_score'] = float(score)
            ranked_sections.append(section_copy)
        
        return ranked_sections
    
    def _extract_and_rank_subsections(self, sections: List[Dict], query: str) -> List[Dict]:
        """Extract and rank subsections from top sections"""
        subsections = []
        
        for section in sections:
            content = section['content']
            
            # Split content into sentences
            sentences = self._split_sentences(content)
            
            # Create subsections from sentences (group 2-3 sentences)
            for i in range(0, len(sentences), 2):
                subsection_text = ' '.join(sentences[i:i+3]).strip()
                if len(subsection_text) > 100:  # Only meaningful subsections
                    subsection = {
                        'document': section['document'],
                        'parent_section': section['title'],
                        'refined_text': subsection_text,
                        'page_number': section['page']
                    }
                    subsections.append(subsection)
        
        # Calculate relevance for subsections
        if subsections:
            subsection_texts = [sub['refined_text'] for sub in subsections]
            
            # Use simpler scoring for subsections to maintain speed
            scores = [self._keyword_similarity(text, query) for text in subsection_texts]
            
            # Rank subsections
            if len(scores) == len(subsections):
                subsection_score_pairs = list(zip(subsections, scores))
                subsection_score_pairs.sort(key=lambda x: x[1], reverse=True)
                ranked_subsections = [sub for sub, score in subsection_score_pairs]
            else:
                ranked_subsections = subsections
            
            return ranked_subsections[:20]  # Return top 20 subsections
        
        return []
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        if NLTK_AVAILABLE:
            try:
                return sent_tokenize(text)
            except:
                pass
        
        # Fallback sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]