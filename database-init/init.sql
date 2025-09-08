-- Database initialisatie script
-- Dit script wordt automatisch uitgevoerd bij de eerste opstart van PostgreSQL

-- Maak de tasks tabel aan als deze nog niet bestaat
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Voeg index toe voor betere performance
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);

-- Voeg wat voorbeelddata toe (optioneel)
INSERT INTO tasks (title, description) VALUES 
    ('Welkom bij Taakbeheer', 'Dit is je eerste taak! Je kunt deze verwijderen en nieuwe taken toevoegen.'),
    ('Docker Setup Voltooid', 'Gefeliciteerd! Je Docker containers draaien succesvol.')
ON CONFLICT DO NOTHING;

-- Toon bevestiging
SELECT 'Database initialisatie voltooid!' as status;