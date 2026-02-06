CREATE TABLE IF NOT EXISTS attraction (
    attraction_id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    description TEXT,
    difficulte INTEGER,
    visible BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS critique (
    critique_id SERIAL PRIMARY KEY,
    attraction_id INTEGER REFERENCES attraction(attraction_id) ON DELETE CASCADE,
    nom VARCHAR(100),
    prenom VARCHAR(100),
    note INTEGER,
    commentaire TEXT,
    est_anonyme BOOLEAN DEFAULT FALSE
);

INSERT INTO attraction (nom, description, difficulte, visible) VALUES ('Silver Star', 'Montagne russe', 3, 1);
INSERT INTO attraction (nom, description, difficulte, visible) VALUES ('Montagne 8', 'Montagne russe', 4, 1);
INSERT INTO users (name, password) VALUES ('toto', 'toto');