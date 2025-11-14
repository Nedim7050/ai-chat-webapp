# Configuration API pour le Chatbot

Ce projet supporte maintenant l'utilisation d'APIs externes (OpenAI GPT ou Google Gemini) pour des réponses plus fiables et précises.

## Configuration OpenAI (Recommandé)

### 1. Obtenir une clé API OpenAI

1. Allez sur https://platform.openai.com/
2. Créez un compte ou connectez-vous
3. Allez dans "API keys" (https://platform.openai.com/api-keys)
4. Créez une nouvelle clé API
5. Copiez la clé (elle commence par `sk-...`)

### 2. Configurer l'environnement

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

**Ou créez un fichier `.env` dans le dossier `backend/`:**
```
USE_API=true
OPENAI_API_KEY=sk-votre-cle-api-ici
OPENAI_MODEL=gpt-3.5-turbo
API_TYPE=openai
```

### 3. Installer les dépendances

```bash
cd backend
pip install openai requests
```

### 4. Démarrer le serveur

```bash
uvicorn app.main:app --reload --port 8000
```

## Configuration Google Gemini (Alternative)

### 1. Obtenir une clé API Gemini

1. Allez sur https://makersuite.google.com/app/apikey
2. Créez une clé API
3. Copiez la clé

### 2. Configurer l'environnement

```powershell
$env:USE_API="true"
$env:GEMINI_API_KEY="votre-cle-gemini-ici"
$env:API_TYPE="gemini"
```

## Modèles disponibles

### OpenAI
- `gpt-3.5-turbo` (recommandé, économique)
- `gpt-4` (plus puissant, plus cher)
- `gpt-4-turbo` (meilleur rapport qualité/prix)

### Google Gemini
- `gemini-pro` (utilisé par défaut)

## Coûts approximatifs

### OpenAI GPT-3.5-turbo
- ~$0.002 par 1000 tokens (entrée)
- ~$0.002 par 1000 tokens (sortie)
- Une conversation typique coûte environ $0.01-0.05

### Google Gemini
- Gratuit jusqu'à 60 requêtes/minute
- Puis payant selon usage

## Avantages de l'API

✅ Réponses plus précises et cohérentes
✅ Pas besoin de charger un modèle local (plus rapide)
✅ Moins de problèmes de mémoire
✅ Meilleure compréhension du contexte
✅ Support multilingue amélioré

## Fallback automatique

Si l'API n'est pas configurée ou échoue, le système utilise automatiquement le modèle local (DialoGPT-small).

## Désactiver l'API

Pour utiliser uniquement le modèle local:

```powershell
$env:USE_API="false"
```

Ou ne pas définir les variables d'environnement API.

