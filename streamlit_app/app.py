"""
Streamlit app for AI Chat Webapp
Single-file application deployable on Streamlit Cloud
"""
import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from datetime import datetime
import json
import os

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


def check_api_available():
    """Check if API is configured"""
    openai_key = os.getenv("OPENAI_API_KEY", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    use_api = os.getenv("USE_API", "false").lower() == "true"
    
    if use_api and openai_key:
        return "openai", openai_key
    elif use_api and gemini_key:
        return "gemini", gemini_key
    return None, None

def generate_with_openai_api(message: str, history: list, api_key: str):
    """Generate reply using OpenAI API"""
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        system_context = "Tu es un assistant spécialisé dans le domaine pharmaceutique et de la santé (Pharma/MedTech). Tu aides les utilisateurs avec des questions sur les médicaments, les dispositifs médicaux, la recherche pharmaceutique, la réglementation, les essais cliniques, et les innovations en santé. Tu dois TOUJOURS répondre en français."
        
        messages = [{"role": "system", "content": system_context}]
        
        # Add history (last 10 messages)
        for msg in history[-10:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ["user", "assistant"] and content:
                messages.append({"role": role, "content": content})
        
        messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Erreur API OpenAI: {str(e)}")
        return None

@st.cache_resource
def load_model():
    """Load the AI model (cached for performance) - only if API not available"""
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
        st.warning(f"⚠️ Erreur lors du chargement du modèle {model_name}: {e}")
        st.info("Tentative avec un modèle alternatif (GPT-2)...")
        try:
            pipeline_obj = pipeline(
                "text-generation",
                model="gpt2",
                device=-1
            )
            st.success("✅ Modèle GPT-2 chargé avec succès!")
            return pipeline_obj, "gpt2"
        except Exception as e2:
            st.error(f"❌ Impossible de charger un modèle: {e2}")
            st.info("💡 **Recommandation :** Utilisez l'API OpenAI pour des réponses plus fiables (voir README_API.md)")
            return None, None


def get_domain_specific_response(message_lower: str):
    """Get domain-specific response for common Pharma/MedTech questions"""
    # Greetings
    if message_lower in ['bonjour', 'salut', 'hello', 'hi', 'bonsoir', 'bonne journée']:
        return "Bonjour! Je suis un assistant spécialisé dans le domaine pharmaceutique et de la santé (Pharma/MedTech). Je peux vous aider avec des questions sur les médicaments, les dispositifs médicaux, la recherche pharmaceutique, la réglementation, les essais cliniques, et les innovations en santé. Comment puis-je vous aider aujourd'hui?"
    
    # Medications/Drugs
    if any(word in message_lower for word in ['médicament', 'medicament', 'drug', 'molecule', 'principe actif', 'posologie', 'dosage']):
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

def is_clearly_off_topic(text: str) -> bool:
    """Check if text is clearly off-topic"""
    if not text or len(text) < 3:
        return False
    text_lower = text.lower()
    off_topic_keywords = [
        'cuisine', 'cooking', 'recette', 'recipe', 'restaurant',
        'sport', 'football', 'basketball', 'tennis',
        'musique', 'music', 'film', 'movie', 'cinéma',
        'voyage', 'travel', 'vacances', 'vacation',
        'cv', 'curriculum', 'lettre de motivation', 'cover letter',
        'informatique', 'computer', 'programmation', 'programming',
        'voiture', 'car', 'automobile'
    ]
    has_off_topic = any(keyword in text_lower for keyword in off_topic_keywords)
    has_pharma = is_domain_related(text)
    return has_off_topic and not has_pharma

def is_domain_related(text: str) -> bool:
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
    
    return any(keyword in text_lower for keyword in domain_keywords)

def generate_domain_fallback(message: str) -> str:
    """Generate a domain-specific fallback response"""
    message_lower = message.lower().strip()
    
    domain_keywords = [
        'médicament', 'medicament', 'drug', 'pharma', 'pharmaceutique',
        'dispositif médical', 'dispositif medical', 'medical device', 'medtech',
        'essai clinique', 'clinical trial', 'étude clinique',
        'réglementation', 'regulation', 'fda', 'ema', 'ansm',
        'recherche', 'research', 'développement', 'development', 'r&d',
        'pharmacovigilance', 'effet indésirable', 'side effect',
        'biotechnologie', 'biotechnology', 'biotech', 'thérapie génique',
        'santé', 'health', 'médical', 'medical', 'thérapeutique'
    ]
    if any(keyword in message_lower for keyword in domain_keywords):
        return f"Je comprends que vous parlez de '{message}'. Pour mieux vous aider dans le domaine pharmaceutique et de la santé (Pharma/MedTech), pouvez-vous être plus précis? Par exemple :\n• Quelle question avez-vous sur les médicaments ou dispositifs médicaux?\n• Souhaitez-vous des informations sur la réglementation?\n• Avez-vous des questions sur les essais cliniques ou la recherche?"
    
    return f"Je suis désolé, mais je suis spécialisé uniquement dans le domaine pharmaceutique et de la santé (Pharma/MedTech). Je ne peux répondre qu'aux questions concernant :\n• Les médicaments et principes actifs\n• Les dispositifs médicaux (MedTech)\n• Les essais cliniques et la recherche pharmaceutique\n• La réglementation (FDA, EMA, ANSM)\n• La pharmacovigilance et la sécurité des médicaments\n• La biotechnologie pharmaceutique\n• Les innovations en santé\n\nVotre question '{message}' ne semble pas être liée à ce domaine. Pourriez-vous reformuler votre question dans le contexte pharmaceutique et de la santé?"

def is_pharma_question(message_lower: str) -> bool:
    """Check if question is clearly pharmaceutique/medical"""
    pharma_keywords = [
        'médicament', 'medicament', 'drug', 'molecule', 'principe actif', 'posologie', 'dosage',
        'antibiotique', 'antibiotic', 'amoxicilline', 'amoxicillin', 'paracétamol', 'paracetamol',
        'aspirine', 'aspirin', 'ibuprofène', 'ibuprofen', 'pillule', 'comprimé', 'gélule',
        'pénicilline', 'penicillin', 'céphalosporine', 'cephalosporin',
        'effet secondaire', 'side effect', 'effet indésirable', 'adverse', 'contre-indication',
        'indication', 'contraindication', 'interaction', 'pharmacocinétique', 'pharmacodynamie',
        'posologie', 'dosage', 'administration', 'voie d\'administration', 'fonctionne', 'fonctionnement',
        'mécanisme', 'mechanism', 'action', 'comment fonctionne', 'how does', 'how it works',
        'dispositif médical', 'dispositif medical', 'medical device', 'medtech',
        'essai clinique', 'clinical trial', 'étude clinique', 'phase', 'rct',
        'réglementation', 'regulation', 'fda', 'ema', 'ansm', 'amm', 'autorisation',
        'recherche', 'research', 'développement', 'development', 'r&d',
        'pharmacovigilance', 'sécurité', 'safety', 'surveillance', 'toxicité',
        'biotechnologie', 'biotechnology', 'biotech', 'biologique', 'biologic',
        'santé', 'health', 'médical', 'medical', 'thérapeutique', 'therapeutic', 'thérapie',
        'comment', 'pourquoi', 'qu\'est', 'what is', 'how', 'why'
    ]
    has_keyword = any(keyword in message_lower for keyword in pharma_keywords)
    known_drugs = ['amoxicilline', 'amoxicillin', 'paracétamol', 'paracetamol', 'aspirine', 
                  'aspirin', 'ibuprofène', 'ibuprofen', 'pénicilline', 'penicillin']
    has_drug_name = any(drug in message_lower for drug in known_drugs)
    question_words = ['comment', 'pourquoi', 'quels', 'quelle', 'quel', 'qu\'est', 'what', 'how', 'why', 'which']
    is_question = any(qw in message_lower for qw in question_words)
    return has_keyword or (has_drug_name and is_question)

def get_pharma_specific_answer(message_lower: str):
    """Get specific pre-defined answers for common pharma questions - EXPANDED"""
    # Amoxicilline - specific questions (HIGHEST PRIORITY)
    if 'amoxicilline' in message_lower or 'amoxicillin' in message_lower:
        if any(word in message_lower for word in ['fonctionne', 'fonctionnement', 'comment', 'how', 'mécanisme', 'mechanism', 'action', 'works']):
            return "L'Amoxicilline est un antibiotique de la famille des bêta-lactamines (pénicillines). Son mécanisme d'action consiste à inhiber la synthèse de la paroi cellulaire bactérienne en se liant aux protéines de liaison aux pénicillines (PBP). Cela empêche la formation de la paroi cellulaire, entraînant la lyse et la mort des bactéries. L'Amoxicilline est efficace contre de nombreuses bactéries Gram-positives et certaines Gram-négatives. Elle est utilisée pour traiter diverses infections : respiratoires, urinaires, cutanées, et dentaires."
        if any(word in message_lower for word in ['effet', 'side effect', 'indésirable', 'adverse', 'secondaire']):
            return "Les effets secondaires les plus fréquents de l'Amoxicilline incluent :\n• Troubles digestifs : nausées, vomissements, diarrhée\n• Réactions cutanées : éruptions, urticaire\n• Réactions allergiques (plus rares) : anaphylaxie chez les personnes allergiques aux pénicillines\n• Candidose buccale ou vaginale (surinfection fongique)\n\nLes effets graves sont rares mais peuvent inclure des réactions anaphylactiques. En cas de réaction allergique, arrêtez le traitement et consultez immédiatement un professionnel de santé."
        if any(word in message_lower for word in ['posologie', 'dosage', 'dose', 'prendre', 'take', 'utiliser', 'use']):
            return "La posologie de l'Amoxicilline varie selon l'infection :\n• Adultes : généralement 500 mg à 1 g, 3 fois par jour\n• Enfants : 20-50 mg/kg/jour en 3 prises\n• Infections sévères : jusqu'à 3 g par jour en 3 prises\n• Durée : généralement 5 à 10 jours selon l'infection\n\nLa posologie exacte doit être déterminée par un professionnel de santé selon l'infection, l'âge, le poids, et la fonction rénale du patient."
        if any(word in message_lower for word in ['indication', 'utilisé', 'used', 'traitement', 'treatment', 'pour', 'for']):
            return "L'Amoxicilline est indiquée pour le traitement de diverses infections bactériennes :\n• Infections respiratoires : pneumonie, bronchite, sinusite\n• Infections urinaires : cystite, pyélonéphrite\n• Infections cutanées et des tissus mous\n• Infections dentaires et buccales\n• Otite moyenne\n• Infections gynécologiques\n\nElle est efficace contre de nombreuses bactéries Gram-positives (streptocoques, staphylocoques sensibles) et certaines Gram-négatives."
        # Generic Amoxicilline answer
        return "L'Amoxicilline est un antibiotique bêta-lactamine de la famille des pénicillines, largement utilisé pour traiter les infections bactériennes. Elle agit en inhibant la synthèse de la paroi cellulaire bactérienne. Les indications courantes incluent les infections respiratoires, urinaires, cutanées, et dentaires. Les effets secondaires fréquents sont les troubles digestifs et les réactions cutanées. La posologie varie selon l'infection et doit être prescrite par un professionnel de santé."
    
    # General medication mechanism questions
    if any(word in message_lower for word in ['fonctionne', 'fonctionnement', 'comment', 'how', 'mécanisme', 'mechanism', 'works']) and any(word in message_lower for word in ['médicament', 'medicament', 'drug', 'antibiotique', 'antibiotic', 'pharmaceutique']):
        return "Les médicaments fonctionnent selon différents mécanismes d'action selon leur classe :\n• Antibiotiques : inhibent la croissance ou tuent les bactéries en ciblant des structures spécifiques (paroi cellulaire, ADN, protéines)\n• Anti-inflammatoires : réduisent l'inflammation en inhibant les médiateurs inflammatoires\n• Analgésiques : soulagent la douleur en agissant sur les récepteurs de la douleur\n• Antihypertenseurs : abaissent la tension artérielle en agissant sur le système cardiovasculaire\n\nChaque médicament a un mécanisme spécifique qui cible des processus biologiques particuliers dans l'organisme. Pour des informations précises sur un médicament spécifique, pouvez-vous me donner son nom?"
    
    # Effects side effects - general
    if any(word in message_lower for word in ['effet secondaire', 'side effect', 'effet indésirable', 'adverse', 'effets']) and any(word in message_lower for word in ['médicament', 'medicament', 'drug', 'pharmaceutique']):
        return "Les effets secondaires des médicaments varient selon le principe actif et la classe thérapeutique. Les effets les plus fréquents incluent : troubles digestifs (nausées, diarrhée), réactions cutanées, maux de tête, et fatigue. Les effets graves sont plus rares mais peuvent inclure des réactions allergiques, des troubles hépatiques, ou des problèmes cardiaques. Pour des informations précises sur les effets secondaires d'un médicament spécifique, pouvez-vous me donner son nom?"
    
    # Dosage questions - general
    if any(word in message_lower for word in ['posologie', 'dosage', 'dose', 'prendre', 'utiliser']) and any(word in message_lower for word in ['médicament', 'medicament', 'drug', 'pharmaceutique']):
        return "La posologie d'un médicament dépend de plusieurs facteurs :\n• Le type d'infection ou de condition traitée\n• L'âge et le poids du patient\n• La fonction rénale et hépatique\n• Les interactions médicamenteuses\n• La sévérité de la condition\n\nPour des informations précises sur la posologie d'un médicament spécifique, consultez la notice du médicament ou un professionnel de santé."
    
    # Interaction questions
    if any(word in message_lower for word in ['interaction', 'interagit', 'compatible', 'compatibilité']):
        return "Les interactions médicamenteuses peuvent survenir lorsque deux médicaments ou plus sont pris simultanément. Les interactions peuvent :\n• Augmenter ou diminuer l'efficacité d'un médicament\n• Augmenter le risque d'effets secondaires\n• Créer de nouveaux effets indésirables\n\nPour vérifier les interactions d'un médicament spécifique, consultez la notice du médicament, un pharmacien, ou un professionnel de santé."
    
    # Contraindication questions
    if any(word in message_lower for word in ['contre-indication', 'contraindication', 'contre indication', 'ne pas', 'interdit']):
        return "Les contre-indications sont des situations où un médicament ne doit pas être utilisé. Les contre-indications courantes incluent :\n• Allergies connues au médicament ou à ses composants\n• Grossesse ou allaitement (pour certains médicaments)\n• Insuffisance rénale ou hépatique sévère\n• Interactions avec d'autres médicaments\n• Certaines conditions médicales préexistantes\n\nPour connaître les contre-indications d'un médicament spécifique, consultez la notice ou un professionnel de santé."
    
    return None

def is_incoherent(text: str) -> bool:
    """Check if text is incoherent"""
    if not text or len(text) < 3:
        return True
    text_lower = text.lower()
    if len(text) > 10:
        alpha_count = sum(1 for c in text if c.isalpha())
        if alpha_count / len(text) < 0.4:
            return True
    import re
    if re.search(r'[.,!?;:]{4,}', text):
        return True
    incoherent_patterns = ['edit', 'jamaisez', 'suhas', 'geul', 'comptite', 'duranteilleurs',
                          '1stahhaaaaaaaaanggghhhhhhh', 'ahahahhuhhhhaaardyyoooood',
                          'plenialisation', 'soutument', 'chases quand penser']
    if any(pattern in text_lower for pattern in incoherent_patterns):
        return True
    return False

def generate_reply(pipeline_obj, message, history):
    """Generate a reply using the model with domain-specific validation"""
    try:
        # Check if API is available
        api_type, api_key = check_api_available()
        if api_type == "openai" and api_key:
            reply = generate_with_openai_api(message, history, api_key)
            if reply:
                return reply
            # Fall through to local model if API fails
        
        # Clean message
        message = message.strip()
        if not message:
            return "Je n'ai pas compris votre message. Pouvez-vous reformuler votre question concernant le domaine pharmaceutique et de la santé (Pharma/MedTech)?"
        
        message_lower = message.lower().strip()
        
        # Check if this exact question was already asked
        if history:
            recent_user_messages = [msg.get("content", "").lower().strip() for msg in history[-10:] if msg.get("role") == "user"]
            if message_lower in recent_user_messages:
                return "Vous avez déjà posé cette question. Pourriez-vous reformuler ou préciser votre demande?"
        
        # Check if pharma question
        is_pharma = is_pharma_question(message_lower)
        
        # Check for domain-specific inputs first
        if not is_pharma:
            domain_reply = get_domain_specific_response(message_lower)
            if domain_reply:
                return domain_reply
        
        # For pharma questions, ALWAYS use pre-defined answers first (most reliable)
        # Skip model generation for pharma questions to avoid incoherent responses
        if is_pharma:
            specific_answer = get_pharma_specific_answer(message_lower)
            if specific_answer:
                # Check if we already gave this answer
                if history:
                    recent_assistant_messages = [msg.get("content", "").strip() for msg in history[-5:] if msg.get("role") == "assistant"]
                    if specific_answer in recent_assistant_messages:
                        return "J'ai déjà répondu à cette question précédemment. Pourriez-vous poser une question différente ou plus précise sur le même sujet?"
                return specific_answer
            
            # If no specific answer but it's pharma, use intelligent fallback directly
            return generate_domain_fallback(message)
        
        # If no pipeline (API mode), use fallback
        if pipeline_obj is None:
            return generate_domain_fallback(message)
        
        # For non-pharma questions, try generation with validation (max 2 attempts)
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
                    # VERY STRICT validation - reject incoherent responses
                    if (not _is_repetitive(reply) and 
                        _is_valid_response(reply) and
                        not is_incoherent(reply) and
                        is_domain_related(reply)):
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
        
        # If all attempts failed, use intelligent fallback
        if is_pharma:
            specific_answer = get_pharma_specific_answer(message_lower)
            if specific_answer:
                return specific_answer
        return generate_domain_fallback(message)
            
    except Exception as e:
        print(f"Error in generate_reply: {e}")
        import traceback
        traceback.print_exc()
        return generate_domain_fallback(message)

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

# Check API first, then load model if needed
api_type, api_key = check_api_available()
if api_type:
    # API is available, no need to load local model
    if not st.session_state.model_loaded:
        st.session_state.pipeline = None  # API mode
        st.session_state.model_name = f"api-{api_type}"
        st.session_state.model_loaded = True
        st.success(f"✅ API {api_type.upper()} configurée et prête!")
else:
    # No API, try to load local model
    if not st.session_state.model_loaded:
        with st.spinner("Chargement du modèle IA..."):
            pipeline_obj, model_name = load_model()
            if pipeline_obj or model_name:
                st.session_state.pipeline = pipeline_obj
                st.session_state.model_name = model_name
                st.session_state.model_loaded = True
            else:
                st.error("❌ Impossible de charger le modèle local.")
                st.info("💡 **Solution :** Configurez l'API OpenAI pour des réponses plus fiables.")
                st.markdown("""
                **Pour configurer l'API OpenAI :**
                1. Obtenez une clé API sur https://platform.openai.com/api-keys
                2. Configurez les variables d'environnement :
                   - `USE_API=true`
                   - `OPENAI_API_KEY=votre-cle-api`
                   - `OPENAI_MODEL=gpt-3.5-turbo`
                3. Redémarrez l'application
                
                Voir `streamlit_app/README_API.md` pour plus de détails.
                """)
                st.stop()

# Main UI
st.title("💊 Assistant Pharma/MedTech")
st.markdown("**Spécialisé en Pharmaceutique & Santé**")
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
        st.info("""
        👋 **Bonjour!** Je suis un assistant spécialisé dans le domaine **pharmaceutique et de la santé (Pharma/MedTech)**.
        
        Je peux vous aider avec des questions sur :
        - 💊 Médicaments et principes actifs
        - 🏥 Dispositifs médicaux (MedTech)
        - 🔬 Essais cliniques et recherche pharmaceutique
        - 📋 Réglementation (FDA, EMA, ANSM)
        - ⚠️ Pharmacovigilance et sécurité
        - 🧬 Biotechnologie pharmaceutique
        
        **Note :** Je ne peux répondre qu'aux questions liées au domaine pharmaceutique et de la santé.
        """)
    
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
    user_message = user_input.strip()
    
    # Prevent duplicate messages
    if st.session_state.messages:
        last_msg = st.session_state.messages[-1]
        if last_msg.get("role") == "user" and last_msg.get("content") == user_message:
            st.warning("Vous avez déjà envoyé ce message.")
            st.stop()
    
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_message,
        "timestamp": datetime.now().isoformat()
    })
    
    # Generate reply
    with st.spinner("🤔 Réflexion en cours..."):
        try:
            reply = generate_reply(
                st.session_state.pipeline,
                user_message,
                st.session_state.messages[:-1]  # Exclude the just-added user message
            )
            
            if not reply or not reply.strip():
                reply = "Désolé, je n'ai pas pu générer de réponse. Veuillez réessayer."
        except Exception as e:
            st.error(f"Erreur: {str(e)}")
            reply = "Désolé, une erreur s'est produite. Veuillez réessayer."
    
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

