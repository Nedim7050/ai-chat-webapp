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
from app.api_model import APIChatModel
import os

# Initialize models - try API first, fallback to local model
api_model = APIChatModel()
chat_model = ChatModel()

# Determine which model to use
USE_API = os.getenv("USE_API", "true").lower() == "true" and api_model.is_loaded()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup"""
    if USE_API:
        print("Using API model (OpenAI/Gemini)...")
        if api_model.is_loaded():
            print("API model ready!")
        else:
            print("WARNING: API not configured, falling back to local model")
            print("Set OPENAI_API_KEY or GEMINI_API_KEY environment variable to use API")
            print("Loading local model as fallback...")
            chat_model.load_model()
            print("Local model loaded successfully!")
    else:
        print("Loading local AI model...")
        chat_model.load_model()
        print("Local model loaded successfully!")
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
    if USE_API:
        return {
            "status": "healthy",
            "model_loaded": api_model.is_loaded(),
            "model_type": "api",
            "api_type": api_model.api_type
        }
    else:
        return {
            "status": "healthy",
            "model_loaded": chat_model.is_loaded(),
            "model_type": "local"
        }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint: accepts message and history, returns AI reply
    Uses API if available, otherwise falls back to local model
    """
    print(f"Received chat request: {request.message[:50]}...")
    
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Try API first if configured
    if USE_API and api_model.is_loaded():
        try:
            print(f"Using API model ({api_model.api_type}) for: {request.message[:50]}...")
            reply = api_model.generate_reply(
                message=request.message,
                history=request.history or []
            )
            print(f"API generated reply: {reply[:100] if reply else 'EMPTY'}...")
            
            if reply and reply.strip():
                return ChatResponse(
                    reply=reply,
                    usage={
                        "model": f"{api_model.api_type}-{api_model.model_name}",
                        "tokens": len(reply.split())
                    }
                )
        except Exception as e:
            print(f"API error, falling back to local model: {str(e)}")
            # Fall through to local model
    
    # Fallback to local model
    if not chat_model.is_loaded():
        print("ERROR: Neither API nor local model available!")
        raise HTTPException(
            status_code=503, 
            detail="Model not available. Please configure API key or wait for local model to load."
        )
    
    try:
        print(f"Using local model for: {request.message[:50]}...")
        reply = chat_model.generate_reply(
            message=request.message,
            history=request.history or []
        )
        
        print(f"Local model generated reply: {reply[:100] if reply else 'EMPTY'}...")
        
        if not reply or not reply.strip():
            print("WARNING: Empty reply generated, using fallback")
            reply = "Désolé, je n'ai pas pu générer de réponse. Veuillez réessayer avec une question plus précise sur le domaine pharmaceutique et de la santé."
        
        return ChatResponse(
            reply=reply,
            usage={
                "model": chat_model.model_name,
                "tokens": len(reply.split())
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR generating reply: {str(e)}")
        import traceback
        traceback.print_exc()
        return ChatResponse(
            reply=f"Désolé, une erreur s'est produite. Veuillez réessayer avec une question sur le domaine pharmaceutique et de la santé.",
            usage={
                "model": "error",
                "tokens": 0
            }
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

