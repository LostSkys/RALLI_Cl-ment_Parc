#!/usr/bin/env python3
"""
🚀 SCRIPT DE LANCEMENT AUTOMATIQUE - PARC D'ATTRACTION
Ce script fait TOUT automatiquement !
"""

import subprocess
import time
import sys
import os
import platform
import webbrowser
from datetime import datetime

# Couleurs pour Windows et Linux
if platform.system() == 'Windows':
    os.system('color')

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_color(text, color=Colors.WHITE):
    print(f"{color}{text}{Colors.RESET}")

def print_header(text):
    print_color(f"\n{'='*60}", Colors.CYAN)
    print_color(f"  {text}", Colors.BOLD + Colors.CYAN)
    print_color(f"{'='*60}\n", Colors.CYAN)

def run_command(command, show_output=True, timeout=None):
    """Exécute une commande et retourne True si succès"""
    try:
        if show_output:
            result = subprocess.run(command, shell=True, check=True, timeout=timeout)
            return result.returncode == 0
        else:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=timeout
            )
            return result.returncode == 0
    except subprocess.TimeoutExpired:
        print_color(f"⏱️  Timeout dépassé pour: {command}", Colors.YELLOW)
        return False
    except subprocess.CalledProcessError:
        return False
    except Exception as e:
        print_color(f"❌ Erreur: {e}", Colors.RED)
        return False

def check_docker():
    """Vérifie que Docker est installé et lancé"""
    print_header("🐳 VÉRIFICATION DOCKER")
    
    if not run_command("docker --version", show_output=False):
        print_color("❌ Docker n'est pas installé !", Colors.RED)
        print_color("   Installez Docker Desktop depuis: https://www.docker.com/products/docker-desktop", Colors.YELLOW)
        return False
    
    print_color("✅ Docker est installé", Colors.GREEN)
    
    if not run_command("docker ps", show_output=False):
        print_color("❌ Docker n'est pas lancé !", Colors.RED)
        print_color("   Lancez Docker Desktop et réessayez", Colors.YELLOW)
        return False
    
    print_color("✅ Docker est actif", Colors.GREEN)
    return True

def stop_containers():
    """Arrête tous les containers existants"""
    print_header("🛑 ARRÊT DES CONTAINERS EXISTANTS")
    
    run_command("docker compose down", show_output=False)
    time.sleep(2)
    print_color("✅ Containers arrêtés", Colors.GREEN)

def build_containers():
    """Build tous les containers"""
    print_header("🔨 BUILD DES CONTAINERS")
    
    print_color("📦 Build du backend Python...", Colors.CYAN)
    if not run_command("docker compose build api"):
        print_color("❌ Erreur lors du build de l'API", Colors.RED)
        return False
    
    print_color("📦 Build du frontend Angular...", Colors.CYAN)
    if not run_command("docker compose build web"):
        print_color("❌ Erreur lors du build du frontend", Colors.RED)
        return False
    
    print_color("✅ Tous les containers sont buildés", Colors.GREEN)
    return True

def start_containers():
    """Démarre tous les containers"""
    print_header("🚀 DÉMARRAGE DES CONTAINERS")
    
    if not run_command("docker compose up -d"):
        print_color("❌ Erreur lors du démarrage", Colors.RED)
        return False
    
    print_color("✅ Containers démarrés", Colors.GREEN)
    return True

def wait_for_database():
    """Attend que la base de données soit prête"""
    print_header("⏳ ATTENTE DE LA BASE DE DONNÉES")
    
    max_attempts = 30
    for i in range(max_attempts):
        result = subprocess.run(
            "docker compose exec -T database mariadb-admin ping -h localhost -u mysqlusr -pmysqlpwd",
            shell=True,
            capture_output=True
        )
        
        if result.returncode == 0:
            print_color(f"✅ Base de données prête ! (après {i+1} tentatives)", Colors.GREEN)
            return True
        
        if (i + 1) % 5 == 0:
            print_color(f"   Tentative {i+1}/{max_attempts}...", Colors.YELLOW)
        
        time.sleep(2)
    
    print_color("❌ La base de données n'a pas démarré", Colors.RED)
    return False

def wait_for_api():
    """Attend que l'API soit prête"""
    print_header("⏳ ATTENTE DE L'API")
    
    max_attempts = 40
    for i in range(max_attempts):
        try:
            import urllib.request
            response = urllib.request.urlopen('http://localhost:5000/', timeout=2)
            if response.status == 200:
                print_color(f"✅ API prête ! (après {i+1} tentatives)", Colors.GREEN)
                return True
        except:
            pass
        
        if (i + 1) % 5 == 0:
            print_color(f"   Tentative {i+1}/{max_attempts}...", Colors.YELLOW)
        
        time.sleep(2)
    
    print_color("❌ L'API n'a pas démarré", Colors.RED)
    return False

def initialize_database():
    """Initialise la base de données"""
    print_header("💾 INITIALISATION DE LA BASE DE DONNÉES")
    
    # Vérifier si init.py existe
    result = subprocess.run(
        "docker compose exec -T api test -f init.py",
        shell=True,
        capture_output=True
    )
    
    if result.returncode != 0:
        print_color("⚠️  Fichier init.py non trouvé, initialisation ignorée", Colors.YELLOW)
        return True
    
    # Lancer init.py
    print_color("🔄 Exécution de init.py...", Colors.CYAN)
    if run_command("docker compose exec -T api python3 init.py"):
        print_color("✅ Base de données initialisée", Colors.GREEN)
        return True
    else:
        print_color("⚠️  Erreur lors de l'initialisation (peut-être déjà fait)", Colors.YELLOW)
        return True  # On continue quand même

