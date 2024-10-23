from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
import shutil
from typing import List, Dict, Optional
import os
from pathlib import Path
import uvicorn
import aiofiles
import asyncio
from datetime import datetime

# Import your existing PolicyAnalyzer class
from collections import defaultdict
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Your existing PolicyAnalyzer class (with minor modifications for async)
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
    
    def extract_topics(self, text: str) -> set:
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

# Pydantic models for request/response validation
class Query(BaseModel):
    text: str
    max_responses: Optional[int] = 3

class PolicyResponse(BaseModel):
    statement: str
    score: float
    source: str
    context: List[str]
    topics: List[str]

class AnalysisResponse(BaseModel):
    responses: List[PolicyResponse]

# Initialize FastAPI app and PolicyAnalyzer
app = FastAPI(
    title="Policy Analyzer API",
    description="API for analyzing policy documents and retrieving relevant information",
    version="1.0.0"
)

# Create upload directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Global analyzer instance
analyzer = PolicyAnalyzer()

async def process_document(file_path: Path, doc_id: str):
    """Process a document asynchronously"""
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        await analyzer.analyze_document(content, doc_id)
    except UnicodeDecodeError:
        # Fallback to latin-1 encoding if UTF-8 fails
        async with aiofiles.open(file_path, 'r', encoding='latin-1') as f:
            content = await f.read()
        await analyzer.analyze_document(content, doc_id)

@app.post("/upload/", summary="Upload a policy document")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a policy document"""
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    doc_id = f"{os.path.splitext(file.filename)[0]}_{timestamp}"
    file_path = UPLOAD_DIR / f"{doc_id}.txt"
    
    try:
        # Save uploaded file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Process the document
        await process_document(file_path, doc_id)
        
        return {"message": "Document processed successfully", "doc_id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/", response_model=AnalysisResponse, summary="Query policy documents")
async def query_documents(query: Query):
    """Query processed policy documents"""
    try:
        responses = analyzer.get_relevant_responses(query.text, query.max_responses)
        return {"responses": responses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/topics/", summary="Get available topics")
async def get_topics():
    """Get list of available topics"""
    return {
        "topics": [
            "regulation",
            "safety",
            "ethics",
            "development",
            "governance",
            "implementation"
        ]
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
