#!/bin/bash

# ============================================
# SCRIPT DE DÉMARRAGE ROBUSTE
# Parc d'Attraction
# ============================================

set -e  # Arrêter en cas d'erreur

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     DÉMARRAGE DE L'APPLICATION PARC D'ATTRACTION          ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Couleurs pour l'affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher avec couleur
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo "ℹ️  $1"
}

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    print_error "Docker n'est pas installé!"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    print_error "Docker Compose n'est pas installé!"
    exit 1
fi

print_success "Docker et Docker Compose sont installés"
echo ""

# Arrêter les services existants
print_info "Arrêt des services existants..."
docker compose down 2>/dev/null || true
print_success "Services arrêtés"
echo ""

# Nettoyer les containers arrêtés
print_info "Nettoyage des containers arrêtés..."
docker container prune -f &>/dev/null || true
print_success "Nettoyage effectué"
echo ""

# Démarrer la base de données
print_info "Démarrage de la base de données..."
docker compose up -d database

# Attendre que la base soit healthy
print_info "Attente de la disponibilité de la base de données..."
MAX_ATTEMPTS=60
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    HEALTH_STATUS=$(docker compose ps database --format json | grep -o '"Health":"[^"]*"' | cut -d'"' -f4)
    
    if [ "$HEALTH_STATUS" = "healthy" ]; then
        print_success "Base de données prête!"
        break
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
    if [ $((ATTEMPT % 5)) -eq 0 ]; then
        print_info "Tentative $ATTEMPT/$MAX_ATTEMPTS..."
    fi
    sleep 2
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    print_error "La base de données n'a pas démarré correctement"
    print_info "Vérifiez les logs: docker compose logs database"
    exit 1
fi

echo ""

# Vérifier si la base est initialisée
print_info "Vérification de l'initialisation de la base..."
TABLE_COUNT=$(docker compose exec -T database mysql -u mysqlusr -pmysqlpwd -e "USE parc; SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'parc';" 2>/dev/null | tail -n 1)

if [ "$TABLE_COUNT" = "0" ] || [ -z "$TABLE_COUNT" ]; then
    print_warning "Base de données vide, initialisation nécessaire"
    NEED_INIT=true
else
    print_success "Base de données déjà initialisée ($TABLE_COUNT tables)"
    NEED_INIT=false
fi

echo ""

# Démarrer l'API
print_info "Démarrage de l'API Flask..."
docker compose up -d api

# Attendre que l'API soit prête
print_info "Attente de la disponibilité de l'API..."
ATTEMPT=0
MAX_ATTEMPTS=40

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if docker compose exec -T api python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" &>/dev/null; then
        print_success "API prête!"
        break
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
    if [ $((ATTEMPT % 5)) -eq 0 ]; then
        print_info "Tentative $ATTEMPT/$MAX_ATTEMPTS..."
    fi
    sleep 2
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    print_error "L'API n'a pas démarré correctement"
    print_info "Vérifiez les logs: docker compose logs api"
    exit 1
fi

echo ""

# Initialiser la base si nécessaire
if [ "$NEED_INIT" = true ]; then
    print_info "Initialisation de la base de données..."
    if docker compose exec -T api python3 init.py; then
        print_success "Base de données initialisée avec succès!"
    else
        print_error "Erreur lors de l'initialisation de la base"
        print_info "Vérifiez les logs: docker compose logs api"
        exit 1
    fi
    echo ""
fi

# Démarrer le frontend
print_info "Démarrage du frontend Angular..."
docker compose up -d web

# Attendre un peu pour Angular
print_info "Attente du démarrage Angular (peut prendre 30-60 secondes)..."
sleep 15
print_success "Frontend lancé"
echo ""

# Démarrer Nginx
print_info "Démarrage du reverse proxy Nginx..."
docker compose up -d nginx
sleep 5
print_success "Nginx démarré"
echo ""

# Vérification finale
print_info "Vérification finale des services..."
echo ""

# Vérifier chaque service
ALL_OK=true

# Database
if docker compose ps database | grep -q "Up"; then
    print_success "Database: En cours d'exécution"
else
    print_error "Database: Arrêté"
    ALL_OK=false
fi

# API
if docker compose ps api | grep -q "Up"; then
    print_success "API: En cours d'exécution"
    
    # Test de connexion
    if curl -s -f http://localhost:5000/ &>/dev/null; then
        print_success "API: Accessible sur http://localhost:5000/"
    else
        print_warning "API: Démarrée mais pas encore accessible (peut prendre quelques secondes)"
    fi
else
    print_error "API: Arrêté"
    ALL_OK=false
fi

# Web
if docker compose ps web | grep -q "Up"; then
    print_success "Frontend: En cours d'exécution"
else
    print_error "Frontend: Arrêté"
    ALL_OK=false
fi

# Nginx
if docker compose ps nginx | grep -q "Up"; then
    print_success "Nginx: En cours d'exécution"
else
    print_error "Nginx: Arrêté"
    ALL_OK=false
fi

echo ""

# Statistiques de la base
print_info "Contenu de la base de données:"
docker compose exec -T database mysql -u mysqlusr -pmysqlpwd -e "
USE parc;
SELECT 'Attractions' as Type, COUNT(*) as Total FROM attraction WHERE visible = 1
UNION ALL
SELECT 'Critiques', COUNT(*) FROM critique;
" 2>/dev/null || print_warning "Impossible de récupérer les statistiques"

echo ""

if [ "$ALL_OK" = true ]; then
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║              ✅ DÉMARRAGE RÉUSSI ✅                        ║"
    echo "╠═══════════════════════════════════════════════════════════╣"
    echo "║                                                           ║"
    echo "║  🌐 Application:  https://parcattraction/accueil          ║"
    echo "║  🔌 API:          https://api/                            ║"
    echo "║  💾 Database:     localhost:3306                          ║"
    echo "║                                                           ║"
    echo "║  📋 Logs:         docker compose logs -f                  ║"
    echo "║  🔄 Redémarrer:   docker compose restart                  ║"
    echo "║  ⏹️  Arrêter:      docker compose down                     ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
else
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║          ⚠️  DÉMARRAGE INCOMPLET ⚠️                        ║"
    echo "╠═══════════════════════════════════════════════════════════╣"
    echo "║                                                           ║"
    echo "║  Certains services n'ont pas démarré correctement.        ║"
    echo "║                                                           ║"
    echo "║  🔍 Vérifier l'état:  docker compose ps                   ║"
    echo "║  📋 Voir les logs:    docker compose logs                 ║"
    echo "║                                                           ║"
    echo "║  Consultez le GUIDE_DEPANNAGE.md pour plus d'aide        ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    exit 1
fi