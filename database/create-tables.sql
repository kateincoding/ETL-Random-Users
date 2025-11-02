-- Crear extensión para UUIDs (si no existe)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========================
-- ENUMS
-- ========================
CREATE TYPE gender_type AS ENUM ('male', 'female', 'other', 'prefer_not_to_say');

-- ========================
-- TABLE: users
-- ========================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR,
    first_name VARCHAR,
    last_name VARCHAR,
    gender gender_type,
    email VARCHAR,
    dob TIMESTAMP,
    nat VARCHAR,
    phone VARCHAR(15),
    cell VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================
-- TABLE: DNI
-- ========================
CREATE TABLE dni (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    name VARCHAR,
    value VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_dni FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE
);

-- ========================
-- TABLE: location
-- ========================
CREATE TABLE location (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    state VARCHAR,
    city VARCHAR,
    sreet_number INTEGER,
    street_name VARCHAR,
    postcode INTEGER,
    coord_latitude DOUBLE PRECISION,
    coord_longitude DOUBLE PRECISION,
    timezone_offset VARCHAR(7),
    timezone_description VARCHAR,
	country VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_location FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE
);

-- ========================
-- TABLE: registers
-- ========================
CREATE TABLE registers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    age VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_registers FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE
);
