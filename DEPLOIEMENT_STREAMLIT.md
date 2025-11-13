# 🚀 Déploiement sur Streamlit Cloud

Votre projet est maintenant sur GitHub! Voici comment le déployer sur Streamlit Cloud.

## 📋 Prérequis

- ✅ Code poussé sur GitHub (fait!)
- ✅ Compte GitHub
- ✅ Compte Streamlit Cloud (gratuit)

## 🎯 Étapes de déploiement

### 1. Créer un compte Streamlit Cloud

1. Allez sur [share.streamlit.io](https://share.streamlit.io)
2. Cliquez sur "Sign up" ou "Get started"
3. Connectez-vous avec votre compte GitHub

### 2. Déployer votre application

1. **Cliquez sur "New app"** dans le tableau de bord Streamlit Cloud

2. **Remplissez le formulaire:**
   - **Repository:** `Nedim7050/ai-chat-webapp`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app/app.py`
   - **Python version:** `3.11` (recommandé)

3. **Cliquez sur "Deploy"**

### 3. Attendre le déploiement

- Streamlit Cloud va automatiquement:
  - Installer les dépendances depuis `streamlit_app/requirements.txt`
  - Télécharger le modèle IA (DialoGPT-small)
  - Démarrer l'application

**Note:** Le premier déploiement peut prendre 5-10 minutes car le modèle doit être téléchargé.

### 4. Accéder à votre application

Une fois déployée, votre application sera accessible sur:
```
https://ai-chat-webapp.streamlit.app
```
(ou un nom similaire selon la disponibilité)

## ⚙️ Configuration avancée (optionnel)

### Variables d'environnement

Si vous avez besoin de variables d'environnement:
1. Dans Streamlit Cloud, allez dans les paramètres de votre app
2. Section "Secrets" ou "Environment variables"
3. Ajoutez vos variables

### Fichier `.streamlit/config.toml` (optionnel)

Vous pouvez créer un fichier de configuration:

```toml
[server]
port = 8501
enableCORS = false
enableXsrfProtection = false

[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

## 🔧 Dépannage

### Le déploiement échoue

1. **Vérifiez les logs** dans Streamlit Cloud
2. **Vérifiez que `streamlit_app/app.py` existe** à la racine du repo
3. **Vérifiez les dépendances** dans `streamlit_app/requirements.txt`

### Le modèle ne se charge pas

- Vérifiez votre connexion internet
- Le modèle sera téléchargé automatiquement au premier lancement
- Cela peut prendre quelques minutes

### Erreur de mémoire

- Streamlit Cloud a des limites de mémoire
- Utilisez un modèle plus petit si nécessaire
- Considérez l'utilisation de l'API Hugging Face Inference

## 📝 Mise à jour de l'application

Pour mettre à jour votre application:

1. Faites vos modifications localement
2. Committez et pushez vers GitHub:
   ```bash
   git add .
   git commit -m "Description des modifications"
   git push origin main
   ```
3. Streamlit Cloud redéploiera automatiquement!

## 🎉 C'est tout!

Votre application sera accessible publiquement sur Streamlit Cloud!

---

**URL de votre repo GitHub:** https://github.com/Nedim7050/ai-chat-webapp

