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


def generate_reply(pipeline_obj, message, history):
    """Generate a reply using the model with improved parameters"""
    try:
        from transformers import Conversation
        import torch
        
        # Clean message
        message = message.strip()
        if not message:
            return "Je n'ai pas compris votre message. Pouvez-vous reformuler?"
        
        # Simple fallback for common inputs
        message_lower = message.lower()
        if message_lower in ['cv', 'c.v.', 'curriculum vitae']:
            return "Je peux vous aider avec votre CV! Que souhaitez-vous savoir? Par exemple, je peux vous aider à rédiger une section ou à améliorer votre présentation."
        
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
                max_length=200,
                min_length=5,
                do_sample=True,
                top_p=0.95,
                top_k=50,
                temperature=0.8,
                repetition_penalty=1.2
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
            # Check if reply is repetitive
            if _is_repetitive(reply):
                return _generate_fallback(message)
            return reply
        else:
            return _generate_fallback(message)
            
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

def _generate_fallback(message: str) -> str:
    """Generate a fallback response"""
    message_lower = message.lower().strip()
    
    if message_lower in ['cv', 'c.v.', 'curriculum vitae']:
        return "Je peux vous aider avec votre CV! Que souhaitez-vous savoir?"
    
    if message_lower in ['bonjour', 'salut', 'hello', 'hi']:
        return "Bonjour! Comment puis-je vous aider aujourd'hui?"
    
    if message_lower in ['merci', 'thanks', 'thank you']:
        return "De rien! N'hésitez pas si vous avez d'autres questions."
    
    return f"Je comprends que vous dites '{message}'. Pouvez-vous me donner plus de détails ou reformuler votre question?"


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
        st.info("👋 Bonjour! Je suis votre assistant IA. Posez-moi une question!")
    
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

