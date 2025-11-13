# Models Directory

Ce dossier contient les instructions pour les modèles de chatbot IA.

## Modèles recommandés

### Modèles légers (recommandés pour développement local)

1. **microsoft/DialoGPT-small**
   - Taille: ~117 MB
   - Type: Modèle conversationnel
   - Usage: Par défaut dans le projet

2. **gpt2**
   - Taille: ~500 MB
   - Type: Génération de texte
   - Usage: Fallback si DialoGPT échoue

### Modèles alternatifs

- **microsoft/DialoGPT-medium** (~350 MB)
- **microsoft/DialoGPT-large** (~1.5 GB) - Nécessite plus de RAM
- **facebook/blenderbot-small-90M** (~360 MB)

## Utilisation de l'API Hugging Face Inference

Pour éviter de télécharger et charger de gros modèles localement, vous pouvez utiliser l'API Hugging Face Inference:

```python
import requests

def generate_with_api(message, history):
    API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
    headers = {"Authorization": f"Bearer {YOUR_API_TOKEN}"}
    
    payload = {
        "inputs": {
            "past_user_inputs": [h["content"] for h in history if h["role"] == "user"],
            "generated_responses": [h["content"] for h in history if h["role"] == "assistant"],
            "text": message
        }
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()
```

## Téléchargement manuel

Si vous souhaitez télécharger les modèles manuellement:

```bash
# Installer huggingface-hub
pip install huggingface-hub

# Télécharger un modèle
python -c "from transformers import AutoModelForCausalLM, AutoTokenizer; AutoModelForCausalLM.from_pretrained('microsoft/DialoGPT-small'); AutoTokenizer.from_pretrained('microsoft/DialoGPT-small')"
```

Les modèles seront téléchargés dans `~/.cache/huggingface/transformers/` (Linux/Mac) ou `C:\Users\<user>\.cache\huggingface\transformers\` (Windows).

## Notes

- Les modèles sont automatiquement téléchargés au premier usage
- Assurez-vous d'avoir suffisamment d'espace disque (au moins 2-3 GB)
- Pour la production, considérez l'utilisation de l'API Hugging Face ou d'un service cloud

