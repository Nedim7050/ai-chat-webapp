# Streamlit App

Application Streamlit standalone pour le chatbot IA, déployable sur Streamlit Cloud sans Docker.

## Installation locale

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
pip install -r requirements.txt
```

### 3. Lancer l'application

```bash
streamlit run app.py
```

L'application sera accessible sur `http://localhost:8501`

## Déploiement sur Streamlit Cloud

### Méthode 1: Via GitHub

1. **Pousser votre code sur GitHub**
   - Créez un repo GitHub
   - Poussez le dossier `streamlit_app/` à la racine ou dans un sous-dossier

2. **Connecter à Streamlit Cloud**
   - Allez sur [share.streamlit.io](https://share.streamlit.io)
   - Connectez votre compte GitHub
   - Cliquez sur "New app"
   - Sélectionnez votre repo et la branche
   - **Chemin principal:** `streamlit_app/app.py` (ou `app.py` si à la racine)
   - Cliquez sur "Deploy"

3. **Attendre le déploiement**
   - Streamlit Cloud installera automatiquement les dépendances depuis `requirements.txt`
   - Le premier déploiement peut prendre quelques minutes (téléchargement du modèle)

### Méthode 2: Via Streamlit CLI

```bash
streamlit login
streamlit deploy streamlit_app/app.py
```

## Fonctionnalités

- 💬 Interface de chat intuitive
- 🗑️ Bouton pour effacer la conversation
- 📥 Téléchargement de la conversation en JSON
- 🔄 Gestion de l'historique de conversation
- ⚡ Modèle chargé en cache pour de meilleures performances

## Structure du fichier

Le fichier `app.py` contient:
- Chargement du modèle (avec cache Streamlit)
- Interface utilisateur complète
- Gestion de l'historique de conversation
- Export de conversation

## Notes

- Le modèle se charge au premier lancement (peut prendre du temps)
- Streamlit Cloud utilise des ressources limitées, privilégiez des modèles légers
- Pour de meilleures performances, considérez l'utilisation de l'API Hugging Face Inference

## Dépannage

**Erreur de mémoire:**
- Utilisez un modèle plus petit ou l'API Hugging Face Inference
- Réduisez la taille du batch dans le code

**Modèle ne se charge pas:**
- Vérifiez votre connexion internet (téléchargement initial)
- Vérifiez que le modèle existe sur Hugging Face
- Consultez les logs Streamlit Cloud pour plus de détails

