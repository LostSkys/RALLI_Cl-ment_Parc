#!/bin/sh
# ==========================================
# Script d'initialisation pour Angular
# ==========================================

echo "🚀 Démarrage du serveur Angular..."

# Vérifier si node_modules existe, sinon installer
if [ ! -d "node_modules" ]; then
    echo "📦 Installation des dépendances npm..."
    npm install
fi

# Vérifier si @angular/localize est installé
if ! npm list @angular/localize &> /dev/null; then
    echo "🌍 Installation de @angular/localize pour i18n..."
    npm install @angular/localize --save
fi

# Vérifier si Angular CLI est installé
if ! command -v ng &> /dev/null; then
    echo "⚙️  Installation d'Angular CLI..."
    npm install -g @angular/cli@17
fi

# Démarrer le serveur de développement Angular
echo "✅ Lancement de 'ng serve'..."
echo "📍 Application accessible sur: http://localhost:4200"
ng serve --host 0.0.0.0 --port 4200 --poll=2000 --disable-host-check