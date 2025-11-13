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
        
        # Check for common inputs first - use fallback immediately for better UX
        message_lower = message.lower().strip()
        if message_lower in ['cv', 'c.v.', 'curriculum vitae', 'cv?']:
            return "Je peux vous aider avec votre CV! Que souhaitez-vous savoir? Par exemple, je peux vous aider à rédiger une section ou à améliorer votre présentation."
        
        # Try model generation, but with strict validation
        # First, try direct model generation if available
        if self.model is not None and self.tokenizer is not None:
            try:
                reply = self._generate_with_model(message, history)
                # Validate reply - if valid, return it
                if reply and isinstance(reply, str) and reply.strip():
                    if self._is_valid_response(reply) and not self._is_repetitive(reply):
                        return reply
            except Exception as e:
                print(f"Error in _generate_with_model: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # If direct model failed or not available, try pipeline
        if self.pipeline is not None:
            try:
                reply = self._generate_with_pipeline(message, history)
                # Validate reply - if valid, return it
                if reply and isinstance(reply, str) and reply.strip():
                    if self._is_valid_response(reply) and not self._is_repetitive(reply):
                        return reply
            except Exception as e:
                print(f"Error in _generate_with_pipeline: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # If all attempts failed or returned invalid responses, use fallback
        # This ensures we always return a response
        return self._generate_simple_fallback(message)
    
    def _generate_with_model(self, message: str, history: List[Dict[str, str]]) -> str:
        """Generate reply using direct model inference with better parameters"""
        import torch
        
        try:
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
                        if chat_history_ids is not None:
                            chat_history_ids = torch.cat([chat_history_ids, bot_input_ids], dim=-1)
            
            # Encode current user message
            new_user_input_ids = self.tokenizer.encode(
                message + self.tokenizer.eos_token,
                return_tensors='pt'
            )
            
            if chat_history_ids is not None:
                # Truncate history if too long (keep last 256 tokens)
                if chat_history_ids.shape[1] > 256:
                    chat_history_ids = chat_history_ids[:, -256:]
                bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1)
            else:
                bot_input_ids = new_user_input_ids
            
            # Move to device
            device = next(self.model.parameters()).device
            bot_input_ids = bot_input_ids.to(device)
            
            # Generate response with better parameters - more conservative
            with torch.no_grad():
                chat_history_ids = self.model.generate(
                    bot_input_ids,
                    max_length=bot_input_ids.shape[1] + 50,  # Generate up to 50 new tokens (shorter)
                    pad_token_id=self.tokenizer.eos_token_id,
                    do_sample=True,
                    top_p=0.9,  # More conservative
                    top_k=30,  # More conservative
                    temperature=0.7,  # Lower temperature for more coherent responses
                    no_repeat_ngram_size=4,  # Prevent 4-gram repetition
                    repetition_penalty=1.5,  # Stronger penalty
                    length_penalty=1.2,  # Prefer shorter responses
                    early_stopping=True  # Stop early if EOS token
                )
            
            # Decode only the new part
            new_tokens = chat_history_ids[:, bot_input_ids.shape[1]:]
            reply = self.tokenizer.decode(new_tokens[0], skip_special_tokens=True)
            
            # Clean up reply
            if reply:
                reply = reply.strip()
            
            # Return reply (validation will be done in generate_reply)
            return reply if reply else ""
            
        except Exception as e:
            print(f"Error in _generate_with_model: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return empty string to trigger fallback
            return ""
    
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
            try:
                result = self.pipeline(
                    conversation,
                    max_length=150,
                    min_length=5,
                    do_sample=True,
                    top_p=0.9,
                    top_k=30,
                    temperature=0.7,
                    repetition_penalty=1.5
                )
            except TypeError:
                # If pipeline doesn't accept parameters, use default
                result = self.pipeline(conversation)
            
            # Extract reply
            if hasattr(result, 'generated_responses') and result.generated_responses:
                reply = result.generated_responses[-1]
            elif isinstance(result, Conversation):
                reply = result.generated_responses[-1] if result.generated_responses else None
            else:
                reply = str(result)
            
            # Return reply (validation will be done in generate_reply)
            if reply:
                return reply.strip()
            return ""
                
        except Exception as e:
            print(f"Pipeline generation error: {e}")
            import traceback
            traceback.print_exc()
            # Return empty string to trigger fallback
            return ""
    
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
    
    def _is_valid_response(self, text: str) -> bool:
        """Strict validation to check if response is coherent and valid"""
        if not text or len(text) < 2:
            return False
        
        # Remove extra whitespace
        text = text.strip()
        
        # Check length (too short or too long)
        if len(text) < 3 or len(text) > 500:
            return False
        
        # Check for excessive non-alphabetic characters (more than 30%)
        alphabetic_chars = sum(1 for c in text if c.isalpha() or c.isspace())
        if alphabetic_chars / len(text) < 0.5:  # Less than 50% alphabetic
            return False
        
        # Check for excessive repeated characters (like "aaaaa" or ",,,,,")
        if len(text) > 3:
            for i in range(len(text) - 3):
                if text[i] == text[i+1] == text[i+2] == text[i+3]:
                    # Allow some repetition but not excessive
                    if text.count(text[i]) > len(text) * 0.3:
                        return False
        
        # Check for too many special characters in a row
        special_char_count = 0
        max_special_in_row = 0
        for char in text:
            if not (char.isalnum() or char.isspace()):
                special_char_count += 1
                if special_char_count > max_special_in_row:
                    max_special_in_row = special_char_count
            else:
                special_char_count = 0
        
        if max_special_in_row > 5:  # More than 5 special chars in a row
            return False
        
        # Check for repetitive patterns (like "cv? cv? cv?")
        words = text.lower().split()
        if len(words) >= 3:
            # Check if same word appears more than 3 times in short text
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            for word, count in word_counts.items():
                if count > 3 and len(words) < 10:
                    return False
        
        # Check for random character sequences (like "xcvdc" or "vuv.ru")
        # Count sequences of consonants without vowels
        words = text.split()
        invalid_word_count = 0
        for word in words:
            # Remove punctuation
            clean_word = ''.join(c for c in word if c.isalnum())
            if len(clean_word) > 5:  # Only check longer words
                # Check if word has too many consonants in a row (likely random)
                vowels = 'aeiouyAEIOUY'
                consonant_streak = 0
                max_consonant_streak = 0
                for char in clean_word:
                    if char.isalpha() and char not in vowels:
                        consonant_streak += 1
                        if consonant_streak > max_consonant_streak:
                            max_consonant_streak = consonant_streak
                    else:
                        consonant_streak = 0
                
                # If more than 5 consonants in a row, likely invalid
                if max_consonant_streak > 5:
                    invalid_word_count += 1
        
        # If more than 40% of words are invalid, reject (more lenient)
        if len(words) > 0 and invalid_word_count / len(words) > 0.4:
            return False
        
        # Check for common French/English words (basic validation)
        # If text has at least some common words, it's more likely valid
        common_words = {
            'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles',
            'le', 'la', 'les', 'un', 'une', 'des',
            'et', 'ou', 'mais', 'donc', 'car', 'parce',
            'que', 'qui', 'quoi', 'comment', 'pourquoi', 'où',
            'bonjour', 'salut', 'merci', 'oui', 'non',
            'i', 'you', 'he', 'she', 'we', 'they',
            'the', 'a', 'an', 'and', 'or', 'but',
            'hello', 'hi', 'thanks', 'yes', 'no',
            'cv', 'curriculum', 'vitae', 'peux', 'peut', 'peuvent',
            'aide', 'aider', 'aide', 'savoir', 'sais', 'savez',
            'votre', 'votre', 'vos', 'mon', 'ma', 'mes',
            'avec', 'sans', 'pour', 'dans', 'sur', 'sous'
        }
        
        words_lower = [w.lower().strip('.,!?;:') for w in words]
        common_word_count = sum(1 for w in words_lower if w in common_words)
        
        # If no common words and text is long (more than 8 words), likely invalid
        # But be more lenient for short responses
        if len(words) > 8 and common_word_count == 0:
            return False
        
        # Final check: if it passed all checks, it's probably valid
        return True

