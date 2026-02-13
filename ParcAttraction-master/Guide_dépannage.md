# 🚨 GUIDE DE DÉPANNAGE - PARC D'ATTRACTION

## 🎯 Problèmes Courants et Solutions

---

## Problème 1: Bad Gateway (502)

### Symptômes
- Le site affiche "502 Bad Gateway"
- Impossible d'accéder à https://parcattraction

### Diagnostic

```bash
# 1. Vérifier l'état des containers
docker compose ps

# Tous les services doivent être "Up" et "healthy"
```

### Solutions

#### Solution A: Redémarrer dans le bon ordre

```bash
# 1. Arrêter tout
docker compose down

# 2. Démarrer la base d'abord
docker compose up -d database

# 3. Attendre que la BDD soit healthy (30-60 secondes)
docker compose ps database
# Doit afficher "(healthy)"

# 4. Démarrer l'API
docker compose up -d api

# 5. Attendre que l'API soit healthy (20-30 secondes)
docker compose ps api
# Doit afficher "(healthy)"

# 6. Démarrer le frontend
docker compose up -d web

# 7. Attendre 10 secondes puis démarrer nginx
sleep 10
docker compose up -d nginx

# 8. Vérifier
docker compose ps
```

#### Solution B: Vérifier les logs

```bash
# Logs de nginx (si erreur de proxy)
docker compose logs nginx | tail -50

# Logs de l'API (si erreur backend)
docker compose logs api | tail -50

# Logs du frontend (si erreur Angular)
docker compose logs web | tail -50
```

#### Solution C: Rebuild complet

```bash
# Arrêter et supprimer tout (SAUF les volumes de données)
docker compose down

# Rebuild les images
docker compose build --no-cache

# Redémarrer
docker compose up -d

# Suivre les logs
docker compose logs -f
```

---

## Problème 2: Base de Données Vide

### Symptômes
- Aucune attraction n'apparaît
- Page blanche ou erreurs 404
- API retourne `[]`

### Diagnostic

```bash
# Se connecter à la base
docker compose exec database mysql -u mysqlusr -pmysqlpwd parc

# Dans MySQL, vérifier:
SHOW TABLES;
SELECT COUNT(*) FROM attraction;
SELECT COUNT(*) FROM critique;
EXIT;
```

### Solutions

#### Solution A: Réinitialiser avec init.py

```bash
# 1. Se connecter au container API
docker compose exec api sh

# 2. Lancer le script d'initialisation
python3 init.py

# 3. Sortir
exit

# 4. Redémarrer l'API
docker compose restart api
```

**⚠️ ATTENTION: Cette solution SUPPRIME toutes les données existantes!**

#### Solution B: Restaurer depuis un backup

Si vous avez fait un backup avant:

```bash
# 1. Lister les backups disponibles
docker compose exec api ls -la backup_*.sql

# 2. Restaurer (remplacer par le bon nom de fichier)
docker compose exec api python3 backup.py restore backup_parc_20260206_153000.sql

# 3. Redémarrer
docker compose restart api
```

#### Solution C: Insertion manuelle SQL

```bash
# Se connecter à la base
docker compose exec database mysql -u mysqlusr -pmysqlpwd parc

# Copier-coller ce SQL:
```

```sql
-- Insérer les attractions
INSERT INTO attraction (nom, description, difficulte, visible) VALUES 
('Silver Star', 'Une montagne russe mythique avec des loopings vertigineux.', 4, 1),
('Le Condor', 'Une chute libre spectaculaire de 100 mètres.', 5, 1),
('Le Carrousel', 'Manège traditionnel pour les plus petits.', 1, 1),
('Space Mountain', 'Voyage dans les étoiles à toute vitesse.', 4, 1),
('Le Petit Train', 'Balade tranquille à travers le parc.', 1, 1);

-- Insérer quelques critiques
INSERT INTO critique (attraction_id, nom, prenom, note, commentaire, est_anonyme) VALUES 
(1, 'Dupont', 'Marie', 5, 'Incroyable! Les sensations sont au rendez-vous.', 0),
(1, 'Anonyme', '', 5, 'Meilleure attraction du parc!', 1),
(2, 'Bernard', 'Sophie', 5, 'J\'ai adoré la chute libre!', 0);

-- Vérifier
SELECT COUNT(*) FROM attraction;
SELECT COUNT(*) FROM critique;
EXIT;
```

