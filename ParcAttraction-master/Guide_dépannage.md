# GUIDE D'INSTALLATION FINAL - PARC D'ATTRACTION

## SOLUTION COMPLÈTE EN 3 ÉTAPES

### Étape 1: Placer les Fichiers Corrigés

```powershell
# À la racine de votre projet
Copy-Item docker-compose-WORKING.yml docker-compose.yml -Force
Copy-Item start_app.py . -Force

# Frontend Angular (parc/)
Copy-Item Dockerfile.parc parc/Dockerfile -Force

# Nginx
Copy-Item default.conf.WORKING nginx/default.conf -Force
```

### Étape 2: Lancer le Script Magique

```powershell
python start_app.py
```

**C'est tout !** Le script va :
1.  Vérifier que Docker est installé et lancé
2.  Arrêter les anciens containers
3.  Build tous les containers
4.  Démarrer tous les services
5.  Attendre que la base soit prête
6.  Attendre que l'API soit prête
7.  Initialiser la base de données
8.  Attendre que le frontend soit prêt
9.  Afficher le statut
10.  Proposer d'ouvrir le navigateur

### Étape 3: Profiter !

Ouvrir le navigateur sur : **https://parcattraction/accueil**

---

## SI LE SCRIPT PYTHON NE FONCTIONNE PAS

### Méthode Manuelle (PowerShell)

```powershell
# 1. Arrêter tout
docker compose down

# 2. Supprimer les anciennes images (optionnel mais recommandé)
docker rmi app-python app-angular 2>$null

# 3. Build
docker compose build --no-cache

# 4. Démarrer
docker compose up -d

# 5. Attendre 30 secondes
Start-Sleep -Seconds 30

# 6. Vérifier la base
docker compose ps database
# Doit afficher "(healthy)"

# 7. Attendre encore 30 secondes pour l'API
Start-Sleep -Seconds 30

# 8. Initialiser la base
docker compose exec api python3 init.py

# 9. Attendre 60 secondes pour le frontend
Start-Sleep -Seconds 60

# 10. Vérifier tout
docker compose ps

# 11. Ouvrir le navigateur
start https://parcattraction/accueil
```

## VÉRIFICATIONS

### Vérifier que tout fonctionne

```powershell
# État des containers
docker compose ps

# Doit afficher:
# parc-database   Up (healthy)
# parc-backend    Up
# parc-frontend   Up
# parc-proxy      Up
```

### Tests Individuels

```powershell
# Test Database
docker compose exec database mysql -u mysqlusr -pmysqlpwd -e "SELECT COUNT(*) FROM parc.attraction;"

# Test API
curl http://localhost:5000/

# Test Frontend
curl http://localhost:4200/

# Test Nginx vers API
curl https://api/ -k

# Test Nginx vers Frontend
curl https://parcattraction/accueil -k
```

---

## EXPLICATIONS DES CORRECTIONS

### Problème 1: Frontend qui redémarre en boucle
**Cause:** Commande `chmod` dans docker-compose.yml sur Windows
**Solution:** Commande directe `["ng", "serve", ...]` sans script intermédiaire

### Problème 2: Dockerfile Angular manquant
**Cause:** Vous n'aviez que le Dockerfile Python
**Solution:** Création d'un Dockerfile optimisé pour Angular

### Problème 3: Timeouts Nginx trop courts
**Cause:** Angular prend du temps à compiler au premier démarrage
**Solution:** Timeouts augmentés à 300 secondes

### Problème 4: Build lent
**Cause:** npm install à chaque démarrage
**Solution:** npm install dans le Dockerfile + volume pour node_modules

---

## COMMANDES DE DÉPANNAGE

### Voir les Logs

```powershell
# Tous les services
docker compose logs -f

# Service spécifique
docker compose logs -f web
docker compose logs -f api
docker compose logs -f database
docker compose logs -f nginx

# Dernières 50 lignes
docker compose logs web --tail 50
```

### Redémarrer un Service

```powershell
docker compose restart web
docker compose restart api
docker compose restart nginx
```

### Entrer dans un Container

```powershell
# Frontend
docker compose exec web sh

# API
docker compose exec api sh

# Database
docker compose exec database bash

# Nginx
docker compose exec nginx sh
```

### Reset Complet

```powershell
# Tout arrêter et supprimer
docker compose down -v

# Rebuild from scratch
docker compose build --no-cache

# Redémarrer
docker compose up -d

# Attendre 2 minutes
Start-Sleep -Seconds 120

# Initialiser
docker compose exec api python3 init.py
```

---

## CHECKLIST POST-INSTALLATION

- [ ] `docker compose ps` affiche tous les services "Up"
- [ ] `curl http://localhost:5000/` retourne "Hello, Docker!"
- [ ] `curl http://localhost:4200/` retourne du HTML
- [ ] `docker compose exec database mysql -u mysqlusr -pmysqlpwd -e "SELECT COUNT(*) FROM parc.attraction;"` retourne 7
- [ ] https://parcattraction/accueil charge dans le navigateur
- [ ] Les attractions s'affichent
- [ ] Le bouton "Laisser un avis" ouvre le dialogue
- [ ] Le formulaire de critique fonctionne

---

## STRUCTURE FINALE DES FICHIERS

```
parc-attraction/
├── start_app.py                     NOUVEAU - Script magique
├── docker-compose.yml               REMPLACÉ
│
├── parc/
│   ├── Dockerfile                   NOUVEAU - Manquait !
│   ├── package.json                (existant)
│   ├── angular.json                (existant)
│   └── src/...
│
├── python/
│   ├── Dockerfile                  (existant, OK)
│   ├── docker-entrypoint.sh        (existant, OK)
│   ├── requirements.txt            (existant, OK)
│   ├── init.py                     (à créer si manquant)
│   └── ...
│
└── nginx/
    ├── default.conf                 REMPLACÉ
    └── ssl/
        ├── selfsigned.crt          (existant)
        └── selfsigned.key          (existant)
```

---

## LANCEMENT RAPIDE

**Version ultra courte:**

```powershell
# 1. Copier les fichiers
Copy-Item docker-compose-WORKING.yml docker-compose.yml -Force
Copy-Item Dockerfile.parc parc/Dockerfile -Force
Copy-Item default.conf.WORKING nginx/default.conf -Force
Copy-Item start_app.py . -Force

# 2. Lancer
python start_app.py

# 3. Attendre que le script finisse

# 4. Ouvrir
start https://parcattraction/accueil
```

---

## RÉSULTAT ATTENDU

Après le lancement du script, vous devriez voir :

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║                DÉMARRAGE RÉUSSI !                             ║
║                                                               ║
║     Temps écoulé: 2m 34s                                      ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

 URLS D'ACCÈS

   Application:  https://parcattraction/accueil
   API:          https://api/
   API directe:  http://localhost:5000/
   Frontend:     http://localhost:4200/
   Database:     localhost:3306
```

