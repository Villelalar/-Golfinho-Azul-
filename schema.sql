USE defaultdb;

DROP TABLE IF EXISTS doacoes;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS aprovar_admins;

DROP TABLE IF EXISTS aprovar_admins;
CREATE TABLE aprovar_admins (
    id VARCHAR(14) PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    profile_color VARCHAR(20) DEFAULT '#008bb4'  
);


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

INSERT INTO users (id, email, password_hash, name, phone, role, profile_color) VALUES (
    'admin',
    'admin@admin.com',
    'pbkdf2:sha256:260000$hRu4PQsONrQM2xDx$a2e7481c6499f6ab643faec0b4dd1b77025f5c00e668ac014f949def08557e76',
    'Admin',
    NULL,
    'admin',
    '#008bb4'
);

INSERT INTO users (id, email, password_hash, name, phone, role, profile_color) VALUES (
    'testclient',
    'test@client.com',
    'pbkdf2:sha256:260000$hRu4PQsONrQM2xDx$a2e7481c6499f6ab643faec0b4dd1b77025f5c00e668ac014f949def085557e76',
    'Cliente Teste',
    '(11) 99999-9999',
    'client',
    '#008bb4'
);

INSERT INTO doacoes (user_id, status, metodo, valor, created_at) VALUES (
    'testclient',
    'pendente',
    'pix',
    50.00,
    CURRENT_TIMESTAMP
);