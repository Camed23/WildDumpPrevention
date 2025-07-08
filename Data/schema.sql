DROP DATABASE IF EXISTS wdp;
CREATE DATABASE wdp;

-- 1. Activer l'extension de chiffrement (utile pour les mots de passe)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 2. TYPES ENUM ------------------------------------------------------------

-- Type de rôles utilisateur
DROP TYPE IF EXISTS user_role CASCADE;
CREATE TYPE user_role AS ENUM ('Admin', 'Citoyen', 'Agent');

-- Type d'annotation (plein, vide, inconnu)
DROP TYPE IF EXISTS annotation_label_v CASCADE;
CREATE TYPE annotation_label_v AS ENUM ('plein', 'vide');
ALTER TYPE annotation_label_v ADD VALUE IF NOT EXISTS 'inconnu';

-- Source de l'annotation
DROP TYPE IF EXISTS annotation_source CASCADE;
CREATE TYPE annotation_source AS ENUM ('manuel', 'auto');

-- 3. TABLES ----------------------------------------------------------------

-- Table des utilisateurs
DROP TABLE IF EXISTS "User" CASCADE;
CREATE TABLE "User" (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role user_role NOT NULL
);

-- Table des images
DROP TABLE IF EXISTS Image CASCADE;
CREATE TABLE Image (
    image_id SERIAL PRIMARY KEY,
    file_path VARCHAR(255) NOT NULL,
    name_image VARCHAR(255),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT REFERENCES "User"(user_id),
    size FLOAT,
    width INT,
    height INT,
    avg_red FLOAT,
    avg_green FLOAT,
    avg_blue FLOAT,
    contrast FLOAT,
    edges_detected BOOLEAN,
    localisation TEXT,
    date_i TIMESTAMP
);

-- Table des annotations
DROP TABLE IF EXISTS Annotation CASCADE;
CREATE TABLE Annotation (
    annotation_id SERIAL PRIMARY KEY,
    label annotation_label_v NOT NULL,
    source annotation_source NOT NULL,
    date_a TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    image_id INT REFERENCES Image(image_id) ON DELETE CASCADE
);

-- 4. FONCTIONS -------------------------------------------------------------

-- Création d’un utilisateur
CREATE OR REPLACE FUNCTION creation_user(
    p_username VARCHAR,
    p_email VARCHAR,
    p_password VARCHAR,
    p_role user_role DEFAULT 'Citoyen'
) RETURNS VOID AS $$
BEGIN
    INSERT INTO "User" (username, email, password, role)
    VALUES (
        p_username,
        p_email,
        crypt(p_password, gen_salt('bf')),
        p_role
    );
END;
$$ LANGUAGE plpgsql;

-- Modification d’un utilisateur
CREATE OR REPLACE FUNCTION modif_user(
    p_user_id INT,
    p_username VARCHAR,
    p_email VARCHAR,
    p_password VARCHAR,
    p_role user_role
) RETURNS VOID AS $$
BEGIN
    UPDATE "User"
    SET username = p_username,
        email = p_email,
        password = p_password,
        role = p_role
    WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- Suppression d’un utilisateur
CREATE OR REPLACE FUNCTION supp_user(p_user_id INT) RETURNS VOID AS $$
BEGIN
    DELETE FROM "User" WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- Création d’une image
CREATE OR REPLACE FUNCTION creation_image(
    p_user_id INT,
    p_file_path VARCHAR,
    p_name_image VARCHAR,
    p_size FLOAT,
    p_width INT,
    p_height INT,
    p_avg_red FLOAT,
    p_avg_green FLOAT,
    p_avg_blue FLOAT,
    p_contrast FLOAT,
    p_edges_detected BOOLEAN,
    p_localisation TEXT
) RETURNS VOID AS $$
BEGIN
    INSERT INTO Image (
        user_id, file_path, name_image, size, width, height,
        avg_red, avg_green, avg_blue, contrast, edges_detected, localisation
    ) VALUES (
        p_user_id, p_file_path, p_name_image, p_size, p_width, p_height,
        p_avg_red, p_avg_green, p_avg_blue, p_contrast, p_edges_detected, p_localisation
    );
END;
$$ LANGUAGE plpgsql;

