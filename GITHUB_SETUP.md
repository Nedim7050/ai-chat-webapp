# 📤 Configuration GitHub et déploiement Streamlit

## Étape 1: Créer un repository GitHub

1. Allez sur https://github.com
2. Cliquez sur le bouton "+" en haut à droite
3. Sélectionnez "New repository"
4. Remplissez les informations:
   - **Repository name**: `ai-chat-webapp`
   - **Description**: `Application complète de chatbot IA avec FastAPI, React et Streamlit`
   - **Visibility**: Public ou Private
   - **NE COCHEZ PAS** "Initialize this repository with a README"
5. Cliquez sur "Create repository"

## Étape 2: Push vers GitHub

### Méthode rapide (Script PowerShell)

```powershell
# Exécuter le script avec votre nom d'utilisateur GitHub
.\push-to-github.ps1 -GitHubUsername "VOTRE_USERNAME"
```

### Méthode manuelle

```powershell
# 1. Configurer Git (si pas déjà fait)
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@example.com"

# 2. Ajouter tous les fichiers
git add .

# 3. Faire le commit
git commit -m "Initial commit: AI Chat Webapp avec FastAPI, React et Streamlit"

# 4. Ajouter le remote GitHub (remplacez VOTRE_USERNAME)
git remote add origin https://github.com/VOTRE_USERNAME/ai-chat-webapp.git

# 5. Renommer la branche en main
git branch -M main

# 6. Push vers GitHub
git push -u origin main
```

### Si vous avez déjà un remote

```powershell
# Vérifier le remote actuel
git remote -v

# Changer le remote (si nécessaire)
git remote set-url origin https://github.com/VOTRE_USERNAME/ai-chat-webapp.git

# Push
git push -u origin main
```

## Étape 3: Déployer sur Streamlit Cloud

### Option A: Via l'interface Streamlit Cloud (Recommandé)

1. **Allez sur Streamlit Cloud**
   - Ouvrez https://share.streamlit.io
   - Connectez-vous avec votre compte GitHub
   - Autorisez Streamlit Cloud à accéder à vos repositories

2. **Créer une nouvelle app**
   - Cliquez sur "New app"
   - Remplissez les informations:
     - **Repository**: `VOTRE_USERNAME/ai-chat-webapp`
     - **Branch**: `main`
     - **Main file path**: `streamlit_app/app.py`
     - **Python version**: `3.11` (recommandé)
   - Cliquez sur "Deploy"

3. **Attendre le déploiement**
   - Streamlit Cloud installera automatiquement les dépendances
   - Le premier déploiement peut prendre 5-10 minutes (téléchargement du modèle)
   - Votre app sera accessible sur `https://votre-app.streamlit.app`

### Option B: Via Streamlit CLI

```powershell
# 1. Installer Streamlit CLI (si pas déjà fait)
pip install streamlit

# 2. Se connecter à Streamlit Cloud
streamlit login

# 3. Déployer l'application
cd streamlit_app
streamlit deploy app.py
```

## ✅ Vérification

### Vérifier le repository GitHub

- Allez sur https://github.com/VOTRE_USERNAME/ai-chat-webapp
- Vérifiez que tous les fichiers sont présents
- Vérifiez que `streamlit_app/app.py` existe

### Vérifier le déploiement Streamlit

- Ouvrez l'URL de votre app Streamlit Cloud
- Attendez que le modèle se charge (peut prendre 1-2 minutes)
- Testez l'interface de chat
- Vérifiez que les messages sont générés correctement

## 🔄 Mises à jour

### Mettre à jour le code

```powershell
# 1. Faire vos modifications
# 2. Ajouter les changements
git add .

# 3. Commit les changements
git commit -m "Description des changements"

# 4. Push vers GitHub
git push origin main

# Streamlit Cloud redéploiera automatiquement
```

## 🐛 Dépannage

### Problème: Erreur lors du push GitHub

**Solutions:**
- Vérifiez que le repository existe sur GitHub
- Vérifiez que vous êtes authentifié: `git config --global credential.helper wincred`
- Vérifiez les permissions du repository

### Problème: Streamlit Cloud ne trouve pas le fichier

**Solutions:**
- Vérifiez que le "Main file path" est `streamlit_app/app.py`
- Vérifiez que le fichier existe dans le repository GitHub
- Vérifiez que vous avez push sur la bonne branche

### Problème: Erreur d'installation des dépendances

**Solutions:**
- Vérifiez que `streamlit_app/requirements.txt` est correct
- Vérifiez les logs de déploiement dans Streamlit Cloud
- Assurez-vous d'utiliser Python 3.11 ou 3.12

### Problème: Le modèle ne se charge pas

**Solutions:**
- Attendez quelques minutes lors du premier déploiement
- Vérifiez les logs pour plus de détails
- Vérifiez votre connexion internet (Streamlit Cloud doit télécharger le modèle)

## 📚 Ressources

- **GitHub:** https://github.com
- **Streamlit Cloud:** https://share.streamlit.io
- **Documentation Streamlit:** https://docs.streamlit.io
- **Documentation Streamlit Cloud:** https://docs.streamlit.io/streamlit-community-cloud

## 🎉 Félicitations!

Une fois déployé, votre application sera accessible publiquement sur Streamlit Cloud!

---

**Bon déploiement ! 🚀**

