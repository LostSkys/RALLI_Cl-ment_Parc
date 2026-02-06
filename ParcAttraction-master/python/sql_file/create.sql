-- ===============================================================
-- SCHÉMA DE BASE DE DONNÉES - PARC D'ATTRACTION
-- ===============================================================
-- Version: 2.0
-- Date: Février 2026
-- Description: Schéma complet avec tables attractions et critiques
-- ===============================================================

-- Suppression des tables existantes (ordre important pour FK)
DROP TABLE IF EXISTS critique;
DROP TABLE IF EXISTS attraction;
DROP TABLE IF EXISTS users;

-- ===============================================================
-- TABLE: users (Administrateurs)
-- ===============================================================
-- Description: Table des utilisateurs administrateurs
-- Usage: Authentification pour gérer les attractions
-- ===============================================================
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identifiant unique',
    name VARCHAR(100) NOT NULL UNIQUE COMMENT 'Nom d''utilisateur (login)',
    password VARCHAR(255) NOT NULL COMMENT 'Mot de passe hashé',
    email VARCHAR(255) COMMENT 'Email de l''administrateur',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Date de création',
    last_login TIMESTAMP NULL COMMENT 'Dernière connexion'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Utilisateurs administrateurs du système';

-- ===============================================================
-- TABLE: attraction
-- ===============================================================
-- Description: Table principale des attractions du parc
-- Règles métier:
--   - Une attraction peut être visible ou masquée (maintenance)
--   - La difficulté est notée de 1 (facile) à 5 (extrême)
--   - Les attractions masquées n'apparaissent pas côté visiteur
-- ===============================================================
CREATE TABLE attraction (
    attraction_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identifiant unique de l''attraction',
    nom VARCHAR(255) NOT NULL COMMENT 'Nom de l''attraction',
    description TEXT COMMENT 'Description détaillée de l''attraction',
    difficulte INT NOT NULL CHECK (difficulte BETWEEN 1 AND 5) COMMENT 'Niveau de difficulté (1=Facile, 5=Extrême)',
    visible TINYINT(1) DEFAULT 1 COMMENT '1=Visible par visiteurs, 0=Masquée (maintenance)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Date de création',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Dernière modification',
    
    INDEX idx_visible (visible) COMMENT 'Index pour filtrage rapide des attractions visibles',
    INDEX idx_difficulte (difficulte) COMMENT 'Index pour tri par difficulté'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Attractions du parc';

-- ===============================================================
-- TABLE: critique
-- ===============================================================
-- Description: Avis et notes laissés par les visiteurs
-- Règles métier:
--   - Un visiteur peut laisser plusieurs critiques
--   - Les critiques peuvent être anonymes
--   - La note est de 1 à 5 étoiles
--   - Suppression en cascade si attraction supprimée
-- ===============================================================
CREATE TABLE critique (
    critique_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identifiant unique de la critique',
    attraction_id INT NOT NULL COMMENT 'Référence à l''attraction',
    nom VARCHAR(255) COMMENT 'Nom du visiteur (ou "Anonyme")',
    prenom VARCHAR(255) COMMENT 'Prénom du visiteur',
    note INT NOT NULL CHECK (note BETWEEN 1 AND 5) COMMENT 'Note de 1 à 5 étoiles',
    commentaire TEXT COMMENT 'Texte de l''avis',
    est_anonyme BOOLEAN DEFAULT 0 COMMENT '1=Avis anonyme, 0=Identifié',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Date de publication',
    
    -- Clé étrangère avec suppression en cascade
    CONSTRAINT fk_attraction 
        FOREIGN KEY (attraction_id) 
        REFERENCES attraction(attraction_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    
    -- Index pour performances
    INDEX idx_attraction_id (attraction_id) COMMENT 'Index pour recherche par attraction',
    INDEX idx_note (note) COMMENT 'Index pour tri par note',
    INDEX idx_created_at (created_at) COMMENT 'Index pour tri chronologique'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='Critiques et avis des visiteurs';

-- ===============================================================
-- DONNÉES DE TEST
-- ===============================================================

-- Insertion d'un administrateur de test
-- Mot de passe: "admin123" (À CHANGER EN PRODUCTION!)
INSERT INTO users (name, password, email) VALUES 
('admin', 'admin123', 'admin@parcattraction.com');

-- Insertion d'attractions de démonstration
INSERT INTO attraction (nom, description, difficulte, visible) VALUES 
('Silver Star', 'Une montagne russe mythique avec des loopings vertigineux et une chute de 73 mètres.', 4, 1),
('Le Condor', 'Une chute libre spectaculaire de 100 mètres de hauteur. Sensations fortes garanties!', 5, 1),
('Le Carrousel', 'Manège traditionnel pour les plus petits. Douceur et musique d''antan.', 1, 1),
('Maintenance Express', 'Attraction actuellement en maintenance - NE PAS AFFICHER AUX VISITEURS', 3, 0),
('Space Mountain', 'Voyage dans les étoiles à toute vitesse dans le noir complet.', 4, 1),
('Le Petit Train', 'Balade tranquille à travers le parc pour découvrir les coulisses.', 1, 1),
('Le Manoir Hanté', 'Parcours terrifiant dans une maison hantée. Âmes sensibles s''abstenir!', 4, 0);

-- Insertion de critiques de démonstration
INSERT INTO critique (attraction_id, nom, prenom, note, commentaire, est_anonyme) VALUES 
(1, 'Dupont', 'Marie', 5, 'Incroyable! Les sensations sont au rendez-vous. Une attraction à ne pas manquer!', 0),
(1, 'Martin', 'Jean', 4, 'Très bien mais un peu d''attente. L''attraction en elle-même est top!', 0),
(1, 'Anonyme', '', 5, 'Meilleure attraction du parc sans hésitation!', 1),
(2, 'Bernard', 'Sophie', 5, 'J''ai adoré la chute libre! Mon cœur bat encore!', 0),
(2, 'Anonyme', '', 3, 'Trop intense pour moi, mais bien pour les amateurs de sensations fortes.', 1),
(3, 'Petit', 'Lucas', 5, 'Mon fils de 4 ans a adoré! Parfait pour les enfants.', 0),
(5, 'Rousseau', 'Emma', 5, 'Space Mountain est toujours aussi magique après toutes ces années!', 0),
(5, 'Anonyme', '', 4, 'Super attraction mais la file d''attente était très longue.', 1),
(6, 'Lefebvre', 'Pierre', 4, 'Balade agréable et reposante entre deux attractions à sensations.', 0);

-- ===============================================================
-- VUES UTILES (Optionnel)
-- ===============================================================

-- Vue: Attractions avec note moyenne
CREATE OR REPLACE VIEW v_attractions_note_moyenne AS
SELECT 
    a.attraction_id,
    a.nom,
    a.description,
    a.difficulte,
    a.visible,
    COUNT(c.critique_id) AS nombre_critiques,
    ROUND(AVG(c.note), 2) AS note_moyenne
FROM attraction a
LEFT JOIN critique c ON a.attraction_id = c.attraction_id
GROUP BY a.attraction_id, a.nom, a.description, a.difficulte, a.visible;

-- Vue: Attractions visibles avec statistiques
CREATE OR REPLACE VIEW v_attractions_visibles_stats AS
SELECT 
    a.attraction_id,
    a.nom,
    a.description,
    a.difficulte,
    COUNT(c.critique_id) AS total_avis,
    ROUND(AVG(c.note), 2) AS note_moyenne,
    MAX(c.created_at) AS dernier_avis
FROM attraction a
LEFT JOIN critique c ON a.attraction_id = c.attraction_id
WHERE a.visible = 1
GROUP BY a.attraction_id, a.nom, a.description, a.difficulte;

-- ===============================================================
-- PROCÉDURES STOCKÉES (Optionnel)
-- ===============================================================

-- Procédure: Obtenir les attractions populaires
DELIMITER //
CREATE PROCEDURE get_attractions_populaires(IN min_note DECIMAL(3,2))
BEGIN
    SELECT 
        a.attraction_id,
        a.nom,
        COUNT(c.critique_id) AS nombre_avis,
        ROUND(AVG(c.note), 2) AS note_moyenne
    FROM attraction a
    INNER JOIN critique c ON a.attraction_id = c.attraction_id
    WHERE a.visible = 1
    GROUP BY a.attraction_id, a.nom
    HAVING note_moyenne >= min_note
    ORDER BY note_moyenne DESC, nombre_avis DESC;
END //
DELIMITER ;

-- ===============================================================
-- STATISTIQUES ET INFORMATIONS
-- ===============================================================

-- Vérification du schéma
SELECT 'SCHÉMA CRÉÉ AVEC SUCCÈS!' AS statut;

SELECT 
    'Attractions' AS table_name,
    COUNT(*) AS total_lignes,
    SUM(CASE WHEN visible = 1 THEN 1 ELSE 0 END) AS visibles,
    SUM(CASE WHEN visible = 0 THEN 1 ELSE 0 END) AS masquees
FROM attraction
UNION ALL
SELECT 
    'Critiques',
    COUNT(*),
    NULL,
    NULL
FROM critique
UNION ALL
SELECT 
    'Utilisateurs',
    COUNT(*),
    NULL,
    NULL
FROM users;

-- ===============================================================
-- NOTES DE MAINTENANCE
-- ===============================================================
-- 
-- Pour sauvegarder la base:
--   mysqldump -u mysqlusr -p parc > backup.sql
--
-- Pour restaurer:
--   mysql -u mysqlusr -p parc < backup.sql
--
-- Pour réinitialiser (ATTENTION: perte de données!):
--   source create.sql
--
-- ===============================================================