-- Modification d’une image
CREATE OR REPLACE FUNCTION modif_image(
    p_image_id INT,
    p_user_id INT,
    p_file_path VARCHAR,
    p_name_image VARCHAR,
    p_size FLOAT,
    p_width INT,
    p_height INT,
    p_avg_red FLOAT,
    p_avg_green FLOAT,
    p_avg_blue FLOAT,
    p_contrast FLOAT,
    p_edges_detected BOOLEAN,
    p_localisation TEXT
) RETURNS VOID AS $$
BEGIN
    UPDATE Image
    SET user_id = p_user_id,
        file_path = p_file_path,
        name_image = p_name_image,
        size = p_size,
        width = p_width,
        height = p_height,
        avg_red = p_avg_red,
        avg_green = p_avg_green,
        avg_blue = p_avg_blue,
        contrast = p_contrast,
        edges_detected = p_edges_detected,
        localisation = p_localisation
    WHERE image_id = p_image_id;
END;
$$ LANGUAGE plpgsql;

-- Suppression d’une image
CREATE OR REPLACE FUNCTION supp_image(p_image_id INT) RETURNS VOID AS $$
BEGIN
    DELETE FROM Image WHERE image_id = p_image_id;
END;
$$ LANGUAGE plpgsql;

-- Création d’une annotation
CREATE OR REPLACE FUNCTION creation_annotation(
    p_image_id INT,
    p_label annotation_label_v,
    p_source annotation_source
) RETURNS VOID AS $$
BEGIN
    INSERT INTO Annotation (image_id, label, source)
    VALUES (p_image_id, p_label, p_source);
END;
$$ LANGUAGE plpgsql;

-- Modification d’une annotation
CREATE OR REPLACE FUNCTION modif_annotation(
    p_annotation_id INT,
    p_image_id INT,
    p_label annotation_label_v,
    p_source annotation_source
) RETURNS VOID AS $$
BEGIN
    UPDATE Annotation
    SET image_id = p_image_id,
        label = p_label,
        source = p_source
    WHERE annotation_id = p_annotation_id;
END;
$$ LANGUAGE plpgsql;

-- Suppression d’une annotation
CREATE OR REPLACE FUNCTION supp_annotation(p_annotation_id INT) RETURNS VOID AS $$
BEGIN
    DELETE FROM Annotation WHERE annotation_id = p_annotation_id;
END;
$$ LANGUAGE plpgsql;

-- Nombre de poubelles pleines par ville
CREATE OR REPLACE FUNCTION nb_poubelles_pleines(par_ville TEXT)
RETURNS INTEGER AS $$
DECLARE
    nb_pleines INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO nb_pleines
    FROM Image i
    JOIN Annotation a ON a.image_id = i.image_id
    WHERE i.localisation = par_ville
      AND a.label = 'plein';

    RETURN nb_pleines;
END;
$$ LANGUAGE plpgsql;

-- Nombre de poubelles vides par ville
CREATE OR REPLACE FUNCTION nb_poubelles_vides(par_ville TEXT)
RETURNS INTEGER AS $$
DECLARE
    nb_vides INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO nb_vides
    FROM Image i
    JOIN Annotation a ON a.image_id = i.image_id
    WHERE i.localisation = par_ville
      AND a.label = 'vide';

    RETURN nb_vides;
END;
$$ LANGUAGE plpgsql;

-- Nombre de poubelles non annotées par ville
CREATE OR REPLACE FUNCTION nb_poubelles_non_annotées(par_ville TEXT)
RETURNS INTEGER AS $$
DECLARE
    nb_non_annotées INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO nb_non_annotées
    FROM Image i
    LEFT JOIN Annotation a ON a.image_id = i.image_id
    WHERE i.localisation = par_ville
      AND a.annotation_id IS NULL;

    RETURN nb_non_annotées;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION verify_password(p_email VARCHAR, p_password VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    result BOOLEAN;
BEGIN
    SELECT crypt(p_password, password) = password
    INTO result
    FROM "User"
    WHERE email = p_email;

    RETURN result;
END;
$$ LANGUAGE plpgsql;


-- Gestion des règles de classification des images

CREATE TABLE classification_rules (
    id SERIAL PRIMARY KEY,
    rule_name TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    threshold_operator TEXT CHECK (threshold_operator IN ('<', '>', '<=', '>=', '=', '!=')) NOT NULL,
    threshold_value DOUBLE PRECISION NOT NULL,
    weight DOUBLE PRECISION NOT NULL,
    category TEXT CHECK (category IN ('full', 'empty')) NOT NULL
);

-- fonction 
CREATE OR REPLACE FUNCTION add_classification_rule(
    p_rule_name TEXT,
    p_description TEXT,
    p_threshold_operator TEXT,
    p_threshold_value DOUBLE PRECISION,
    p_weight DOUBLE PRECISION,
    p_category TEXT
) RETURNS VOID AS $$
BEGIN
    INSERT INTO classification_rules (
        rule_name, description, threshold_operator,
        threshold_value, weight, category
    ) VALUES (
        p_rule_name, p_description, p_threshold_operator,
        p_threshold_value, p_weight, p_category
    );
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION update_classification_rule(
    p_rule_name TEXT,
    p_description TEXT,
    p_threshold_operator TEXT,
    p_threshold_value DOUBLE PRECISION,
    p_weight DOUBLE PRECISION,
    p_category TEXT
) RETURNS VOID AS $$
BEGIN
    UPDATE classification_rules
    SET
        description = p_description,
        threshold_operator = p_threshold_operator,
        threshold_value = p_threshold_value,
        weight = p_weight,
        category = p_category
    WHERE rule_name = p_rule_name;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Rule "%" does not exist.', p_rule_name;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION delete_classification_rule(
    p_rule_name TEXT
) RETURNS VOID AS $$
BEGIN
    DELETE FROM classification_rules WHERE rule_name = p_rule_name;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Rule "%" does not exist.', p_rule_name;
    END IF;
