#!/usr/bin/env python3
"""
Script de backup de la base de données
Crée un fichier SQL avec toutes les données
"""

import mariadb
import sys
from datetime import datetime

def backup_database():
    """Crée un backup complet de la base de données"""
    
    try:
        print("🔗 Connexion à la base de données...")
        conn = mariadb.connect(
            user="mysqlusr",
            password="mysqlpwd",
            host="database",
            port=3306,
            database="parc"
        )
        cur = conn.cursor()
        
        # Nom du fichier backup avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_parc_{timestamp}.sql"
        
        print(f"💾 Création du backup: {backup_file}")
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(f"-- Backup de la base de données 'parc'\n")
            f.write(f"-- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- ==========================================\n\n")
            
            # Backup des attractions
            f.write("-- TABLE: attraction\n")
            f.write("DELETE FROM critique;\n")
            f.write("DELETE FROM attraction;\n\n")
            
            cur.execute("SELECT * FROM attraction")
            attractions = cur.fetchall()
            
            if attractions:
                for attr in attractions:
                    f.write(f"INSERT INTO attraction (attraction_id, nom, description, difficulte, visible) VALUES ")
                    f.write(f"({attr[0]}, '{attr[1].replace(chr(39), chr(39)+chr(39))}', ")
                    f.write(f"'{attr[2].replace(chr(39), chr(39)+chr(39))}', {attr[3]}, {attr[4]});\n")
                f.write("\n")
            
            # Backup des critiques
            f.write("-- TABLE: critique\n")
            cur.execute("SELECT * FROM critique")
            critiques = cur.fetchall()
            
            if critiques:
                for crit in critiques:
                    nom = crit[1].replace("'", "''") if crit[1] else ''
                    prenom = crit[2].replace("'", "''") if crit[2] else ''
                    commentaire = crit[4].replace("'", "''") if crit[4] else ''
                    
                    f.write(f"INSERT INTO critique (attraction_id, nom, prenom, note, commentaire, est_anonyme) VALUES ")
                    f.write(f"({crit[0]}, '{nom}', '{prenom}', {crit[3]}, '{commentaire}', {crit[5]});\n")
                f.write("\n")
            
            # Backup des users
            f.write("-- TABLE: users\n")
            cur.execute("SELECT * FROM users")
            users = cur.fetchall()
            
            if users:
                for user in users:
                    email = user[3].replace("'", "''") if user[3] else ''
                    f.write(f"INSERT INTO users (user_id, name, password, email) VALUES ")
                    f.write(f"({user[0]}, '{user[1]}', '{user[2]}', '{email}');\n")
        
        cur.close()
        conn.close()
        
        print(f"✅ Backup créé avec succès: {backup_file}")
        print(f"\n📋 Statistiques:")
        print(f"   - {len(attractions)} attractions")
        print(f"   - {len(critiques)} critiques")
        print(f"   - {len(users)} utilisateurs")
        
        return backup_file
        
    except mariadb.Error as e:
        print(f"❌ Erreur MariaDB: {e}")
        return None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def restore_from_backup(backup_file):
    """Restaure la base de données depuis un fichier backup"""
    
    try:
        print(f"🔗 Connexion à la base de données...")
        conn = mariadb.connect(
            user="mysqlusr",
            password="mysqlpwd",
            host="database",
            port=3306,
            database="parc"
        )
        cur = conn.cursor()
        
        print(f"📂 Lecture du fichier: {backup_file}")
        with open(backup_file, 'r', encoding='utf-8') as f:
            sql_commands = f.read()
        
        # Exécuter les commandes SQL
        print("⚙️  Restauration en cours...")
        for command in sql_commands.split(';'):
            command = command.strip()
            if command and not command.startswith('--'):
                try:
                    cur.execute(command)
                except mariadb.Error as e:
                    print(f"⚠️  Erreur sur commande: {e}")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("✅ Restauration terminée!")
        return True
        
    except mariadb.Error as e:
        print(f"❌ Erreur MariaDB: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {backup_file}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        if len(sys.argv) < 3:
            print("Usage: python3 backup.py restore <fichier_backup.sql>")
            sys.exit(1)
        restore_from_backup(sys.argv[2])
    else:
        backup_database()