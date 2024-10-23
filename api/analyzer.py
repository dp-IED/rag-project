from collections import defaultdict
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from typing import List, Dict, Set

class PolicyAnalyzer:
    def __init__(self):
        # Download NLTK data at startup
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.policy_positions = defaultdict(list)
        self.context_map = defaultdict(list)
        
    async def analyze_document(self, text: str, doc_id: str):
        """Async version of document analysis"""
        sentences = sent_tokenize(text)
        
        for i, sentence in enumerate(sentences):
            start = max(0, i - 2)
            end = min(len(sentences), i + 3)
            context = sentences[start:end]
            
            if self.is_policy_relevant(sentence):
                self.policy_positions[doc_id].append(sentence)
                self.context_map[sentence] = {
                    'context': context,
                    'doc_id': doc_id,
                    'topics': self.extract_topics(sentence)
                }
    
    def is_policy_relevant(self, text: str) -> bool:
        relevant_terms = {
            'policy', 'strategy', 'initiative', 'regulation', 'law',
            'governance', 'framework', 'approach', 'position', 'stance',
            'development', 'implementation', 'ai', 'artificial intelligence',
            'declare', 'announce', 'establish', 'create', 'propose'
        }
        return any(term in text.lower() for term in relevant_terms)
    
    def extract_topics(self, text: str) -> Set[str]:
        topics = {
            'regulation': {'regulation', 'law', 'compliance', 'rules'},
            'safety': {'safety', 'security', 'protection', 'risk'},
            'ethics': {'ethics', 'ethical', 'responsibility', 'principles'},
            'development': {'development', 'research', 'innovation'},
            'governance': {'governance', 'oversight', 'control'},
            'implementation': {'implementation', 'deployment', 'adoption'}
        }
        
        text_lower = text.lower()
        return {topic for topic, keywords in topics.items() 
                if any(keyword in text_lower for keyword in keywords)}

    def get_relevant_responses(self, query: str, max_responses: int = 3) -> List[Dict]:
        query_lower = query.lower()
        query_topics = self.extract_topics(query)
        
        scored_responses = []
        for statement, info in self.context_map.items():
            score = len(query_topics.intersection(info['topics'])) * 2
            score += len(set(statement.lower().split()).intersection(set(query_lower.split())))
            
            if score > 0:
                scored_responses.append({
                    'statement': statement,
                    'score': score,
                    'source': info['doc_id'],
                    'context': info['context'],
                    'topics': list(info['topics'])  # Convert set to list for JSON serialization
                })
        
        return sorted(scored_responses, key=lambda x: x['score'], reverse=True)[:max_responses]