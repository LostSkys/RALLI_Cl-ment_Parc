#!/usr/bin/env python3
"""
Script d'initialisation de la base de données
Crée les tables et insère les données de test
"""

import mariadb
import sys
import time

def wait_for_db(max_attempts=30):
    """Attend que la base de données soit disponible"""
    print("⏳ Attente de la disponibilité de la base de données...")
    
    for attempt in range(max_attempts):
        try:
            conn = mariadb.connect(
                user="mysqlusr",
                password="mysqlpwd",
                host="database",
                port=3306,
                database="parc"
            )
            conn.close()
            print("✅ Base de données disponible!")
            return True
        except mariadb.Error as e:
            print(f"Tentative {attempt + 1}/{max_attempts}: {e}")
            time.sleep(2)
    
    print("❌ Impossible de se connecter à la base de données")
    return False

def init_database():
    """Initialise la base de données avec les tables et données"""
    
    if not wait_for_db():
        sys.exit(1)
    
    try:
        # Connexion
        print("\n🔗 Connexion à la base de données...")
        conn = mariadb.connect(
            user="mysqlusr",
            password="mysqlpwd",
            host="database",
            port=3306,
            database="parc"
        )
        cur = conn.cursor()
        print("✅ Connecté!")
        
        # Suppression des tables existantes
        print("\n🗑️  Suppression des tables existantes...")
        cur.execute("DROP TABLE IF EXISTS critique")
        cur.execute("DROP TABLE IF EXISTS attraction")
        cur.execute("DROP TABLE IF EXISTS users")
        print("✅ Tables supprimées")
        
        # Création de la table users
        print("\n📋 Création de la table 'users'...")
        cur.execute("""
            CREATE TABLE users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✅ Table 'users' créée")
        
        # Création de la table attraction
        print("\n📋 Création de la table 'attraction'...")
        cur.execute("""
            CREATE TABLE attraction (
                attraction_id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(255) NOT NULL,
                description TEXT,
                difficulte INT NOT NULL CHECK (difficulte BETWEEN 1 AND 5),
                visible TINYINT(1) DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_visible (visible),
                INDEX idx_difficulte (difficulte)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✅ Table 'attraction' créée")
        
        # Création de la table critique
        print("\n📋 Création de la table 'critique'...")
        cur.execute("""
            CREATE TABLE critique (
                critique_id INT AUTO_INCREMENT PRIMARY KEY,
                attraction_id INT NOT NULL,
                nom VARCHAR(255),
                prenom VARCHAR(255),
                note INT NOT NULL CHECK (note BETWEEN 1 AND 5),
                commentaire TEXT,
                est_anonyme BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_attraction 
                    FOREIGN KEY (attraction_id) 
                    REFERENCES attraction(attraction_id) 
                    ON DELETE CASCADE 
                    ON UPDATE CASCADE,
                INDEX idx_attraction_id (attraction_id),
                INDEX idx_note (note),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        print("✅ Table 'critique' créée")
        
        # Insertion de l'utilisateur admin
        print("\n👤 Insertion de l'utilisateur administrateur...")
        cur.execute("""
            INSERT INTO users (name, password, email) 
            VALUES ('admin', 'admin123', 'admin@parcattraction.com')
        """)
        print("✅ Utilisateur admin créé (login: admin, password: admin123)")
        
        # Insertion des attractions
        print("\n🎢 Insertion des attractions...")
        attractions = [
            ('Silver Star', 'Une montagne russe mythique avec des loopings vertigineux et une chute de 73 mètres.', 4, 1),
            ('Le Condor', 'Une chute libre spectaculaire de 100 mètres de hauteur. Sensations fortes garanties!', 5, 1),
            ('Le Carrousel', 'Manège traditionnel pour les plus petits. Douceur et musique d\'antan.', 1, 1),
            ('Maintenance Express', 'Attraction actuellement en maintenance - NE PAS AFFICHER', 3, 0),
            ('Space Mountain', 'Voyage dans les étoiles à toute vitesse dans le noir complet.', 4, 1),
            ('Le Petit Train', 'Balade tranquille à travers le parc pour découvrir les coulisses.', 1, 1),
            ('Le Manoir Hanté', 'Parcours terrifiant dans une maison hantée. Âmes sensibles s\'abstenir!', 4, 0),
        ]
        
        for attraction in attractions:
            cur.execute("""
                INSERT INTO attraction (nom, description, difficulte, visible) 
                VALUES (?, ?, ?, ?)
            """, attraction)
        
        print(f"✅ {len(attractions)} attractions insérées")
        
        # Insertion de critiques de test
        print("\n💬 Insertion de critiques de test...")
        critiques = [
            (1, 'Dupont', 'Marie', 5, 'Incroyable! Les sensations sont au rendez-vous. Une attraction à ne pas manquer!', 0),
            (1, 'Martin', 'Jean', 4, 'Très bien mais un peu d\'attente. L\'attraction en elle-même est top!', 0),
            (1, 'Anonyme', '', 5, 'Meilleure attraction du parc sans hésitation!', 1),
            (2, 'Bernard', 'Sophie', 5, 'J\'ai adoré la chute libre! Mon cœur bat encore!', 0),
            (2, 'Anonyme', '', 3, 'Trop intense pour moi, mais bien pour les amateurs de sensations fortes.', 1),
            (3, 'Petit', 'Lucas', 5, 'Mon fils de 4 ans a adoré! Parfait pour les enfants.', 0),
            (5, 'Rousseau', 'Emma', 5, 'Space Mountain est toujours aussi magique après toutes ces années!', 0),
            (5, 'Anonyme', '', 4, 'Super attraction mais la file d\'attente était très longue.', 1),
            (6, 'Lefebvre', 'Pierre', 4, 'Balade agréable et reposante entre deux attractions à sensations.', 0),
        ]
        
        for critique in critiques:
            cur.execute("""
                INSERT INTO critique (attraction_id, nom, prenom, note, commentaire, est_anonyme) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, critique)
        
        print(f"✅ {len(critiques)} critiques insérées")
        
        # Commit
        conn.commit()
        print("\n✅ Toutes les modifications ont été enregistrées!")
        
        # Vérification
        print("\n📊 Vérification des données...")
        cur.execute("SELECT COUNT(*) FROM attraction")
        nb_attractions = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM attraction WHERE visible = 1")
        nb_visibles = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM critique")
        nb_critiques = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM users")
        nb_users = cur.fetchone()[0]
        
        print(f"""
╔════════════════════════════════════════╗
║        INITIALISATION TERMINÉE         ║
╠════════════════════════════════════════╣
║ Attractions totales    : {nb_attractions:>13} ║
║ Attractions visibles   : {nb_visibles:>13} ║
║ Attractions masquées   : {nb_attractions - nb_visibles:>13} ║
║ Critiques              : {nb_critiques:>13} ║
║ Utilisateurs           : {nb_users:>13} ║
╚════════════════════════════════════════╝
        """)
        
        # Fermeture
        cur.close()
        conn.close()
        
        print("\n🎉 Base de données prête à l'emploi!")
        print("\n📝 Credentials:")
        print("   Admin: login='admin', password='admin123'")
        print("   Database: user='mysqlusr', password='mysqlpwd', db='parc'")
        
        return True
        
    except mariadb.Error as e:
        print(f"\n❌ Erreur MariaDB: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║     SCRIPT D'INITIALISATION - PARC D'ATTRACTION           ║
║                                                           ║
║  Ce script va:                                            ║
║  1. Supprimer toutes les tables existantes                ║
║  2. Créer les tables (users, attraction, critique)        ║
║  3. Insérer les données de test                           ║
║                                                           ║
║  ⚠️  ATTENTION: Toutes les données existantes seront      ║
║      perdues!                                             ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    success = init_database()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)