# 🔧 Guide de Dépannage

## Erreur 403 (Forbidden)

### Symptômes
- Erreur `Failed to load resource: the server responded with a status of 403`
- Le frontend ne peut pas se connecter au backend

### Solutions

#### 1. Vérifier que le backend est démarré

```powershell
# Vérifier si le backend tourne
curl http://localhost:8000/health

# Ou ouvrir dans le navigateur
# http://localhost:8000/docs
```

Si le backend ne répond pas:
```powershell
cd backend
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

#### 2. Vérifier la configuration CORS

Le backend doit autoriser l'origine du frontend. Vérifiez `backend/app/main.py`:

```python
allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "*"  # En développement seulement
]
```

#### 3. Utiliser le proxy Vite

Le frontend utilise maintenant le proxy Vite par défaut en développement. Vérifiez `frontend/vite.config.js`:

```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, '')
  }
}
```

#### 4. Vérifier l'URL de l'API

Le frontend utilise automatiquement `/api` en développement (qui est proxy vers `http://localhost:8000`).

Pour forcer une URL spécifique, créez `frontend/.env`:
```
VITE_API_URL=http://localhost:8000
```

## Autres erreurs

### Erreur: "Model not loaded yet"

**Cause:** Le modèle IA est encore en train de se charger.

**Solution:** Attendez 30-60 secondes après le démarrage du backend, puis réessayez.

### Erreur: "Timeout"

**Cause:** La requête prend trop de temps (plus de 60 secondes).

**Solutions:**
1. Utilisez un modèle plus petit
2. Vérifiez votre connexion internet
3. Augmentez le timeout dans `frontend/src/App.jsx`:
   ```javascript
   signal: AbortSignal.timeout(120000) // 120 secondes
   ```

### Erreur: "Cannot connect to backend"

**Cause:** Le backend n'est pas démarré ou l'URL est incorrecte.

**Solutions:**
1. Vérifiez que le backend tourne sur le port 8000
2. Vérifiez l'URL dans la console du navigateur
3. Vérifiez les logs du backend

### Warnings dans la console (non critiques)

Les warnings suivants sont normaux et n'affectent pas le fonctionnement:
- `Unrecognized feature: 'ambient-light-sensor'`
- `Unrecognized feature: 'battery'`
- etc.

Ces warnings viennent de Vite/React et peuvent être ignorés.

## Vérification rapide

### Checklist

- [ ] Backend démarré sur http://localhost:8000
- [ ] Frontend démarré sur http://localhost:5173
- [ ] Le endpoint `/health` répond: `curl http://localhost:8000/health`
- [ ] CORS configuré correctement dans le backend
- [ ] Pas d'erreurs dans la console du backend
- [ ] Pas d'erreurs bloquantes dans la console du navigateur

### Test de connexion

1. **Test du backend:**
   ```powershell
   curl http://localhost:8000/health
   ```
   Devrait retourner: `{"status":"healthy","model_loaded":true}`

2. **Test du frontend:**
   - Ouvrez http://localhost:5173
   - Vérifiez l'indicateur de statut (devrait être "En ligne")
   - Envoyez un message de test

3. **Test de l'API:**
   ```powershell
   curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{\"message\":\"Bonjour\",\"history\":[]}'
   ```

## Logs utiles

### Backend
Les logs du backend montrent:
- Chargement du modèle
- Erreurs de génération
- Requêtes reçues

### Frontend
Ouvrez la console du navigateur (F12) pour voir:
- Erreurs de connexion
- Erreurs de requête
- Statut de connexion

## Support

Si le problème persiste:
1. Vérifiez les logs du backend
2. Vérifiez la console du navigateur
3. Vérifiez que toutes les dépendances sont installées
4. Réinstallez les dépendances si nécessaire

