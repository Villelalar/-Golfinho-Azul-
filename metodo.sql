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

-- Example donation for testclient
INSERT INTO doacoes (user_id, status, metodo, valor, created_at)
VALUES ('testclient', 'pendente', 'pix', 100.00, NOW());