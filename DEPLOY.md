# 🚀 Guide de déploiement

## 📤 Push vers GitHub

### 1. Créer un repository GitHub

1. Allez sur https://github.com
2. Cliquez sur "New repository"
3. Nommez-le `ai-chat-webapp`
4. Choisissez Public ou Private
5. **Ne cochez PAS** "Initialize this repository with a README"
6. Cliquez sur "Create repository"

### 2. Configurer Git et push

```powershell
# 1. Vérifier que vous êtes dans le bon répertoire
cd C:\Users\najdm\ai-chat-webapp

# 2. Initialiser Git (si pas déjà fait)
git init

# 3. Ajouter tous les fichiers
git add .

# 4. Faire le premier commit
git commit -m "Initial commit: AI Chat Webapp avec FastAPI, React et Streamlit"

# 5. Ajouter le remote GitHub (remplacez VOTRE_USERNAME)
git remote add origin https://github.com/VOTRE_USERNAME/ai-chat-webapp.git

# 6. Renommer la branche principale en main (si nécessaire)
git branch -M main

# 7. Push vers GitHub
git push -u origin main
```

### 3. Si vous avez déjà un repo GitHub

```powershell
# Vérifier le remote actuel
git remote -v

# Changer le remote (si nécessaire)
git remote set-url origin https://github.com/VOTRE_USERNAME/ai-chat-webapp.git

# Push
git push -u origin main
```

## 🎈 Déploiement sur Streamlit Cloud

### Méthode 1: Via l'interface Streamlit Cloud (Recommandé)

1. **Poussez votre code sur GitHub**
   - Suivez les étapes ci-dessus pour push vers GitHub

2. **Connecter à Streamlit Cloud**
   - Allez sur https://share.streamlit.io
   - Connectez-vous avec votre compte GitHub
   - Autorisez Streamlit Cloud à accéder à vos repositories

3. **Créer une nouvelle app**
   - Cliquez sur "New app"
   - **Repository**: Sélectionnez `VOTRE_USERNAME/ai-chat-webapp`
   - **Branch**: `main` (ou `master`)
   - **Main file path**: `streamlit_app/app.py`
   - **Python version**: `3.11` (recommandé)
   - Cliquez sur "Deploy"

4. **Attendre le déploiement**
   - Streamlit Cloud installera automatiquement les dépendances depuis `streamlit_app/requirements.txt`
   - Le premier déploiement peut prendre 5-10 minutes (téléchargement du modèle)
   - Votre app sera accessible sur `https://votre-app.streamlit.app`

### Méthode 2: Via Streamlit CLI

```powershell
# 1. Installer Streamlit CLI (si pas déjà fait)
pip install streamlit

# 2. Se connecter à Streamlit Cloud
streamlit login

# 3. Déployer l'application
cd streamlit_app
streamlit deploy app.py
```

## 📝 Configuration pour Streamlit Cloud

### Fichier `.streamlit/config.toml` (optionnel)

Créé automatiquement dans `streamlit_app/.streamlit/config.toml`

### Fichier `requirements.txt`

Le fichier `streamlit_app/requirements.txt` est utilisé automatiquement par Streamlit Cloud.

### Variables d'environnement (optionnel)

Si vous avez besoin de variables d'environnement:

1. Allez sur votre app Streamlit Cloud
2. Cliquez sur "Settings" (⚙️)
3. Allez dans "Secrets"
4. Ajoutez vos variables d'environnement

## 🔧 Vérifications avant déploiement

### 1. Vérifier les fichiers nécessaires

```powershell
# Vérifier que tous les fichiers sont présents
ls streamlit_app/app.py
ls streamlit_app/requirements.txt
ls streamlit_app/.streamlit/config.toml
```

### 2. Tester localement

```powershell
# Tester l'application Streamlit localement
cd streamlit_app
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

### 3. Vérifier les dépendances

Assurez-vous que `streamlit_app/requirements.txt` contient toutes les dépendances nécessaires:

```
streamlit>=1.28.0
transformers>=4.30.0
torch>=2.0.0
sentencepiece>=0.1.99
accelerate>=0.20.0
```

## 🐛 Dépannage du déploiement

### Problème: Erreur lors du push GitHub

**Solution:**
```powershell
# Vérifier la configuration Git
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@example.com"

# Réessayer le push
git push -u origin main
```

### Problème: Streamlit Cloud ne trouve pas le fichier

**Solution:**
- Vérifiez que le "Main file path" est `streamlit_app/app.py`
- Vérifiez que le fichier existe dans le repository GitHub

### Problème: Erreur d'installation des dépendances

**Solution:**
- Vérifiez que `requirements.txt` est correct
- Vérifiez les logs de déploiement dans Streamlit Cloud
- Assurez-vous d'utiliser Python 3.11 ou 3.12

### Problème: Le modèle ne se charge pas

**Solution:**
- Vérifiez votre connexion internet (Streamlit Cloud doit télécharger le modèle)
- Attendez quelques minutes lors du premier déploiement
- Vérifiez les logs pour plus de détails

## 📊 Vérification après déploiement

### Vérifier que l'app fonctionne

1. Ouvrez l'URL de votre app Streamlit Cloud
2. Attendez que le modèle se charge (peut prendre 1-2 minutes)
3. Testez l'interface de chat
4. Vérifiez que les messages sont générés correctement

## 🔄 Mises à jour

### Mettre à jour l'application

```powershell
# 1. Faire vos modifications
# 2. Commit les changements
git add .
git commit -m "Description des changements"

# 3. Push vers GitHub
git push origin main

# Streamlit Cloud redéploiera automatiquement
```

### Forcer un redéploiement

1. Allez sur votre app Streamlit Cloud
2. Cliquez sur "Manage app"
3. Cliquez sur "Reboot app"

## 📚 Ressources

- **GitHub:** https://github.com
- **Streamlit Cloud:** https://share.streamlit.io
- **Documentation Streamlit:** https://docs.streamlit.io
- **Documentation Streamlit Cloud:** https://docs.streamlit.io/streamlit-community-cloud

## 🎉 Félicitations!

Une fois déployé, votre application sera accessible publiquement sur Streamlit Cloud!

---

**Bon déploiement ! 🚀**