---

## 🛡️ PROCÉDURE DE SECOURS COMPLÈTE

### Avant toute manipulation: FAIRE UN BACKUP!

```bash
# Se connecter au container API
docker compose exec api sh

# Créer un backup
python3 backup.py

# Le fichier sera créé: backup_parc_YYYYMMDD_HHMMSS.sql
# Noter le nom du fichier!

# Sortir
exit
```

### Reset Total avec Sauvegarde

```bash
# 1. BACKUP (IMPORTANT!)
docker compose exec api python3 backup.py

# 2. Arrêter tout
docker compose down

# 3. Supprimer le volume de données (⚠️ PERTE DE DONNÉES!)
docker volume rm parc_database_data

# 4. Recréer tout
docker compose up -d

# 5. Attendre 60 secondes que tout démarre
sleep 60

# 6. Vérifier
docker compose ps
# Tous doivent être "Up" ou "(healthy)"

# 7. Initialiser la base
docker compose exec api python3 init.py

# 8. Vérifier que ça fonctionne
curl https://api/attraction/visible
```

### Restaurer un Backup

```bash
# 1. Copier le fichier backup dans le container (si nécessaire)
docker cp backup_parc_20260206_153000.sql parc-backend:/var/www/html/back/

# 2. Restaurer
docker compose exec api python3 backup.py restore backup_parc_20260206_153000.sql

# 3. Redémarrer l'API
docker compose restart api

# 4. Vérifier
docker compose exec api sh -c "python3 -c \"
import mariadb
conn = mariadb.connect(user='mysqlusr', password='mysqlpwd', host='database', port=3306, database='parc')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM attraction')
print('Attractions:', cur.fetchone()[0])
cur.execute('SELECT COUNT(*) FROM critique')
print('Critiques:', cur.fetchone()[0])
\""
```

---

## 🔍 Diagnostic Rapide

### Script de diagnostic automatique

Créez un fichier `diagnostic.sh`:

```bash
#!/bin/bash

echo "🔍 DIAGNOSTIC DU SYSTÈME"
echo "========================"
echo ""

echo "📦 État des containers:"
docker compose ps
echo ""

echo "🗄️ Volume de données:"
docker volume ls | grep parc
echo ""

echo "🌐 Réseau:"
docker network ls | grep parc
echo ""

echo "💾 Base de données:"
docker compose exec database mysql -u mysqlusr -pmysqlpwd -e "
USE parc;
SELECT 'Attractions' as Table_Name, COUNT(*) as Count FROM attraction
UNION ALL
SELECT 'Critiques', COUNT(*) FROM critique
UNION ALL
SELECT 'Users', COUNT(*) FROM users;
"
echo ""

echo "🔗 Connectivité API:"
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:5000/ || echo "❌ API non accessible"
echo ""

echo "🔗 Connectivité Frontend:"
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:4200/ || echo "❌ Frontend non accessible"
echo ""

echo "📋 Logs récents (API):"
docker compose logs api | tail -10
echo ""

echo "✅ Diagnostic terminé"
```

Puis:
```bash
chmod +x diagnostic.sh
./diagnostic.sh
```

---

## 🆘 Checklist de Dépannage

Quand quelque chose ne fonctionne pas, suivez cette checklist:

- [ ] **Étape 1**: `docker compose ps` - Tous les services sont "Up"?
- [ ] **Étape 2**: `docker compose ps database` - Database est "(healthy)"?
- [ ] **Étape 3**: `docker compose ps api` - API est "(healthy)"?
- [ ] **Étape 4**: `docker compose logs api | tail -30` - Pas d'erreurs Python?
- [ ] **Étape 5**: `docker compose logs web | tail -30` - Pas d'erreurs Angular?
- [ ] **Étape 6**: `curl http://localhost:5000/` - API répond?
- [ ] **Étape 7**: `curl http://localhost:4200/` - Frontend répond?
- [ ] **Étape 8**: Vérifier la base de données (voir ci-dessus)
- [ ] **Étape 9**: Si tout est OK mais 502: redémarrer nginx `docker compose restart nginx`

---

## 🚀 Redémarrage Propre (Procédure Recommandée)

Cette procédure garantit un démarrage sans problème:

