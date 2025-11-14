"""
API-based model wrapper for OpenAI GPT or Google Gemini
Provides reliable responses using cloud APIs
"""
import os
from typing import List, Dict, Optional
import requests


class APIChatModel:
    """
    API-based chat model using OpenAI GPT or Google Gemini
    Specialized in Pharmaceutical & Health (Pharma/MedTech) domain
    """
    
    DOMAIN = "Pharmaceutique & Santé (Pharma/MedTech)"
    SYSTEM_CONTEXT = """Tu es un assistant spécialisé dans le domaine pharmaceutique et de la santé (Pharma/MedTech). 
Tu aides les utilisateurs avec des questions sur les médicaments, les dispositifs médicaux, la recherche pharmaceutique, 
la réglementation, les essais cliniques, et les innovations en santé. 
Tu dois TOUJOURS répondre en français et être précis et professionnel."""
    
    def __init__(self):
        self.api_type = os.getenv("API_TYPE", "openai")  # "openai" or "gemini"
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")  # or "gpt-4"
        self._loaded = True  # API is always "loaded"
    
    def is_loaded(self) -> bool:
        """Check if API is configured"""
        if self.api_type == "openai":
            return bool(self.openai_api_key)
        elif self.api_type == "gemini":
            return bool(self.gemini_api_key)
        return False
    
    def generate_reply(self, message: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Generate a reply using API (OpenAI or Gemini)
        """
        if history is None:
            history = []
        
        message = message.strip()
        if not message:
            return "Je n'ai pas compris votre message. Pouvez-vous reformuler votre question concernant le domaine pharmaceutique et de la santé (Pharma/MedTech)?"
        
        # Check if question is pharma-related
        message_lower = message.lower()
        is_pharma = self._is_pharma_question(message_lower)
        
        if not is_pharma:
            return "Je suis spécialisé uniquement dans le domaine pharmaceutique et de la santé (Pharma/MedTech). Je peux vous aider avec des questions sur les médicaments, les dispositifs médicaux, les essais cliniques, la réglementation, et la recherche pharmaceutique. Comment puis-je vous aider dans ce domaine?"
        
        try:
            if self.api_type == "openai":
                return self._generate_with_openai(message, history)
            elif self.api_type == "gemini":
                return self._generate_with_gemini(message, history)
            else:
                return "Configuration API incorrecte. Veuillez configurer OPENAI_API_KEY ou GEMINI_API_KEY."
        except Exception as e:
            print(f"Error generating reply with API: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"Désolé, une erreur s'est produite lors de la génération de la réponse. Veuillez réessayer."
    
    def _generate_with_openai(self, message: str, history: List[Dict[str, str]]) -> str:
        """Generate reply using OpenAI API"""
        import openai
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not configured")
        
        openai.api_key = self.openai_api_key
        
        # Build messages for OpenAI
        messages = [
            {"role": "system", "content": self.SYSTEM_CONTEXT}
        ]
        
        # Add history (last 10 messages to stay within token limits)
        for msg in history[-10:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ["user", "assistant"] and content:
                messages.append({"role": role, "content": content})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        try:
            if use_new_api:
                # New OpenAI client (v1.0+)
                client = OpenAI(api_key=self.openai_api_key)
                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500,
                    top_p=0.9
                )
                reply = response.choices[0].message.content.strip()
            else:
                # Old OpenAI API
                response = openai.ChatCompletion.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500,
                    top_p=0.9
                )
                reply = response.choices[0].message.content.strip()
            
            return reply if reply else "Désolé, je n'ai pas pu générer de réponse."
            
        except Exception as e:
            print(f"OpenAI API error: {str(e)}")
            raise
    
    def _generate_with_gemini(self, message: str, history: List[Dict[str, str]]) -> str:
        """Generate reply using Google Gemini API"""
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        
        # Build prompt with context
        prompt = f"{self.SYSTEM_CONTEXT}\n\n"
        
        # Add history
        for msg in history[-5:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if content:
                if role == "user":
                    prompt += f"Utilisateur: {content}\n"
                elif role == "assistant":
                    prompt += f"Assistant: {content}\n"
        
        # Add current message
        prompt += f"Utilisateur: {message}\nAssistant:"
        
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.gemini_api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 500,
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if "candidates" in data and len(data["candidates"]) > 0:
                reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return reply if reply else "Désolé, je n'ai pas pu générer de réponse."
            else:
                raise ValueError("No response from Gemini API")
                
        except Exception as e:
            print(f"Gemini API error: {str(e)}")
            raise
    
    def _is_pharma_question(self, message_lower: str) -> bool:
        """Check if question is pharmaceutique/medical"""
        pharma_keywords = [
            'médicament', 'medicament', 'drug', 'molecule', 'principe actif', 'posologie', 'dosage',
            'antibiotique', 'antibiotic', 'amoxicilline', 'amoxicillin', 'paracétamol', 'paracetamol',
            'aspirine', 'aspirin', 'ibuprofène', 'ibuprofen', 'pillule', 'comprimé', 'gélule',
            'pénicilline', 'penicillin', 'effet secondaire', 'side effect', 'effet indésirable',
            'dispositif médical', 'dispositif medical', 'medical device', 'medtech',
            'essai clinique', 'clinical trial', 'étude clinique', 'phase',
            'réglementation', 'regulation', 'fda', 'ema', 'ansm', 'amm',
            'recherche', 'research', 'développement', 'development', 'r&d',
            'pharmacovigilance', 'sécurité', 'safety', 'surveillance',
            'biotechnologie', 'biotechnology', 'biotech', 'biologique', 'biologic',
            'santé', 'health', 'médical', 'medical', 'thérapeutique', 'therapeutic', 'thérapie',
            'fonctionne', 'fonctionnement', 'comment', 'how', 'mécanisme', 'mechanism', 'action'
        ]
        return any(keyword in message_lower for keyword in pharma_keywords)

