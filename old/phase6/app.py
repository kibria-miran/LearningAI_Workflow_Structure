# Phase 6 - app.py: Main FastAPI application
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="RAG Application API",
    description="Phase 6: RAG system deployed with Docker + n8n",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "rag-app"}

# Simple query endpoint
@app.post("/query")
async def query_rag(query: str):
    """Simple RAG query endpoint."""
    from phase4.ask import rag_answer
    
    try:
        result = rag_answer(query)
        if result.get("refused"):
            raise HTTPException(status_code=404, detail="No relevant information found")
        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "cost": result["cost"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint
@app.get("/")
async def root():
    return {"message": "RAG Application is running", "version": "1.0.0"}