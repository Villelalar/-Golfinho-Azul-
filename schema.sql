-- Create USERS database
CREATE DATABASE IF NOT EXISTS defaultdb;
USE defaultdb;

-- Drop and recreate tables
DROP TABLE IF EXISTS doacoes;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS aprovar_admins;

-- tabela para aprovar admins -> codigo deleta e bota em users com role admin
DROP TABLE IF EXISTS aprovar_admins;
CREATE TABLE aprovar_admins (
    id VARCHAR(14) PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,  -- senhas em hash geradas automaticamente
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    profile_color VARCHAR(20) DEFAULT '#008bb4'  -- cor do perfil
);

-- Tabela de usuarios -> ID == CPF
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id VARCHAR(14) PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role ENUM('admin', 'client') NOT NULL,
    profile_color VARCHAR(20) DEFAULT '#008bb4'  
);

-- Create consultas table with auto-incrementing ID
DROP TABLE IF EXISTS doacoes;
CREATE TABLE doacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(14) NOT NULL,
    status VARCHAR(50) DEFAULT 'pendente',
    metodo VARCHAR(50) DEFAULT 'pix',
    valor DECIMAL(10,2) NOT NULL,
    created_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE RESTRICT
);

-- Insert test admin (senha é "senha")
INSERT INTO users (id, email, password_hash, name, phone, role, profile_color) VALUES (
    'admin',
    'admin@admin.com',
    'pbkdf2:sha256:260000$hRu4PQsONrQM2xDx$a2e7481c6499f6ab643faec0b4dd1b77025f5c00e668ac014f949def08557e76',
    'Admin',
    NULL,
    'admin',
    '#008bb4'
);

-- Insert test client (senha é "senha")
INSERT INTO users (id, email, password_hash, name, phone, role, profile_color) VALUES (
    'testclient',
    'test@client.com',
    'pbkdf2:sha256:260000$hRu4PQsONrQM2xDx$a2e7481c6499f6ab643faec0b4dd1b77025f5c00e668ac014f949def085557e76',
    'Cliente Teste',
    '(11) 99999-9999',
    'client',
    '#008bb4'  -- cor do perfil padrão
);
