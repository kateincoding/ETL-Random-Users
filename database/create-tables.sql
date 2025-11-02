-- ========================
-- EXTENSIÓN PARA UUID
-- ========================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========================
-- ENUMS
-- ========================
CREATE TYPE gender_type AS ENUM ('male', 'female', 'other', 'prefer_not_to_say');
CREATE TYPE generation_type AS ENUM ('alpha' , 'z', 'millennial' , 'x', 'baby_boomer', 'silent');

-- ========================
-- TABLE: users
-- ========================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR,
    first_name VARCHAR,
    last_name VARCHAR,
    gender gender_type,
    email VARCHAR UNIQUE,
    dob TIMESTAMP,
    generation generation_type,
    nat VARCHAR,
    phone VARCHAR(20),
    cell VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================
-- TABLE: country
-- ========================
CREATE TABLE country (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================
-- TABLE: location
-- ========================
CREATE TABLE location (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    country_id UUID NOT NULL,
    state VARCHAR,
    city VARCHAR,
    street_number INTEGER,
    street_name VARCHAR,
    postcode VARCHAR(15),
    coord_latitude DOUBLE PRECISION,
    coord_longitude DOUBLE PRECISION,
    timezone_offset VARCHAR(7),
    timezone_description VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_location FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_country_location FOREIGN KEY (country_id)
        REFERENCES country(id) ON DELETE CASCADE
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
-- TABLE: registers
-- ========================
CREATE TABLE registers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    age INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_registers FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE
);
