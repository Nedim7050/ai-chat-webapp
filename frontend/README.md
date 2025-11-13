# Frontend React

Interface React pour le chatbot IA, connectée au backend FastAPI.

## Installation

### Prérequis
- Node.js 18+ et npm (ou yarn/pnpm)

### Installation des dépendances

```bash
npm install
```

## Développement

Lancer le serveur de développement:

```bash
npm run dev
```

L'application sera accessible sur `http://localhost:5173`

## Build pour production

```bash
npm run build
```

Les fichiers optimisés seront dans le dossier `dist/`.

## Configuration

Par défaut, le frontend se connecte à `http://localhost:8000`.

Pour changer l'URL de l'API, créez un fichier `.env`:

```
VITE_API_URL=http://votre-backend-url:8000
```

## Fonctionnalités

- Interface de chat moderne et responsive
- Bulles de messages distinctes pour utilisateur et assistant
- Indicateur de frappe pendant la génération
- Gestion des erreurs
- Effacement de la conversation
- Support du clavier (Enter pour envoyer)

## Déploiement

### Vercel

1. Connectez votre repo GitHub à Vercel
2. Configurez la variable d'environnement `VITE_API_URL` avec l'URL de votre backend
3. Déployez!

### Netlify

1. Connectez votre repo GitHub à Netlify
2. Build command: `npm run build`
3. Publish directory: `dist`
4. Ajoutez la variable d'environnement `VITE_API_URL`

