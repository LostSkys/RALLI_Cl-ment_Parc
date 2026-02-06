#!/bin/sh

# Script d'initialisation pour Angular

echo "======================================"
echo "Initialisation du frontend Angular..."
echo "======================================"

# Vérifier si node_modules existe
if [ ! -d "node_modules" ]; then
    echo "📦 Installation des dépendances npm..."
    npm install
else
    echo "✅ node_modules existe déjà"
fi

# Vérifier si Angular CLI est installé
if ! command -v ng &> /dev/null; then
    echo "📦 Installation d'Angular CLI..."
    npm install -g @angular/cli@17
else
    echo "✅ Angular CLI déjà installé"
fi

echo "======================================"
echo "🚀 Démarrage du serveur de développement Angular..."
echo "======================================"

# Démarrer Angular avec hot reload
ng serve --host 0.0.0.0 --poll 2000 --disable-host-check