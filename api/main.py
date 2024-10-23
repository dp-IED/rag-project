from fastapi import FastAPI, HTTPException, UploadFile, File
from pathlib import Path
import aiofiles
from datetime import datetime
import os
import uvicorn

from models import Query, AnalysisResponse
from analyzer import PolicyAnalyzer
from fastapi.middleware.cors import CORSMiddleware


# Initialize FastAPI app
app = FastAPI(
    title="Policy Analyzer API",
    description="API for analyzing policy documents and retrieving relevant information",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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