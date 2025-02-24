CREATE DATABASE oceano_azul;

USE oceano_azul;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20)  -- Adicionando o campo de telefone
);

INSERT INTO users (name, email, phone) VALUES
('John Doe', 'john@doe.com', '123-456-7890'),
('Jane Doe', 'jane@doe.com', '987-654-3210');

INSERT INTO users (name, email, phone) VALUES
('Kane Doe', 'kane@doe.com', '923-381-123');