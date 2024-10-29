from fastapi import FastAPI, HTTPException, UploadFile, File
from pathlib import Path
import aiofiles
from datetime import datetime
import os
import uvicorn

from models import Query, AnalysisResponse
from analyzer import PolicyAnalyzer
from fastapi.middleware.cors import CORSMiddleware
from CodeFileParser import CodeFileParser

code_parser = CodeFileParser()


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

@app.post("/upload/", summary="Upload a document or code file")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document or code file"""
    if not code_parser.is_supported_file(Path(file.filename)):
        supported_extensions = ', '.join(code_parser.supported_extensions.keys())
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Supported types: {supported_extensions}"
        )
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    doc_id = f"{os.path.splitext(file.filename)[0]}_{timestamp}"
    file_path = UPLOAD_DIR / f"{doc_id}{Path(file.filename).suffix}"
    
    try:
        # Save uploaded file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Parse the file
        parsed_content = await code_parser.parse_file(file_path)
        if parsed_content:
            # Convert parsed content to analyzable text
            analysis_text = await convert_parsed_content_to_text(parsed_content)
            # Process the document using existing analyzer
            await analyzer.analyze_document(analysis_text, doc_id)
        
        return {
            "message": "Document processed successfully",
            "doc_id": doc_id,
            "parsed_content": parsed_content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def convert_parsed_content_to_text(parsed_content: dict) -> str:
    """Convert parsed content to analyzable text format"""
    sections = []
    
    for key, value in parsed_content.items():
        if isinstance(value, list):
            sections.append(f"=== {key.upper()} ===")
            sections.extend(value)
        elif isinstance(value, str):
            sections.append(f"=== {key.upper()} ===")
            sections.append(value)
    
    return "\n\n".join(sections)

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
    return {"topics": list(analyzer.all_topics)}

@app.get("/get_existing_documents/", summary="Get existing documents")
async def get_existing_documents():
    """Get list of existing documents, without including .git .DS_Store etc."""
    return {"files": [f.name for f in UPLOAD_DIR.iterdir() if f.is_file() and not f.name.startswith(".")], 
            "file_contents": [f.read_text() for f in UPLOAD_DIR.iterdir() if f.is_file() and not f.name.startswith(".")]}
    
    

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)