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
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5174",
        "*"  # Allow all origins in development (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
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
    print(f"Received chat request: {request.message[:50]}...")
    
    if not chat_model.is_loaded():
        print("ERROR: Model not loaded!")
        raise HTTPException(
            status_code=503, 
            detail="Model not loaded yet. Please wait a few moments and try again."
        )
    
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        # Get reply from model
        print(f"Generating reply for: {request.message[:50]}...")
        reply = chat_model.generate_reply(
            message=request.message,
            history=request.history or []
        )
        
        print(f"Generated reply: {reply[:100] if reply else 'EMPTY'}...")
        
        if not reply or not reply.strip():
            print("WARNING: Empty reply generated, using fallback")
            reply = "Désolé, je n'ai pas pu générer de réponse. Veuillez réessayer avec une question plus précise sur le domaine pharmaceutique et de la santé."
        
        return ChatResponse(
            reply=reply,
            usage={
                "model": chat_model.model_name,
                "tokens": len(reply.split())  # Approximate token count
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR generating reply: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return a helpful error message instead of crashing
        return ChatResponse(
            reply=f"Désolé, une erreur s'est produite lors de la génération de la réponse. Erreur: {str(e)}. Veuillez réessayer avec une question sur le domaine pharmaceutique et de la santé.",
            usage={
                "model": chat_model.model_name if chat_model.model_name else "unknown",
                "tokens": 0
            }
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

