# AI Chat Webapp

Application complète de chatbot IA avec deux variantes de déploiement:
1. **Full-stack**: Backend FastAPI + Frontend React
2. **Streamlit-only**: Application Streamlit standalone

## 🚀 Démarrage rapide

### Variante A: Full-stack (FastAPI + React)

#### Backend

```powershell
# Windows PowerShell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r app/requirements.txt
uvicorn app.main:app --reload --port 8000
```

```bash
# Linux/Mac
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
uvicorn app.main:app --reload --port 8000
```

Le backend sera accessible sur `http://localhost:8000`

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

Le frontend sera accessible sur `http://localhost:5173`

### Variante B: Streamlit-only

```powershell
# Windows PowerShell
cd streamlit_app
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

```bash
# Linux/Mac
cd streamlit_app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

L'application sera accessible sur `http://localhost:8501`

## 📁 Structure du projet

```
ai-chat-webapp/
├── backend/                 # Backend FastAPI
│   ├── app/
│   │   ├── main.py         # Application FastAPI principale
│   │   ├── model.py        # Wrapper pour le modèle IA
│   │   └── requirements.txt
│   └── README.md
├── frontend/               # Frontend React
│   ├── src/
│   │   ├── App.jsx         # Composant principal React
│   │   ├── App.css         # Styles
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── README.md
├── streamlit_app/          # Application Streamlit
│   ├── app.py              # Application Streamlit complète
│   ├── requirements.txt
│   └── README.md
├── models/                 # Instructions pour les modèles
│   └── README.md
├── README.md               # Ce fichier
└── LICENSE
```

## 🔧 Configuration

### Backend

Le backend utilise par défaut le modèle `microsoft/DialoGPT-small`. Pour changer de modèle, modifiez `backend/app/model.py`:

```python
chat_model = ChatModel(model_name="votre-modele")
```

### Frontend

Pour changer l'URL de l'API backend, créez un fichier `.env` dans `frontend/`:

```
VITE_API_URL=http://localhost:8000
```

## 📦 Déploiement

### Backend (FastAPI)

#### Render / Heroku

1. Créez un compte sur [Render](https://render.com) ou [Heroku](https://heroku.com)
2. Connectez votre repo GitHub
3. Créez un nouveau service web
4. Configurez:
   - **Build Command**: `pip install -r backend/app/requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Working Directory**: `backend`

#### Railway

1. Connectez votre repo GitHub à [Railway](https://railway.app)
2. Sélectionnez le dossier `backend`
3. Railway détectera automatiquement FastAPI et installera les dépendances

### Frontend (React)

#### Vercel

1. Connectez votre repo GitHub à [Vercel](https://vercel.com)
2. Configurez:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
3. Ajoutez la variable d'environnement `VITE_API_URL` avec l'URL de votre backend déployé

#### Netlify

1. Connectez votre repo GitHub à [Netlify](https://netlify.com)
2. Configurez:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`
3. Ajoutez la variable d'environnement `VITE_API_URL`

### Streamlit App

#### Streamlit Cloud

1. Poussez votre code sur GitHub
2. Allez sur [share.streamlit.io](https://share.streamlit.io)
3. Connectez votre compte GitHub
4. Créez une nouvelle app:
   - **Repository**: Votre repo
   - **Branch**: `main` (ou `master`)
   - **Main file path**: `streamlit_app/app.py`
5. Cliquez sur "Deploy"

L'application sera accessible sur `https://votre-app.streamlit.app`

## 🧪 Tests

### Tester le backend

```bash
# Health check
curl http://localhost:8000/health

# Chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Bonjour!", "history": []}'
```

### Tester le frontend

Ouvrez `http://localhost:5173` dans votre navigateur et testez l'interface de chat.

### Tester Streamlit

Ouvrez `http://localhost:8501` dans votre navigateur et testez l'application.

## 📚 Documentation API

Une fois le backend lancé, accédez à:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔒 Sécurité et performances

### Recommandations

1. **Rate limiting**: Ajoutez un middleware de rate limiting pour éviter les abus
2. **Modèles légers**: Utilisez des modèles petits pour réduire l'utilisation mémoire
3. **API Hugging Face**: Pour la production, considérez l'utilisation de l'API Hugging Face Inference au lieu de charger le modèle localement
4. **CORS**: Configurez correctement les origines CORS pour la production

### Exemple de rate limiting (optionnel)

Ajoutez dans `backend/app/main.py`:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request, chat_request: ChatRequest):
    # ...
```

## 🐛 Dépannage

### Le modèle ne se charge pas

- Vérifiez votre connexion internet (téléchargement initial)
- Assurez-vous d'avoir suffisamment d'espace disque (2-3 GB)
- Vérifiez les logs pour plus de détails

### Erreur de mémoire

- Utilisez un modèle plus petit
- Réduisez la taille du batch
- Utilisez l'API Hugging Face Inference

### CORS errors

- Vérifiez que l'URL du frontend est dans `allow_origins` du backend
- Pour la production, remplacez `localhost` par votre domaine

## 📝 Licence

Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🤝 Contribution

Les contributions sont les bienvenues! N'hésitez pas à ouvrir une issue ou une pull request.

## 📧 Support

Pour toute question ou problème, ouvrez une issue sur GitHub.

