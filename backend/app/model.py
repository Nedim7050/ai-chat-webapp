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
            
            # Load tokenizer and model directly for better control
            device = 0 if torch.cuda.is_available() else -1
            
            # Try to load as conversational model first
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
                )
                
                # Set pad_token if not exists
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                
                # Move to device
                if device >= 0:
                    self.model = self.model.to(device)
                else:
                    self.model = self.model.to('cpu')
                
                self.model.eval()  # Set to evaluation mode
                
                # Also create pipeline for fallback
                self.pipeline = pipeline(
                    "text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=device
                )
                
                self._loaded = True
                print("Model loaded successfully!")
                
            except Exception as e:
                print(f"Error loading model directly: {e}")
                # Fallback to pipeline
                self.pipeline = pipeline(
                    "conversational",
                    model=self.model_name,
                    tokenizer=self.model_name,
                    device=device,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
                )
                self._loaded = True
                print("Model loaded via pipeline!")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Falling back to GPT-2...")
            # Fallback to GPT-2
            try:
                self.model_name = "gpt2"
                self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
                self.model = AutoModelForCausalLM.from_pretrained("gpt2")
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                self.model.eval()
                self.pipeline = pipeline(
                    "text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=-1
                )
                self._loaded = True
                print("GPT-2 loaded as fallback!")
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
        
        # Clean and validate message
        message = message.strip()
        if not message:
            return "Je n'ai pas compris votre message. Pouvez-vous reformuler?"
        
        try:
            # Method 1: Use direct model generation with better parameters (if model and tokenizer are loaded)
            if self.model is not None and self.tokenizer is not None:
                return self._generate_with_model(message, history)
            
            # Method 2: Use conversational pipeline
            if self.pipeline is not None:
                return self._generate_with_pipeline(message, history)
            
            raise RuntimeError("No model or pipeline available")
            
        except Exception as e:
            print(f"Error in generate_reply: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return a helpful fallback message
            return f"Je suis désolé, j'ai rencontré une erreur. Veuillez réessayer. ({str(e)[:50]})"
    
    def _generate_with_model(self, message: str, history: List[Dict[str, str]]) -> str:
        """Generate reply using direct model inference with better parameters"""
        import torch
        
        # Build conversation context
        chat_history_ids = None
        
        # Process history
        for msg in history[-5:]:  # Last 5 messages for context
            if msg.get("role") == "user":
                user_input = msg.get("content", "").strip()
                if user_input:
                    # Encode user input
                    new_user_input_ids = self.tokenizer.encode(
                        user_input + self.tokenizer.eos_token,
                        return_tensors='pt'
                    )
                    if chat_history_ids is None:
                        chat_history_ids = new_user_input_ids
                    else:
                        chat_history_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1)
            
            elif msg.get("role") == "assistant":
                bot_response = msg.get("content", "").strip()
                if bot_response:
                    # Encode bot response
                    bot_input_ids = self.tokenizer.encode(
                        bot_response + self.tokenizer.eos_token,
                        return_tensors='pt'
                    )
                    chat_history_ids = torch.cat([chat_history_ids, bot_input_ids], dim=-1)
        
        # Encode current user message
        new_user_input_ids = self.tokenizer.encode(
            message + self.tokenizer.eos_token,
            return_tensors='pt'
        )
        
        if chat_history_ids is not None:
            # Truncate history if too long (keep last 512 tokens)
            if chat_history_ids.shape[1] > 256:
                chat_history_ids = chat_history_ids[:, -256:]
            bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1)
        else:
            bot_input_ids = new_user_input_ids
        
        # Move to device
        device = next(self.model.parameters()).device
        bot_input_ids = bot_input_ids.to(device)
        
        # Generate response with better parameters
        with torch.no_grad():
            chat_history_ids = self.model.generate(
                bot_input_ids,
                max_length=bot_input_ids.shape[1] + 100,  # Generate up to 100 new tokens
                pad_token_id=self.tokenizer.eos_token_id,
                do_sample=True,
                top_p=0.95,
                top_k=50,
                temperature=0.8,
                no_repeat_ngram_size=3,
                repetition_penalty=1.2,
                length_penalty=1.0
            )
        
        # Decode only the new part
        new_tokens = chat_history_ids[:, bot_input_ids.shape[1]:]
        reply = self.tokenizer.decode(new_tokens[0], skip_special_tokens=True)
        
        # Clean up reply
        reply = reply.strip()
        
        # Validate reply
        if not reply or len(reply) < 2:
            # Fallback to simple response
            return self._generate_simple_fallback(message)
        
        # Remove repeated characters/words
        if self._is_repetitive(reply):
            return self._generate_simple_fallback(message)
        
        return reply
    
    def _generate_with_pipeline(self, message: str, history: List[Dict[str, str]]) -> str:
        """Generate reply using pipeline"""
        try:
            from transformers import Conversation
            
            conversation = Conversation()
            
            # Add history
            for msg in history[-5:]:  # Last 5 messages
                if msg.get("role") == "user":
                    conversation.add_user_input(msg.get("content", ""))
                elif msg.get("role") == "assistant":
                    conversation.append_response(msg.get("content", ""))
            
            # Add current message
            conversation.add_user_input(message)
            
            # Generate with better parameters
            result = self.pipeline(
                conversation,
                max_length=200,
                min_length=5,
                do_sample=True,
                top_p=0.95,
                top_k=50,
                temperature=0.8,
                repetition_penalty=1.2
            )
            
            # Extract reply
            if hasattr(result, 'generated_responses') and result.generated_responses:
                reply = result.generated_responses[-1]
            elif isinstance(result, Conversation):
                reply = result.generated_responses[-1] if result.generated_responses else None
            else:
                reply = str(result)
            
            if reply and reply.strip() and not self._is_repetitive(reply):
                return reply.strip()
            else:
                return self._generate_simple_fallback(message)
                
        except Exception as e:
            print(f"Pipeline generation error: {e}")
            return self._generate_simple_fallback(message)
    
    def _generate_simple_fallback(self, message: str) -> str:
        """Generate a simple fallback response"""
        # Simple rule-based responses for common inputs
        message_lower = message.lower().strip()
        
        if message_lower in ['cv', 'c.v.', 'curriculum vitae']:
            return "Je peux vous aider avec votre CV! Que souhaitez-vous savoir? Par exemple, je peux vous aider à rédiger une section ou à améliorer votre présentation."
        
        if message_lower in ['bonjour', 'salut', 'hello', 'hi']:
            return "Bonjour! Comment puis-je vous aider aujourd'hui?"
        
        if message_lower in ['merci', 'thanks', 'thank you']:
            return "De rien! N'hésitez pas si vous avez d'autres questions."
        
        # Generic response
        return f"Je comprends que vous dites '{message}'. Pouvez-vous me donner plus de détails ou reformuler votre question?"
    
    def _is_repetitive(self, text: str) -> bool:
        """Check if text is repetitive (like just commas or repeated words)"""
        if not text or len(text) < 2:
            return True
        
        # Check for too many repeated characters
        if len(set(text.replace(' ', ''))) < 3:
            return True
        
        # Check for repeated words
        words = text.split()
        if len(words) > 0:
            unique_words = set(words)
            if len(unique_words) < len(words) * 0.3:  # More than 70% repetition
                return True
        
        # Check for only punctuation
        if all(c in '.,!?;:' for c in text.replace(' ', '')):
            return True
        
        return False

