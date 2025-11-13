"""
Streamlit app for AI Chat Webapp
Single-file application deployable on Streamlit Cloud
"""
import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="AI Chat",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main .block-container {
        padding-top: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
    }
    .user-message {
        background-color: #667eea;
        color: white;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: white;
        color: #333;
        margin-right: 20%;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_model():
    """Load the AI model (cached for performance)"""
    model_name = "microsoft/DialoGPT-small"
    
    try:
        st.info(f"🔄 Chargement du modèle {model_name}...")
        pipeline_obj = pipeline(
            "conversational",
            model=model_name,
            tokenizer=model_name,
            device=-1,  # CPU
            torch_dtype=torch.float32
        )
        st.success("✅ Modèle chargé avec succès!")
        return pipeline_obj, model_name
    except Exception as e:
        st.warning(f"⚠️ Erreur lors du chargement du modèle: {e}")
        st.info("Tentative avec un modèle alternatif...")
        try:
            pipeline_obj = pipeline(
                "text-generation",
                model="gpt2",
                device=-1
            )
            return pipeline_obj, "gpt2"
        except Exception as e2:
            st.error(f"❌ Impossible de charger un modèle: {e2}")
            return None, None


def get_domain_specific_response(message_lower: str):
    """Get domain-specific response for common CV/cover letter questions"""
    # Greetings
    if message_lower in ['bonjour', 'salut', 'hello', 'hi', 'bonsoir', 'bonne journée']:
        return "Bonjour! Je suis spécialisé dans l'aide à la rédaction de CV et de lettres de motivation. Comment puis-je vous aider aujourd'hui?"
    
    # CV-related keywords
    if any(word in message_lower for word in ['cv', 'c.v.', 'curriculum vitae', 'curriculum', 'résumé']):
        if any(word in message_lower for word in ['comment', 'aide', 'aider', 'améliorer', 'rédiger', 'écrire']):
            return "Je peux vous aider avec votre CV! Voici ce que je peux faire :\n• Rédiger ou améliorer des sections de votre CV\n• Formuler vos compétences et expériences professionnelles\n• Conseiller sur la structure et la mise en forme\n• Adapter votre CV à un poste spécifique\n\nQuelle section souhaitez-vous travailler?"
        return "Je peux vous aider avec votre CV! Que souhaitez-vous savoir? Par exemple, je peux vous aider à rédiger une section, formuler vos compétences, ou améliorer votre présentation."
    
    # Cover letter keywords
    if any(word in message_lower for word in ['lettre', 'motivation', 'cover letter', 'candidature', 'lettre de motivation']):
        return "Je peux vous aider à rédiger votre lettre de motivation! Voici ce que je peux faire :\n• Structurer votre lettre\n• Rédiger des paragraphes adaptés au poste\n• Mettre en valeur vos compétences\n• Adapter le ton et le style\n\nPour quel poste souhaitez-vous écrire votre lettre?"
    
    # Skills/competences
    if any(word in message_lower for word in ['compétence', 'competence', 'skill', 'savoir-faire', 'aptitude']):
        return "Pour formuler vos compétences sur votre CV, je recommande :\n• Utiliser des verbes d'action (gérer, développer, optimiser...)\n• Être spécifique et quantifier quand possible\n• Adapter aux mots-clés du poste visé\n\nQuelles compétences souhaitez-vous mettre en avant?"
    
    # Experience
    if any(word in message_lower for word in ['expérience', 'experience', 'emploi', 'travail', 'poste', 'carrière']):
        return "Pour décrire vos expériences professionnelles, je recommande :\n• Utiliser la structure : Action + Résultat + Contexte\n• Quantifier vos réalisations (ex: 'augmenté les ventes de 20%')\n• Mettre en avant les résultats concrets\n\nQuelle expérience souhaitez-vous décrire?"
    
    # Structure/format
    if any(word in message_lower for word in ['structure', 'format', 'mise en forme', 'organisation', 'modèle', 'template']):
        return "Structure recommandée pour un CV :\n1. En-tête (nom, coordonnées)\n2. Profil/Objectif (optionnel, 2-3 lignes)\n3. Expériences professionnelles (du plus récent au plus ancien)\n4. Formations\n5. Compétences\n6. Langues/Certifications (optionnel)\n\nQuelle section souhaitez-vous travailler?"
    
    # Thanks
    if any(word in message_lower for word in ['merci', 'thanks', 'thank you', 'remerciement']):
        return "De rien! N'hésitez pas si vous avez d'autres questions sur votre CV ou votre lettre de motivation."
    
    return None

def is_domain_related(text: str) -> bool:
    """Check if text is related to CV/cover letter domain"""
    if not text or len(text) < 3:
        return False
    
    text_lower = text.lower()
    domain_keywords = [
        'cv', 'curriculum', 'vitae', 'résumé',
        'lettre', 'motivation', 'candidature',
        'compétence', 'competence', 'skill',
        'expérience', 'experience', 'emploi', 'travail', 'poste',
        'formation', 'diplôme', 'carrière',
        'aide', 'aider', 'rédiger', 'améliorer', 'conseil'
    ]
    
    return any(keyword in text_lower for keyword in domain_keywords)

def generate_domain_fallback(message: str) -> str:
    """Generate a domain-specific fallback response"""
    message_lower = message.lower().strip()
    
    domain_keywords = ['cv', 'lettre', 'motivation', 'compétence', 'expérience', 'emploi', 'candidature', 'poste', 'travail', 'formation', 'diplôme', 'carrière']
    if any(keyword in message_lower for keyword in domain_keywords):
        return f"Je comprends que vous parlez de '{message}'. Pour mieux vous aider avec votre CV ou votre lettre de motivation, pouvez-vous être plus précis? Par exemple :\n• Quelle section de votre CV souhaitez-vous améliorer?\n• Pour quel poste écrivez-vous votre lettre?\n• Quelles compétences voulez-vous mettre en avant?"
    
    return "Je suis spécialisé dans l'aide à la rédaction de CV et de lettres de motivation. Je peux vous aider à :\n• Rédiger ou améliorer votre CV\n• Écrire une lettre de motivation\n• Formuler vos compétences et expériences\n• Adapter votre candidature à un poste\n\nComment puis-je vous aider dans ce domaine?"

def generate_reply(pipeline_obj, message, history):
    """Generate a reply using the model with domain-specific validation"""
    try:
        from transformers import Conversation
        import torch
        
        # Clean message
        message = message.strip()
        if not message:
            return "Je n'ai pas compris votre message. Pouvez-vous reformuler votre question concernant votre CV ou votre lettre de motivation?"
        
        message_lower = message.lower().strip()
        
        # Check for domain-specific inputs first
        domain_reply = get_domain_specific_response(message_lower)
        if domain_reply:
            return domain_reply
        
        # Try generation with validation (max 2 attempts)
        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                conversation = Conversation()
                
                # Add history (last 5 messages)
                for msg in history[-5:]:
                    if msg.get("role") == "user":
                        conversation.add_user_input(msg.get("content", ""))
                    elif msg.get("role") == "assistant":
                        conversation.append_response(msg.get("content", ""))
                
                # Add current message
                conversation.add_user_input(message)
                
                # Generate reply with better parameters
                try:
                    result = pipeline_obj(
                        conversation,
                        max_length=150,  # Shorter responses
                        min_length=5,
                        do_sample=True,
                        top_p=0.9,  # More conservative
                        top_k=30,  # More conservative
                        temperature=0.7,  # Lower temperature
                        repetition_penalty=1.5  # Stronger penalty
                    )
                except TypeError:
                    # If pipeline doesn't accept parameters, use default
                    result = pipeline_obj(conversation)
                
                # Extract reply
                if hasattr(result, 'generated_responses') and result.generated_responses:
                    reply = result.generated_responses[-1]
                elif isinstance(result, Conversation):
                    reply = result.generated_responses[-1] if result.generated_responses else None
                else:
                    reply = str(result)
                
                if reply:
                    reply = reply.strip()
                    # Strict validation - if valid and domain-related, return it
                    if not _is_repetitive(reply) and _is_valid_response(reply):
                        if is_domain_related(reply):
                            return reply
                    # If invalid and not last attempt, try again
                    if attempt < max_attempts - 1:
                        continue
                else:
                    # If no reply and not last attempt, try again
                    if attempt < max_attempts - 1:
                        continue
                    
            except Exception as e:
                print(f"Error in generate_reply (attempt {attempt + 1}): {e}")
                if attempt == max_attempts - 1:
                    import traceback
                    traceback.print_exc()
        
        # If all attempts failed or returned invalid responses, use domain fallback
        return generate_domain_fallback(message)
            
    except Exception as e:
        print(f"Error in generate_reply: {e}")
        import traceback
        traceback.print_exc()
        return _generate_fallback(message)

def _is_repetitive(text: str) -> bool:
    """Check if text is repetitive"""
    if not text or len(text) < 2:
        return True
    
    # Check for too many repeated characters
    if len(set(text.replace(' ', ''))) < 3:
        return True
    
    # Check for repeated words
    words = text.split()
    if len(words) > 0:
        unique_words = set(words)
        if len(unique_words) < len(words) * 0.3:
            return True
    
    # Check for only punctuation
    if all(c in '.,!?;:' for c in text.replace(' ', '')):
        return True
    
    return False

def _is_valid_response(text: str) -> bool:
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
        if len(clean_word) > 4:
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
            
            # If more than 4 consonants in a row, likely invalid
            if max_consonant_streak > 4:
                invalid_word_count += 1
    
    # If more than 30% of words are invalid, reject
    if len(words) > 0 and invalid_word_count / len(words) > 0.3:
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
        'cv', 'curriculum', 'vitae'
    }
    
    words_lower = [w.lower().strip('.,!?;:') for w in words]
    common_word_count = sum(1 for w in words_lower if w in common_words)
    
    # If no common words and text is long, likely invalid
    if len(words) > 5 and common_word_count == 0:
        return False
    
    # Final check: if it passed all checks, it's probably valid
    return True

