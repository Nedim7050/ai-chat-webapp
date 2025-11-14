# Configuration API pour Streamlit

Pour utiliser l'API OpenAI dans Streamlit, configurez les variables d'environnement dans Streamlit Cloud :

## Configuration dans Streamlit Cloud

1. Allez sur https://share.streamlit.io/
2. Sélectionnez votre app
3. Cliquez sur "Settings" → "Secrets"
4. Ajoutez ces secrets :

```toml
OPENAI_API_KEY = "sk-votre-cle-api-ici"
USE_API = "true"
OPENAI_MODEL = "gpt-3.5-turbo"
API_TYPE = "openai"
```

## Configuration locale

**Windows PowerShell:**
```powershell
$env:USE_API="true"
$env:OPENAI_API_KEY="sk-votre-cle-api-ici"
$env:OPENAI_MODEL="gpt-3.5-turbo"
$env:API_TYPE="openai"
```

**Linux/Mac:**
```bash
export USE_API=true
export OPENAI_API_KEY="sk-votre-cle-api-ici"
export OPENAI_MODEL="gpt-3.5-turbo"
export API_TYPE="openai"
```

## Démarrer Streamlit

```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

L'app utilisera automatiquement l'API OpenAI si configurée, sinon le modèle local.

