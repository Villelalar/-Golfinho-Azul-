-- Create USERS database
CREATE DATABASE IF NOT EXISTS defaultdb;
USE defaultdb;

-- Drop and recreate tables
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS consultas;
DROP TABLE IF EXISTS instagram_posts;
DROP TABLE IF EXISTS imagens_homepage;

-- Create users table with auto-incrementing ID and role
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,  -- Store hashed passwords
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role ENUM('admin', 'client') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create consultas table with auto-incrementing ID
CREATE TABLE consultas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    data DATE NOT NULL,
    hora TIME NOT NULL,
    status VARCHAR(50) DEFAULT 'Agendada',
    detalhes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE KEY unique_consulta (user_id, data, hora)
);

-- Create instagram_posts table with auto-incrementing ID
CREATE TABLE instagram_posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id VARCHAR(50) UNIQUE NOT NULL,
    image_url TEXT NOT NULL,
    caption TEXT,
    post_link TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create imagens_homepage table with auto-incrementing ID
CREATE TABLE imagens_homepage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(50) NOT NULL,
    url VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_titulo (titulo)
);

-- Insert test admin (senha é "senha")
INSERT INTO users (email, username, password_hash, name, phone, role) VALUES (
    'admin@admin.com',
    'admin',
    'pbkdf2:sha256:260000$hRu4PQsONrQM2xDx$a2e7481c6499f6ab643faec0b4dd1b77025f5c00e668ac014f949def08557e76',
    'Admin',
    NULL,
    'admin'
);

-- Insert test client (senha é "senha")
INSERT INTO users (email, username, password_hash, name, phone, role) VALUES (
    'test@client.com',
    'client_test',
    'pbkdf2:sha256:260000$hRu4PQsONrQM2xDx$a2e7481c6499f6ab643faec0b4dd1b77025f5c00e668ac014f949def085557e76',
    'Cliente Teste',
    '(11) 99999-9999',
    'client'
);

-- Insert test consultation for the test client
INSERT INTO consultas (user_id, data, hora, status, detalhes) VALUES (
    (SELECT id FROM users WHERE email = 'test@client.com'),
    '2025-05-01',
    '14:00:00',
    'Agendada',
    'Consulta de rotina'
);

-- Insert test Instagram posts
INSERT INTO instagram_posts (post_id, image_url, caption, post_link) VALUES
('1234567890', 'https://via.placeholder.com/600x300?text=Post+Falso', 'Este é um post de teste para debug.', 'https://www.instagram.com/p/1234567890/'),
('0987654321', 'https://via.placeholder.com/600x300?text=Novo+Lançamento', 'Nosso novo produto chegou! Confira agora!', 'https://www.instagram.com/p/0987654321/'),
('1122334455', 'https://via.placeholder.com/600x300?text=Promoção+Especial', 'Aproveite nossa promoção por tempo limitado! 🎉', 'https://www.instagram.com/p/1122334455/'),
('5566778899', 'https://via.placeholder.com/600x300?text=Feedback+Cliente', 'Confira o que nossos clientes dizem sobre nós! ❤️', 'https://www.instagram.com/p/5566778899/'),
('6677889900', 'https://via.placeholder.com/600x300?text=Making+Of', 'Bastidores do nosso processo criativo! ✨', 'https://www.instagram.com/p/6677889900/'),
('7788990011', 'https://via.placeholder.com/600x300?text=Evento+Ao+Vivo', 'Estamos AO VIVO agora! Não perca essa oportunidade!', 'https://www.instagram.com/p/7788990011/');

-- Insert test homepage images
INSERT INTO imagens_homepage (titulo, url) VALUES
('Banner Principal', 'https://via.placeholder.com/1920x1080?text=Banner+Principal'),
('Sobre Nós', 'https://via.placeholder.com/800x600?text=Sobre+Nós'),
('Serviços', 'https://via.placeholder.com/800x600?text=Serviços'),
('Contato', 'https://via.placeholder.com/800x600?text=Contato');