END;
$$ LANGUAGE plpgsql;


-- Création de nos règles

INSERT INTO classification_rules 
(rule_name, description, threshold_operator, threshold_value, weight, category) VALUES
-- Règles pour poubelle pleine
('area_ratio_high', 'Zone occupée élevée', '>', 0.60, 3.0, 'full'),
('hue_std_high', 'Variabilité des couleurs élevée', '>', 60, 2.0, 'full'),
('contrast_iqr_high', 'Contraste élevé', '>', 85, 2.0, 'full'),
('edge_density_low', 'Peu de contours nets', '<', 0.07, 1.0, 'full'),
('mean_brightness_low', 'Image sombre', '<', 115, 1.5, 'full'),
('texture_entropy_high', 'Forte entropie visuelle', '>', 6.5, 2.5, 'full'),
('color_complexity_high', 'Complexité des couleurs élevée', '>', 0.15, 2.0, 'full'),
('brightness_variance_high', 'Grande variance de luminosité', '>', 800, 1.5, 'full'),
('fill_ratio_advanced_high', 'Zone remplie avancée', '>', 0.45, 3.5, 'full'),

-- Règles pour poubelle vide
('area_ratio_low', 'Zone occupée faible', '<', 0.50, -2.5, 'empty'),
('hue_std_low', 'Faible variabilité des couleurs', '<', 55, -1.5, 'empty'),
('contrast_iqr_low', 'Contraste faible', '<', 75, -1.5, 'empty'),
('edge_density_high', 'Beaucoup de contours nets', '>', 0.09, -1.0, 'empty'),
('mean_brightness_high', 'Image claire', '>', 125, -1.0, 'empty'),
('texture_entropy_low', 'Faible entropie', '<', 5.0, -2.0, 'empty'),
('color_complexity_low', 'Peu de couleurs', '<', 0.08, -1.5, 'empty'),
('brightness_variance_low', 'Faible variance de luminosité', '<', 400, -1.5, 'empty'),
('spatial_frequency_low', 'Peu de textures', '<', 8, -1.0, 'empty'),
('fill_ratio_advanced_low', 'Zone peu remplie', '<', 0.25, -3.0, 'empty');

-- Ajout d'autre règle
INSERT INTO classification_rules 
(rule_name, description, threshold_operator, threshold_value, weight, category) VALUES
('shape_compactness_low', 'Forme peu compacte', '<', 0.35, 1.5, 'empty');

INSERT INTO classification_rules 
(rule_name, description, threshold_operator, threshold_value, weight, category) VALUES
('shape_compactness_high', 'Forme très compacte', '>', 0.75, 1.0, 'full');

INSERT INTO classification_rules 
(rule_name, description, threshold_operator, threshold_value, weight, category) VALUES
('edge_orientation_entropy_low', 'Peu de diversité dans les contours', '<', 2.0, 1.8, 'empty');

INSERT INTO classification_rules 
(rule_name, description, threshold_operator, threshold_value, weight, category) VALUES
('edge_orientation_entropy_high', 'Diversité élevée des directions de contours', '>', 3.5, 1.2, 'full');

INSERT INTO classification_rules 
(rule_name, description, threshold_operator, threshold_value, weight, category) VALUES
('center_mass_near_bottom', 'Centre de masse visuel vers le bas', '>', 0.65, 1.0, 'full');

INSERT INTO classification_rules 
(rule_name, description, threshold_operator, threshold_value, weight, category) VALUES
('center_mass_near_center', 'Centre de masse proche du centre', '<', 0.05, 1.3, 'empty');
