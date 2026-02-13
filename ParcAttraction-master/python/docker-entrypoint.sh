#!/bin/bash
set -e

echo "🐍 Démarrage de l'API Flask..."

# Fonction pour attendre MariaDB
wait_for_mariadb() {
    echo "⏳ Attente de MariaDB (database:3306)..."
    
    local max_attempts=60
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if python3 -c "
import mariadb
import sys
try:
    conn = mariadb.connect(
        user='mysqlusr',
        password='mysqlpwd',
        host='database',
        port=3306,
        database='parc'
    )
    conn.close()
    sys.exit(0)
except Exception as e:
    sys.exit(1)
" 2>/dev/null; then
            echo "✅ MariaDB est prêt!"
            return 0
        fi
        
        attempt=$((attempt + 1))
        if [ $((attempt % 10)) -eq 0 ]; then
            echo "   Tentative $attempt/$max_attempts..."
        fi
        sleep 2
    done
    
    echo "❌ Impossible de se connecter à MariaDB après $max_attempts tentatives"
    return 1
}

# Attendre que MariaDB soit prêt
if ! wait_for_mariadb; then
    exit 1
fi

# Vérifier si la base de données est initialisée
echo "🔍 Vérification de la base de données..."
TABLE_COUNT=$(python3 -c "
import mariadb
try:
    conn = mariadb.connect(user='mysqlusr', password='mysqlpwd', host='database', port=3306, database='parc')
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = \"parc\"')
    count = cur.fetchone()[0]
    print(count)
except:
    print(0)
" 2>/dev/null)

if [ "$TABLE_COUNT" = "0" ] || [ -z "$TABLE_COUNT" ]; then
    echo "⚠️  Base de données vide, initialisation..."
    if [ -f "init.py" ]; then
        python3 init.py || echo "⚠️  Erreur lors de l'initialisation (peut-être déjà fait)"
    else
        echo "⚠️  Fichier init.py non trouvé"
    fi
else
    echo "✅ Base de données déjà initialisée ($TABLE_COUNT tables)"
fi

echo ""
echo "🚀 Démarrage du serveur Flask..."
echo ""

# Démarrer Flask
exec python3 -m flask --debug run --host=0.0.0.0