```bash
# 1. Créer un backup (par sécurité)
docker compose exec api python3 backup.py 2>/dev/null || echo "Pas de backup possible"

# 2. Arrêter proprement
docker compose down

# 3. Vérifier que tout est arrêté
docker compose ps
# Doit être vide

# 4. Démarrer la base seule
docker compose up -d database

# 5. Attendre 30 secondes
echo "⏳ Attente démarrage base de données..."
sleep 30

# 6. Vérifier que la base est healthy
docker compose ps database

# 7. Si healthy, démarrer l'API
docker compose up -d api

# 8. Attendre 20 secondes
echo "⏳ Attente démarrage API..."
sleep 20

# 9. Vérifier l'API
docker compose ps api
docker compose logs api | tail -10

# 10. Démarrer le reste
docker compose up -d

# 11. Vérification finale
echo "⏳ Attente finale..."
sleep 10
docker compose ps

# 12. Test
curl http://localhost:5000/
echo ""
echo "✅ Si vous voyez 'Hello, Docker!' ci-dessus, tout fonctionne!"
```

---

## 📝 Logs Utiles

### Voir les logs en temps réel

```bash
# Tous les services
docker compose logs -f

# Un service spécifique
docker compose logs -f api
docker compose logs -f web
docker compose logs -f database
docker compose logs -f nginx

# Filtrer les erreurs
docker compose logs api | grep -i error
docker compose logs api | grep -i exception
```

### Sauvegarder les logs

```bash
# Logs complets dans un fichier
docker compose logs > logs_$(date +%Y%m%d_%H%M%S).txt

# Logs d'un service
docker compose logs api > logs_api_$(date +%Y%m%d_%H%M%S).txt
```

---

## 🔐 Accès Direct aux Services

### Se connecter aux containers

```bash
# Container API (Python)
docker compose exec api sh

# Container Frontend (Node.js)
docker compose exec web sh

# Container Database (MariaDB)
docker compose exec database bash

# Container Nginx
docker compose exec nginx sh
```

### Commandes utiles dans les containers

**Dans le container API:**
```bash
# Vérifier les fichiers Python
ls -la *.py

# Tester la connexion BDD
python3 -c "import mariadb; conn = mariadb.connect(user='mysqlusr', password='mysqlpwd', host='database', port=3306, database='parc'); print('✅ Connexion OK')"

# Lancer init.py
python3 init.py

# Créer un backup
python3 backup.py
```

**Dans le container Frontend:**
```bash
# Vérifier Angular CLI
ng version

# Rebuild
npm install
```

**Dans le container Database:**
```bash
# Se connecter à MySQL
mysql -u mysqlusr -p
# Password: mysqlpwd

# Vérifier les tables
mysql -u mysqlusr -pmysqlpwd -e "USE parc; SHOW TABLES;"
```

---

## 🎓 Comprendre les Erreurs Courantes

### "Connection refused" ou "Network error"
**Cause**: Un service n'est pas démarré ou pas encore prêt  
**Solution**: Attendre que le healthcheck passe à "healthy"

### "502 Bad Gateway"
**Cause**: Nginx ne peut pas joindre le backend/frontend  
**Solution**: Vérifier que web et api sont "Up", redémarrer nginx

### "Cannot connect to database"
**Cause**: La base n'est pas prête ou mot de passe incorrect  
**Solution**: Attendre que database soit "(healthy)", vérifier .env

### "Table doesn't exist"
**Cause**: Base de données non initialisée  
**Solution**: Lancer `python3 init.py` dans le container api

### "Permission denied" 
**Cause**: Problème de droits sur les fichiers  
**Solution**: `chmod +x init-angular.sh docker-entrypoint.sh`

---

## 📞 Dernière Option: Reset Total

Si rien ne fonctionne, reset complet:

```bash
# 1. BACKUP (si possible)
docker compose exec api python3 backup.py

# 2. Tout arrêter et supprimer
docker compose down -v
docker system prune -a --volumes

# 3. Reconstruire depuis zéro
docker compose build --no-cache
docker compose up -d

# 4. Attendre 2 minutes
sleep 120

# 5. Initialiser
docker compose exec api python3 init.py

# 6. Vérifier
docker compose ps
curl http://localhost:5000/
```

---

**💡 Conseil**: Créez des backups réguliers avec `docker compose exec api python3 backup.py`