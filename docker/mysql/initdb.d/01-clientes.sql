-- Schema usado pela tool `cadastrar_cliente` (INSERT em clientes).
-- Roda só na primeira inicialização do volume do MySQL.

CREATE TABLE IF NOT EXISTS clientes (
    id VARCHAR(36) PRIMARY KEY,
    telefone_whatsapp VARCHAR(20) NOT NULL,
    nome VARCHAR(100),
    cpf VARCHAR(14),
    fase_funil VARCHAR(50) DEFAULT 'Novo Lead',
    ultima_interacao TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_telefone_whatsapp (telefone_whatsapp)
);