# _generate_fallback is now replaced by generate_domain_fallback


def download_conversation(history):
    """Download conversation as JSON"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{timestamp}.json"
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "messages": history
    }
    
    return json.dumps(data, ensure_ascii=False, indent=2)


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "model_loaded" not in st.session_state:
    st.session_state.model_loaded = False

if "pipeline" not in st.session_state:
    st.session_state.pipeline = None

if "model_name" not in st.session_state:
    st.session_state.model_name = None

# Load model
if not st.session_state.model_loaded:
    with st.spinner("Chargement du modèle IA..."):
        pipeline_obj, model_name = load_model()
        if pipeline_obj:
            st.session_state.pipeline = pipeline_obj
            st.session_state.model_name = model_name
            st.session_state.model_loaded = True
        else:
            st.error("Impossible de charger le modèle. Veuillez réessayer plus tard.")
            st.stop()

# Main UI
st.title("💬 AI Chat")
st.markdown("---")

# Sidebar for controls
with st.sidebar:
    st.header("Contrôles")
    
    if st.button("🗑️ Effacer la conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    if st.session_state.messages:
        st.markdown("---")
        st.subheader("Exporter")
        
        conversation_json = download_conversation(st.session_state.messages)
        st.download_button(
            label="📥 Télécharger la conversation",
            data=conversation_json,
            file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    st.markdown("---")
    st.info(f"**Modèle:** {st.session_state.model_name}")

# Display messages
chat_container = st.container()

with chat_container:
    if not st.session_state.messages:
        st.info("👋 Bonjour! Je suis votre assistant spécialisé dans la rédaction de CV et de lettres de motivation. Comment puis-je vous aider aujourd'hui?")
    
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        
        if role == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>Vous:</strong> {content}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>Assistant:</strong> {content}
            </div>
            """, unsafe_allow_html=True)

# Input area
st.markdown("---")

user_input = st.text_area(
    "Votre message",
    height=100,
    placeholder="Tapez votre message ici...",
    key="user_input"
)

col1, col2 = st.columns([1, 6])

with col1:
    send_button = st.button("📤 Envoyer", use_container_width=True, type="primary")

if send_button and user_input.strip():
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input.strip(),
        "timestamp": datetime.now().isoformat()
    })
    
    # Generate reply
    with st.spinner("🤔 Réflexion en cours..."):
        reply = generate_reply(
            st.session_state.pipeline,
            user_input.strip(),
            st.session_state.messages[:-1]  # Exclude the just-added user message
        )
    
    # Add assistant reply
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply,
        "timestamp": datetime.now().isoformat()
    })
    
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: white; padding: 1rem;'>"
    "AI Chat Webapp - Powered by Hugging Face Transformers"
    "</div>",
    unsafe_allow_html=True
)

