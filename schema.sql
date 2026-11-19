CREATE DATABASE IF NOT EXISTS scheme_sathi;
USE scheme_sathi;

CREATE TABLE IF NOT EXISTS schemes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    min_age INT,
    max_age INT,
    max_income BIGINT,
    occupations VARCHAR(255),
    categories VARCHAR(255),
    genders VARCHAR(100),
    benefit TEXT,
    description TEXT,
    how_to_apply TEXT,
    official_url VARCHAR(500)
);

-- Starter schema for future MySQL integration.
-- The current MVP reads schemes.csv using Pandas.
