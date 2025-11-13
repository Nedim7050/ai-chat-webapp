# Script pour push vers GitHub
# Usage: .\push-to-github.ps1 -GitHubUsername "votre-username"

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubUsername
)

Write-Host "=== Push vers GitHub ===" -ForegroundColor Green
Write-Host ""

# Vérifier si Git est initialisé
if (-not (Test-Path .git)) {
    Write-Host "Initialisation du repository Git..." -ForegroundColor Yellow
    git init
}

# Configurer Git (si pas déjà fait)
Write-Host "Vérification de la configuration Git..." -ForegroundColor Yellow
$gitUser = git config user.name
$gitEmail = git config user.email

if (-not $gitUser) {
    Write-Host "Configuration Git nécessaire..." -ForegroundColor Yellow
    $userName = Read-Host "Entrez votre nom"
    $userEmail = Read-Host "Entrez votre email"
    git config --global user.name $userName
    git config --global user.email $userEmail
}

# Ajouter tous les fichiers
Write-Host "Ajout des fichiers..." -ForegroundColor Yellow
git add .

# Vérifier s'il y a des changements
$status = git status --short
if (-not $status) {
    Write-Host "Aucun changement à commiter." -ForegroundColor Yellow
    exit 0
}

# Faire le commit
Write-Host "Création du commit..." -ForegroundColor Yellow
git commit -m "Initial commit: AI Chat Webapp avec FastAPI, React et Streamlit"

# Vérifier si le remote existe
$remote = git remote get-url origin 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Ajout du remote GitHub..." -ForegroundColor Yellow
    git remote add origin "https://github.com/$GitHubUsername/ai-chat-webapp.git"
} else {
    Write-Host "Remote GitHub trouvé: $remote" -ForegroundColor Green
    Write-Host "Voulez-vous changer le remote? (o/n)" -ForegroundColor Yellow
    $change = Read-Host
    if ($change -eq "o") {
        git remote set-url origin "https://github.com/$GitHubUsername/ai-chat-webapp.git"
    }
}

# Renommer la branche en main
Write-Host "Renommage de la branche en main..." -ForegroundColor Yellow
git branch -M main 2>$null

# Push vers GitHub
Write-Host "Push vers GitHub..." -ForegroundColor Yellow
Write-Host "Assurez-vous d'avoir créé le repository sur GitHub: https://github.com/new" -ForegroundColor Cyan
Write-Host "Repository: $GitHubUsername/ai-chat-webapp" -ForegroundColor Cyan
Write-Host ""
Write-Host "Appuyez sur Entrée pour continuer..." -ForegroundColor Yellow
Read-Host

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== Succès! ===" -ForegroundColor Green
    Write-Host "Repository GitHub: https://github.com/$GitHubUsername/ai-chat-webapp" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Prochaines étapes:" -ForegroundColor Yellow
    Write-Host "1. Allez sur https://share.streamlit.io" -ForegroundColor White
    Write-Host "2. Connectez votre compte GitHub" -ForegroundColor White
    Write-Host "3. Créez une nouvelle app avec:" -ForegroundColor White
    Write-Host "   - Repository: $GitHubUsername/ai-chat-webapp" -ForegroundColor White
    Write-Host "   - Main file path: streamlit_app/app.py" -ForegroundColor White
    Write-Host "   - Branch: main" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "=== Erreur lors du push ===" -ForegroundColor Red
    Write-Host "Vérifiez que:" -ForegroundColor Yellow
    Write-Host "1. Le repository existe sur GitHub" -ForegroundColor White
    Write-Host "2. Vous avez les permissions nécessaires" -ForegroundColor White
    Write-Host "3. Vous êtes authentifié avec GitHub" -ForegroundColor White
    Write-Host ""
    Write-Host "Pour vous authentifier:" -ForegroundColor Yellow
    Write-Host "git config --global credential.helper wincred" -ForegroundColor Cyan
}

