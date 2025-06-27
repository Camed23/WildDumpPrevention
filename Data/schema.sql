-- Types ENUM
CREATE TYPE user_role AS ENUM ('Admin', 'Citoyen', 'Agent');
CREATE TYPE annotation_label_v AS ENUM ('plein', 'vide');
CREATE TYPE annotation_source AS ENUM ('manuel', 'auto');

-- Extension nécessaire pour crypter les mots de passe
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Table User
CREATE TABLE "User" (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role user_role NOT NULL
);

-- Table Image
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
    edges_detected BOOLEAN
);

-- Table Annotation
CREATE TABLE Annotation (
    annotation_id SERIAL PRIMARY KEY,
    label annotation_label_v NOT NULL,
    source annotation_source NOT NULL,
    date_a TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    image_id INT REFERENCES Image(image_id) ON DELETE CASCADE
);

-- Fonction de création d'utilisateur
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

-- Fonction de modification d'utilisateur
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

-- Fonction de suppression d'utilisateur
CREATE OR REPLACE FUNCTION supp_user(p_user_id INT) RETURNS VOID AS $$
BEGIN
    DELETE FROM "User" WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- Fonction de création d'image
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
    p_edges_detected BOOLEAN
) RETURNS VOID AS $$
BEGIN
    INSERT INTO Image (
        user_id, file_path, name_image, size, width, height,
        avg_red, avg_green, avg_blue, contrast, edges_detected
    ) VALUES (
        p_user_id, p_file_path, p_name_image, p_size, p_width, p_height,
        p_avg_red, p_avg_green, p_avg_blue, p_contrast, p_edges_detected
    );
END;
$$ LANGUAGE plpgsql;

-- Fonction de modification d'image
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
    p_edges_detected BOOLEAN
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
        edges_detected = p_edges_detected
    WHERE image_id = p_image_id;
END;
$$ LANGUAGE plpgsql;

-- Fonction de suppression d'image
CREATE OR REPLACE FUNCTION supp_image(p_image_id INT) RETURNS VOID AS $$
BEGIN
    DELETE FROM Image WHERE image_id = p_image_id;
END;
$$ LANGUAGE plpgsql;

-- Fonction de création d'annotation
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

-- Fonction de modification d'annotation
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

-- Fonction de suppression d'annotation
CREATE OR REPLACE FUNCTION supp_annotation(p_annotation_id INT) RETURNS VOID AS $$
BEGIN
    DELETE FROM Annotation WHERE annotation_id = p_annotation_id;
END;
$$ LANGUAGE plpgsql;