def wait_for_frontend():
    """Attend que le frontend soit prêt"""
    print_header("⏳ ATTENTE DU FRONTEND ANGULAR")
    
    print_color("   Angular prend 60-90 secondes à démarrer...", Colors.YELLOW)
    
    max_attempts = 60
    for i in range(max_attempts):
        try:
            import urllib.request
            response = urllib.request.urlopen('http://localhost:4200/', timeout=2)
            if response.status == 200:
                print_color(f"✅ Frontend prêt ! (après {i+1} tentatives)", Colors.GREEN)
                return True
        except:
            pass
        
        if (i + 1) % 10 == 0:
            print_color(f"   Tentative {i+1}/{max_attempts}...", Colors.YELLOW)
        
        time.sleep(2)
    
    print_color("⚠️  Le frontend n'a pas répondu, mais on continue...", Colors.YELLOW)
    return True  # On continue quand même

def check_status():
    """Affiche le statut de tous les services"""
    print_header("📊 STATUT DES SERVICES")
    
    run_command("docker compose ps")

def show_urls():
    """Affiche les URLs d'accès"""
    print_header("🌐 URLS D'ACCÈS")
    
    print_color("  📱 Application:  https://parcattraction/accueil", Colors.GREEN + Colors.BOLD)
    print_color("  🔌 API:          https://api/", Colors.GREEN)
    print_color("  🔌 API directe:  http://localhost:5000/", Colors.GREEN)
    print_color("  💻 Frontend:     http://localhost:4200/", Colors.GREEN)
    print_color("  💾 Database:     localhost:3306", Colors.GREEN)
    print_color("\n  🔑 Credentials Database:", Colors.CYAN)
    print_color("     User: mysqlusr", Colors.WHITE)
    print_color("     Password: mysqlpwd", Colors.WHITE)
    print_color("     Database: parc", Colors.WHITE)

def open_browser():
    """Ouvre le navigateur sur l'application"""
    print_header("🌍 OUVERTURE DU NAVIGATEUR")
    
    try:
        webbrowser.open('https://parcattraction/accueil')
        print_color("✅ Navigateur ouvert !", Colors.GREEN)
        print_color("\n   ⚠️  Si erreur SSL, cliquez sur 'Paramètres avancés'", Colors.YELLOW)
        print_color("      puis 'Continuer vers le site'", Colors.YELLOW)
    except Exception as e:
        print_color(f"⚠️  Impossible d'ouvrir le navigateur: {e}", Colors.YELLOW)
        print_color("   Ouvrez manuellement: https://parcattraction/accueil", Colors.CYAN)

def show_logs_info():
    """Affiche les commandes pour voir les logs"""
    print_header("📋 COMMANDES UTILES")
    
    print_color("  Voir tous les logs:", Colors.CYAN)
    print_color("    docker compose logs -f", Colors.WHITE)
    print_color("\n  Voir les logs d'un service:", Colors.CYAN)
    print_color("    docker compose logs -f api", Colors.WHITE)
    print_color("    docker compose logs -f web", Colors.WHITE)
    print_color("    docker compose logs -f database", Colors.WHITE)
    print_color("\n  Redémarrer un service:", Colors.CYAN)
    print_color("    docker compose restart api", Colors.WHITE)
    print_color("\n  Arrêter tout:", Colors.CYAN)
    print_color("    docker compose down", Colors.WHITE)

def main():
    """Fonction principale"""
    
    print_color("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     🎢  PARC D'ATTRACTION - LANCEMENT AUTOMATIQUE  🎢          ║
║                                                               ║
║     Ce script va tout faire pour vous !                       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """, Colors.MAGENTA + Colors.BOLD)
    
    start_time = time.time()
    
    # Étape 1: Vérifier Docker
    if not check_docker():
        sys.exit(1)
    
    # Étape 2: Arrêter les containers existants
    stop_containers()
    
    # Étape 3: Build
    if not build_containers():
        print_color("\n❌ Erreur lors du build. Consultez les logs ci-dessus.", Colors.RED)
        sys.exit(1)
    
    # Étape 4: Démarrer
    if not start_containers():
        print_color("\n❌ Erreur lors du démarrage. Consultez les logs ci-dessus.", Colors.RED)
        sys.exit(1)
    
    # Étape 5: Attendre la base de données
    if not wait_for_database():
        print_color("\n⚠️  Problème avec la base de données", Colors.YELLOW)
        check_status()
        sys.exit(1)
    
    # Étape 6: Attendre l'API
    if not wait_for_api():
        print_color("\n⚠️  Problème avec l'API", Colors.YELLOW)
        check_status()
        sys.exit(1)
    
    # Étape 7: Initialiser la base
    initialize_database()
    
    # Étape 8: Attendre le frontend
    wait_for_frontend()
    
    # Étape 9: Afficher le statut
    check_status()
    
    # Étape 10: Calculer le temps écoulé
    elapsed_time = int(time.time() - start_time)
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    
    # Succès !
    print_color(f"""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              ✅  DÉMARRAGE RÉUSSI ! ✅                         ║
║                                                               ║
║     Temps écoulé: {minutes}m {seconds}s                                         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """, Colors.GREEN + Colors.BOLD)
    
    show_urls()
    show_logs_info()
    
    # Demander si on ouvre le navigateur
    print()
    try:
        choice = input(f"{Colors.CYAN}Ouvrir le navigateur maintenant ? (o/N): {Colors.RESET}").lower()
        if choice == 'o' or choice == 'oui':
            open_browser()
    except:
        pass
    
    print_color("\n🎉 L'application est prête ! Bon développement !", Colors.GREEN + Colors.BOLD)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_color("\n\n⚠️  Interruption par l'utilisateur", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        print_color(f"\n❌ Erreur inattendue: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1) 