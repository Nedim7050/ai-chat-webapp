# Backend FastAPI

Backend API pour le chatbot IA utilisant FastAPI et Hugging Face Transformers.

## Installation

### 1. Créer un environnement virtuel

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Sur Linux/Mac:
```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Installer les dépendances

```bash
pip install -r app/requirements.txt
```

### 3. Lancer le serveur

```bash
uvicorn app.main:app --reload --port 8000
```

Le serveur sera accessible sur `http://localhost:8000`

## Endpoints

### GET /health
Vérifie l'état du serveur et du modèle.

**Réponse:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### POST /chat
Envoie un message au chatbot.

**Requête:**
```json
{
  "message": "Bonjour, comment ça va?",
  "history": [
    {"role": "user", "content": "Salut"},
    {"role": "assistant", "content": "Bonjour!"}
  ]
}
```

**Réponse:**
```json
{
  "reply": "Bonjour! Je vais bien, merci de demander.",
  "usage": {
    "model": "microsoft/DialoGPT-small",
    "tokens": 10
  }
}
```

## Modèle utilisé

Par défaut, le backend utilise `microsoft/DialoGPT-small`, un modèle conversationnel léger.

Pour utiliser un autre modèle, modifiez `model_name` dans `app/model.py`:

```python
chat_model = ChatModel(model_name="votre-modele")
```

## Documentation API

Une fois le serveur lancé, accédez à:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Notes

- Le modèle se charge au démarrage du serveur (peut prendre quelques secondes)
- Le premier chargement télécharge le modèle depuis Hugging Face (peut prendre du temps)
- Pour réduire l'utilisation mémoire, utilisez des modèles plus petits ou l'API Hugging Face Inference

