"""
FastAPI backend for AI Chat Webapp
Provides /health and /chat endpoints
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
import uvicorn
from app.model import ChatModel

# Initialize model singleton
chat_model = ChatModel()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup"""
    print("Loading AI model...")
    chat_model.load_model()
    print("Model loaded successfully!")
    yield
    # Cleanup if needed
    print("Shutting down...")


app = FastAPI(
    title="AI Chat API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = []


class ChatResponse(BaseModel):
    reply: str
    usage: Dict[str, Any]


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": chat_model.is_loaded()
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint: accepts message and history, returns AI reply
    """
    if not chat_model.is_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded yet")
    
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        # Get reply from model
        reply = chat_model.generate_reply(
            message=request.message,
            history=request.history
        )
        
        return ChatResponse(
            reply=reply,
            usage={
                "model": chat_model.model_name,
                "tokens": len(reply.split())  # Approximate token count
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating reply: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

