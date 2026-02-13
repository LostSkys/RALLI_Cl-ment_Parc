DROP TABLE IF EXISTS critique;
DROP TABLE IF EXISTS attraction;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE attraction (
    attraction_id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    description TEXT,
    difficulte INT NOT NULL,
    visible TINYINT(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE critique (
    critique_id INT AUTO_INCREMENT PRIMARY KEY,
    attraction_id INT NOT NULL,
    nom VARCHAR(255),
    prenom VARCHAR(255),
    note INT NOT NULL,
    commentaire TEXT,
    est_anonyme TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (attraction_id) REFERENCES attraction(attraction_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insertion des données de test
INSERT INTO attraction (nom, description, difficulte, visible) VALUES 
('Silver Star', 'Montagne russe', 5, 1),
('Le Condor', 'Attraction familiale', 2, 1),
('Le Carrousel', 'Pour les petits', 1, 1),
('Space Mountain', 'Vitesse pure', 5, 1),
('Le Petit Train', 'Visite du parc', 1, 1),
('Maintenance Express', 'En reparation', 3, 0);