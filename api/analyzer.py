from collections import defaultdict
from pathlib import Path
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from typing import List, Dict, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np

import string


UPLOAD_DIR = Path("uploads")

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
        self.all_topics = set()  # Store unique topics
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.documents_text = self.get_existing_documents() 
        
        
    def get_existing_documents(self):
        return [f.read_text() for f in UPLOAD_DIR.iterdir() if f.is_file() and not f.name.startswith(".")]
        
        
        
    async def analyze_document(self, text: str, doc_id: str):
        """Async version of document analysis with dynamic topic extraction"""
        sentences = sent_tokenize(text)
        self.documents_text.append(text)
        
        # Extract topics when we have enough documents
        if len(self.documents_text) >= 1:
            self._extract_topics_from_documents()
        
        for i, sentence in enumerate(sentences):
            start = max(0, i - 2)
            end = min(len(sentences), i + 3)
            context = sentences[start:end]
            
            if self.is_policy_relevant(sentence):
                self.policy_positions[doc_id].append(sentence)
                # Now using dynamically extracted topics
                sentence_topics = self.extract_topics_from_text(sentence)
                self.context_map[sentence] = {
                    'context': context,
                    'doc_id': doc_id,
                    'topics': sentence_topics
                }
    
    def is_policy_relevant(self, text: str) -> bool:
        relevant_terms = {
            'policy', 'strategy', 'initiative', 'regulation', 'law',
            'governance', 'framework', 'approach', 'position', 'stance',
            'development', 'implementation', 'ai', 'artificial intelligence',
            'declare', 'announce', 'establish', 'create', 'propose'
        }
        return any(term in text.lower() for term in relevant_terms)
    
    def _extract_topics_from_documents(self, num_topics: int = 10):
        """Extract topics from all documents using TF-IDF and clustering"""
        try:
            # Create TF-IDF matrix
            tfidf_matrix = self.vectorizer.fit_transform(self.documents_text)
            
            # Perform clustering
            kmeans = KMeans(n_clusters=min(num_topics, len(self.documents_text)), random_state=42)
            kmeans.fit(tfidf_matrix)
            
            # Get top terms for each cluster
            order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
            terms = self.vectorizer.get_feature_names_out()
            
            # Store topics
            self.all_topics.clear()
            for i in range(len(kmeans.cluster_centers_)):
                topic_terms = [terms[ind] for ind in order_centroids[i, :5]]
                print(f"Topic {i}: {topic_terms}")
                self.all_topics = self.all_topics.union(set(topic_terms))
                
        except Exception as e:
            print(f"Error in topic extraction: {str(e)}")
            # Fallback to some default topics if extraction fails
            self.all_topics = {
                "regulation", "safety", "ethics", "development",
                "governance", "implementation"
            }
    
    def extract_topics_from_text(self, text: str) -> Set[str]:
        """Extract topics for a specific piece of text"""
        if not self.all_topics:  # If no topics extracted yet
            return set("general")
            
        try:
            # Transform the text using the same vectorizer
            text_vector = self.vectorizer.transform([text])
            
            # Find similar topics based on term overlap
            topics = set()
            for topic in self.all_topics:
                topic_terms = set(topic.split())
                text_terms = set(word_tokenize(text.lower()))
                if len(topic_terms.intersection(text_terms)) > 0:
                    topics.add(topic)
            
            return topics
            
        except Exception as e:
            print(f"Error in text topic extraction: {str(e)}")
            return set()

    def get_all_topics(self) -> List[str]:
        """Get all currently extracted topics"""
        return list(self.all_topics)

    def get_relevant_responses(self, query: str, max_responses: int = 3) -> List[Dict]:
        query_lower = query.lower()
        query_topics = self.extract_topics_from_text(query)
        
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
                    'topics': list(info['topics'])
                })
        
        return sorted(scored_responses, key=lambda x: x['score'], reverse=True)[:max_responses]
    
    
    