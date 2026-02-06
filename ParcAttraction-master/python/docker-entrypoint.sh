#!/bin/bash

# Script d'initialisation pour Flask

echo "======================================"
echo "Initialisation du backend Flask..."
echo "======================================"

# Attendre que la base de données soit prête
echo "⏳ Attente de la base de données..."
until python3 -c "import mariadb; mariadb.connect(user='mysqlusr', password='mysqlpwd', host='database', port=3306, database='parc')" 2>/dev/null; do
    echo "Base de données non prête, nouvelle tentative dans 2s..."
    sleep 2
done

echo "✅ Base de données prête!"

# Initialiser la base de données si besoin
if [ -f "init.py" ]; then
    echo "🔧 Exécution du script d'initialisation..."
    python3 init.py || echo "⚠️  Initialisation déjà effectuée ou erreur"
fi

echo "======================================"
echo "🚀 Démarrage du serveur Flask..."
echo "======================================"

# Démarrer Flask en mode debug
exec python3 -m flask --debug run --host=0.0.0.0