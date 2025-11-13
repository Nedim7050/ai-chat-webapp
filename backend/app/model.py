"""
Model wrapper for loading and using Hugging Face transformer models
"""
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from typing import List, Dict, Optional


class ChatModel:
    """
    Singleton wrapper for Hugging Face conversational model
    Uses DialoGPT-small or conversational pipeline
    """
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-small"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self._loaded = False
    
    def load_model(self):
        """Load the model and tokenizer"""
        if self._loaded:
            return
        
        try:
            print(f"Loading model: {self.model_name}")
            
            # Use conversational pipeline for simplicity
            # This handles DialoGPT and other conversational models
            device = 0 if torch.cuda.is_available() else -1  # Use GPU if available, else CPU
            self.pipeline = pipeline(
                "conversational",
                model=self.model_name,
                tokenizer=self.model_name,
                device=device,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            )
            
            self._loaded = True
            print("Model loaded successfully!")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Falling back to simpler model...")
            # Fallback to a smaller model if DialoGPT fails
            try:
                self.model_name = "gpt2"
                self.pipeline = pipeline(
                    "text-generation",
                    model="gpt2",
                    device=-1
                )
                self._loaded = True
            except Exception as e2:
                print(f"Fallback also failed: {e2}")
                raise
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self._loaded
    
    def generate_reply(self, message: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Generate a reply given a message and conversation history
        
        Args:
            message: User's message
            history: List of previous messages in format [{"role": "user", "content": "..."}, ...]
        
        Returns:
            Generated reply string
        """
        if not self._loaded:
            raise RuntimeError("Model not loaded")
        
        if history is None:
            history = []
        
        try:
            # Convert history to format expected by pipeline
            from transformers import Conversation
            
            conversation = Conversation()
            
            # Add history
            for msg in history:
                if msg.get("role") == "user":
                    conversation.add_user_input(msg.get("content", ""))
                elif msg.get("role") == "assistant":
                    conversation.append_response(msg.get("content", ""))
            
            # Add current message
            conversation.add_user_input(message)
            
            # Generate reply
            result = self.pipeline(conversation)
            
            # Extract reply
            if hasattr(result, 'generated_responses') and result.generated_responses:
                reply = result.generated_responses[-1]
            elif isinstance(result, Conversation):
                reply = result.generated_responses[-1] if result.generated_responses else "I'm sorry, I couldn't generate a response."
            else:
                reply = str(result)
            
            return reply.strip()
            
        except Exception as e:
            # Fallback for simpler models
            if "conversational" not in str(type(self.pipeline)).lower():
                # For text-generation models, use simple prompt
                prompt = message
                if history:
                    # Build context from history
                    context = "\n".join([
                        f"User: {msg.get('content', '')}" if msg.get('role') == 'user' 
                        else f"Assistant: {msg.get('content', '')}"
                        for msg in history[-3:]  # Last 3 messages for context
                    ])
                    prompt = f"{context}\nUser: {message}\nAssistant:"
                
                result = self.pipeline(
                    prompt,
                    max_length=len(prompt.split()) + 50,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True
                )
                
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    # Extract only the new part
                    reply = generated_text.replace(prompt, "").strip()
                    return reply if reply else "I'm processing your message..."
            
            raise Exception(f"Error generating reply: {str(e)}")

