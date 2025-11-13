"""
Model wrapper for loading and using Hugging Face transformer models
Specialized in Pharmaceutical & Health (Pharma/MedTech) domain
"""
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from typing import List, Dict, Optional


class ChatModel:
    """
    Singleton wrapper for Hugging Face conversational model
    Specialized in Pharmaceutical & Health (Pharma/MedTech) domain
    Uses DialoGPT-small or conversational pipeline with domain-specific context
    """
    
    # Domain-specific system context
    DOMAIN = "Pharmaceutique & Santé (Pharma/MedTech)"
    SYSTEM_CONTEXT = "Tu es un assistant spécialisé dans le domaine pharmaceutique et de la santé (Pharma/MedTech). Tu aides les utilisateurs avec des questions sur les médicaments, les dispositifs médicaux, la recherche pharmaceutique, la réglementation, les essais cliniques, et les innovations en santé."
    
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
            return "Je n'ai pas compris votre message. Pouvez-vous reformuler votre question concernant le domaine pharmaceutique et de la santé (Pharma/MedTech)?"
        
        message_lower = message.lower().strip()
        
        # Check for domain-specific inputs first - use specialized fallback immediately
        domain_reply = self._get_domain_specific_response(message_lower)
        if domain_reply:
            return domain_reply
        
        # Try model generation - be more permissive for pharma questions
        # First, try direct model generation if available
        if self.model is not None and self.tokenizer is not None:
            try:
                reply = self._generate_with_model(message, history)
                # Validate reply - be more permissive for pharma questions
                if reply and isinstance(reply, str) and reply.strip():
                    if self._is_valid_response(reply) and not self._is_repetitive(reply):
                        # If question is pharma-related, accept reply even if it doesn't have explicit keywords
                        # Only reject if reply is clearly off-topic
                        if is_pharma_question:
                            # For pharma questions, accept if not clearly off-topic
                            if not self._is_clearly_off_topic(reply):
                                return reply
                        else:
                            # For non-pharma questions, check domain relation
                            if self._is_domain_related(reply):
                                return reply
            except Exception as e:
                print(f"Error in _generate_with_model: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # If direct model failed or not available, try pipeline
        if self.pipeline is not None:
            try:
                reply = self._generate_with_pipeline(message, history)
                # Validate reply - be more permissive for pharma questions
                if reply and isinstance(reply, str) and reply.strip():
                    if self._is_valid_response(reply) and not self._is_repetitive(reply):
                        # If question is pharma-related, accept reply even if it doesn't have explicit keywords
                        if is_pharma_question:
                            if not self._is_clearly_off_topic(reply):
                                return reply
                        else:
                            if self._is_domain_related(reply):
                                return reply
            except Exception as e:
                print(f"Error in _generate_with_pipeline: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # If all attempts failed, use intelligent domain-specific fallback
        return self._generate_intelligent_fallback(message, is_pharma_question)
    
    def _generate_with_model(self, message: str, history: List[Dict[str, str]]) -> str:
        """Generate reply using direct model inference with domain-specific context"""
        import torch
        
        try:
            # Build conversation context with domain context
            chat_history_ids = None
            
            # Add domain context at the beginning if no history
            if not history:
                context_prompt = f"{self.SYSTEM_CONTEXT} Question: "
                context_ids = self.tokenizer.encode(
                    context_prompt,
                    return_tensors='pt',
                    max_length=50,
                    truncation=True
                )
                chat_history_ids = context_ids
            
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
            
            # Encode current user message with domain context
            contextual_message = f"Question Pharma/MedTech: {message}"
            new_user_input_ids = self.tokenizer.encode(
                contextual_message + self.tokenizer.eos_token,
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
            
            # Generate response with better parameters to avoid repetition
            with torch.no_grad():
                chat_history_ids = self.model.generate(
                    bot_input_ids,
                    max_length=bot_input_ids.shape[1] + 80,  # Generate up to 80 new tokens
                    pad_token_id=self.tokenizer.eos_token_id,
                    do_sample=True,
                    top_p=0.92,  # Slightly more diverse
                    top_k=40,  # More diverse
                    temperature=0.75,  # Balanced temperature
                    no_repeat_ngram_size=5,  # Prevent 5-gram repetition (stronger)
                    repetition_penalty=1.8,  # Much stronger penalty against repetition
                    length_penalty=1.1,  # Slightly prefer longer, more complete responses
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
    
    def _is_pharma_question(self, message_lower: str) -> bool:
        """Check if question is clearly pharmaceutique/medical"""
        pharma_keywords = [
            # Medications
            'médicament', 'medicament', 'drug', 'molecule', 'principe actif', 'posologie', 'dosage',
            'antibiotique', 'antibiotic', 'amoxicilline', 'amoxicillin', 'paracétamol', 'paracetamol',
            'aspirine', 'aspirin', 'ibuprofène', 'ibuprofen', 'médicament', 'pillule', 'comprimé',
            # Medical terms
            'effet secondaire', 'side effect', 'effet indésirable', 'adverse', 'contre-indication',
            'indication', 'contraindication', 'interaction', 'pharmacocinétique', 'pharmacodynamie',
            'posologie', 'dosage', 'administration', 'voie d\'administration',
            # Medical devices
            'dispositif médical', 'dispositif medical', 'medical device', 'medtech',
            # Clinical
            'essai clinique', 'clinical trial', 'étude clinique', 'phase', 'rct',
            # Regulation
            'réglementation', 'regulation', 'fda', 'ema', 'ansm', 'amm', 'autorisation',
            # Research
            'recherche', 'research', 'développement', 'development', 'r&d',
            # Safety
            'pharmacovigilance', 'sécurité', 'safety', 'surveillance', 'toxicité',
            # Biotech
            'biotechnologie', 'biotechnology', 'biotech', 'biologique', 'biologic',
            # General health/pharma
            'santé', 'health', 'médical', 'medical', 'thérapeutique', 'therapeutic', 'thérapie'
        ]
        return any(keyword in message_lower for keyword in pharma_keywords)
    
    def _get_domain_specific_response(self, message_lower: str) -> Optional[str]:
        """Get domain-specific response ONLY for greetings or very general questions"""
        
        # Greetings - return immediately
        if message_lower in ['bonjour', 'salut', 'hello', 'hi', 'bonsoir', 'bonne journée']:
            return "Bonjour! Je suis un assistant spécialisé dans le domaine pharmaceutique et de la santé (Pharma/MedTech). Je peux vous aider avec des questions sur les médicaments, les dispositifs médicaux, la recherche pharmaceutique, la réglementation, les essais cliniques, et les innovations en santé. Comment puis-je vous aider aujourd'hui?"
        
        # Very general questions about medications (without specific drug names)
        if any(word in message_lower for word in ['médicament', 'medicament', 'drug']) and not any(word in message_lower for word in ['quel', 'quels', 'quelle', 'quelles', 'comment', 'pourquoi', 'qu\'est', 'what', 'how', 'why']):
            return "Je peux vous aider avec des questions sur les médicaments! Voici ce que je peux faire :\n• Expliquer les principes actifs et mécanismes d'action\n• Discuter de la posologie et des dosages\n• Informer sur les interactions médicamenteuses\n• Parler de la pharmacocinétique et pharmacodynamie\n\nQuelle question avez-vous sur les médicaments?"
        
        # Medical devices
        if any(word in message_lower for word in ['dispositif médical', 'dispositif medical', 'medical device', 'medtech', 'équipement médical']):
            return "Je peux vous aider avec des questions sur les dispositifs médicaux (MedTech)! Voici ce que je peux faire :\n• Expliquer les types de dispositifs médicaux\n• Discuter de la réglementation (CE marking, FDA)\n• Parler des innovations en dispositifs médicaux\n• Informer sur les classes de dispositifs (I, IIa, IIb, III)\n\nQuelle question avez-vous sur les dispositifs médicaux?"
        
        # Clinical trials
        if any(word in message_lower for word in ['essai clinique', 'clinical trial', 'étude clinique', 'phase', 'rct', 'randomized']):
            return "Je peux vous aider avec des questions sur les essais cliniques! Voici ce que je peux faire :\n• Expliquer les phases des essais cliniques (I, II, III, IV)\n• Discuter de la méthodologie (randomisation, double aveugle)\n• Parler de la réglementation (ICH-GCP, FDA, EMA)\n• Informer sur les endpoints et critères d'évaluation\n\nQuelle question avez-vous sur les essais cliniques?"
        
        # Regulation
        if any(word in message_lower for word in ['réglementation', 'regulation', 'fda', 'ema', 'ansm', 'autorisation', 'mise sur le marché', 'amm']):
            return "Je peux vous aider avec des questions sur la réglementation pharmaceutique! Voici ce que je peux faire :\n• Expliquer les processus d'autorisation de mise sur le marché (AMM)\n• Discuter des agences réglementaires (FDA, EMA, ANSM)\n• Parler des exigences réglementaires pour les médicaments et dispositifs\n• Informer sur les procédures d'enregistrement\n\nQuelle question avez-vous sur la réglementation?"
        
        # Research & Development
        if any(word in message_lower for word in ['recherche', 'research', 'développement', 'development', 'r&d', 'rd', 'innovation', 'découverte']):
            return "Je peux vous aider avec des questions sur la recherche et développement pharmaceutique! Voici ce que je peux faire :\n• Expliquer les étapes du développement de médicaments\n• Discuter de la découverte de molécules\n• Parler des technologies innovantes (biotechnologie, thérapies géniques)\n• Informer sur les partenariats et collaborations\n\nQuelle question avez-vous sur la R&D pharmaceutique?"
        
        # Pharmacovigilance
        if any(word in message_lower for word in ['pharmacovigilance', 'effet indésirable', 'side effect', 'sécurité', 'safety', 'surveillance']):
            return "Je peux vous aider avec des questions sur la pharmacovigilance! Voici ce que je peux faire :\n• Expliquer les systèmes de surveillance post-commercialisation\n• Discuter de la gestion des effets indésirables\n• Parler des obligations réglementaires de pharmacovigilance\n• Informer sur les signalements et rapports\n\nQuelle question avez-vous sur la pharmacovigilance?"
        
        # Biotechnology
        if any(word in message_lower for word in ['biotechnologie', 'biotechnology', 'biotech', 'thérapie génique', 'gene therapy', 'biologique', 'biologic']):
            return "Je peux vous aider avec des questions sur la biotechnologie pharmaceutique! Voici ce que je peux faire :\n• Expliquer les médicaments biologiques et biosimilaires\n• Discuter des thérapies géniques et cellulaires\n• Parler des technologies de production biotechnologique\n• Informer sur les innovations en biotech\n\nQuelle question avez-vous sur la biotechnologie?"
        
        # Thanks
        if any(word in message_lower for word in ['merci', 'thanks', 'thank you', 'remerciement']):
            return "De rien! N'hésitez pas si vous avez d'autres questions sur le domaine pharmaceutique et de la santé (Pharma/MedTech)."
        
        return None
    
    def _is_clearly_off_topic(self, text: str) -> bool:
        """Check if text is clearly off-topic (not pharma/medical)"""
        if not text or len(text) < 3:
            return False
        
        text_lower = text.lower()
        # Off-topic keywords that would indicate the response is not pharma-related
        off_topic_keywords = [
            'cuisine', 'cooking', 'recette', 'recipe', 'restaurant',
            'sport', 'football', 'basketball', 'tennis',
            'musique', 'music', 'film', 'movie', 'cinéma',
            'voyage', 'travel', 'vacances', 'vacation',
            'cv', 'curriculum', 'lettre de motivation', 'cover letter',
            'informatique', 'computer', 'programmation', 'programming',
            'voiture', 'car', 'automobile'
        ]
        
        # If response contains off-topic keywords and no pharma keywords, it's off-topic
        has_off_topic = any(keyword in text_lower for keyword in off_topic_keywords)
        has_pharma = self._is_domain_related(text)
        
        return has_off_topic and not has_pharma
    
    def _generate_intelligent_fallback(self, message: str, is_pharma: bool) -> str:
        """Generate intelligent fallback that doesn't repeat"""
        message_lower = message.lower().strip()
        
        # If it's a pharma question but model failed, provide helpful context
        if is_pharma:
            # Extract key terms from the question
            if 'effet' in message_lower or 'side effect' in message_lower:
                return "Les effets secondaires des médicaments varient selon le principe actif. Pour l'Amoxicilline, les effets secondaires les plus fréquents incluent : diarrhée, nausées, éruptions cutanées, et dans de rares cas, réactions allergiques. Pour des informations précises sur un médicament spécifique, je recommande de consulter la notice du médicament ou un professionnel de santé."
            
            if any(word in message_lower for word in ['amoxicilline', 'amoxicillin', 'antibiotique', 'antibiotic']):
                return "L'Amoxicilline est un antibiotique de la famille des pénicillines, utilisé pour traiter diverses infections bactériennes. Les effets secondaires courants peuvent inclure des troubles digestifs (nausées, diarrhée) et des réactions cutanées. La posologie dépend de l'infection traitée et doit être déterminée par un professionnel de santé."
            
            if 'posologie' in message_lower or 'dosage' in message_lower:
                return "La posologie d'un médicament dépend de plusieurs facteurs : le type d'infection, l'âge du patient, la fonction rénale, et d'autres conditions médicales. Pour des informations précises sur la posologie, consultez la notice du médicament ou un professionnel de santé."
            
            # Generic pharma fallback
            return f"Je comprends votre question sur '{message}'. Dans le domaine pharmaceutique, les réponses peuvent varier selon le contexte spécifique. Pourriez-vous préciser :\n• Le médicament ou dispositif concerné\n• Le contexte d'utilisation\n• L'information recherchée (effets, posologie, interactions, etc.)"
        
        # Not pharma question
        return "Je suis spécialisé uniquement dans le domaine pharmaceutique et de la santé (Pharma/MedTech). Je peux vous aider avec des questions sur les médicaments, les dispositifs médicaux, les essais cliniques, la réglementation, et la recherche pharmaceutique. Comment puis-je vous aider dans ce domaine?"
    
    def _is_domain_related(self, text: str) -> bool:
        """Check if text is related to Pharma/MedTech domain"""
        if not text or len(text) < 3:
            return False
        
        text_lower = text.lower()
        domain_keywords = [
            'médicament', 'medicament', 'drug', 'pharma', 'pharmaceutique', 'pharmaceutical',
            'dispositif médical', 'dispositif medical', 'medical device', 'medtech',
            'essai clinique', 'clinical trial', 'étude clinique', 'phase',
            'réglementation', 'regulation', 'fda', 'ema', 'ansm', 'amm',
            'recherche', 'research', 'développement', 'development', 'r&d', 'rd',
            'pharmacovigilance', 'effet indésirable', 'side effect', 'adverse',
            'biotechnologie', 'biotechnology', 'biotech', 'thérapie génique', 'gene therapy',
            'santé', 'health', 'médical', 'medical', 'thérapeutique', 'therapeutic',
            'molecule', 'principe actif', 'posologie', 'dosage', 'pharmacocinétique',
            'biosimilaire', 'biosimilar', 'biologique', 'biologic', 'innovation'
        ]
        
        # Check if at least one domain keyword is present
        return any(keyword in text_lower for keyword in domain_keywords)
    
    def _is_repetitive(self, text: str) -> bool:
        """Check if text is repetitive (like just commas or repeated words)"""
        if not text or len(text) < 2:
            return True
        
        # Check for too many repeated characters
        if len(set(text.replace(' ', ''))) < 3:
            return True
        
        # Check for repeated words (more strict)
        words = text.split()
        if len(words) > 0:
            unique_words = set(words)
            # If less than 40% unique words, it's repetitive
            if len(unique_words) < len(words) * 0.4:
                return True
            
            # Check for same word repeated more than 3 times in short text
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            for word, count in word_counts.items():
                if count > 3 and len(words) < 15:
                    return True
        
        # Check for only punctuation
        if all(c in '.,!?;:' for c in text.replace(' ', '')):
            return True
        
        # Check for repeated phrases (3+ words repeated)
        if len(words) >= 6:
            for i in range(len(words) - 2):
                phrase = ' '.join(words[i:i+3])
                if text.count(phrase) > 1:
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

