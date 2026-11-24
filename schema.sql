CREATE DATABASE IF NOT EXISTS cotacoes CHARACTER SET utf8mb4;
USE cotacoes;
CREATE TABLE IF NOT EXISTS cotacao_dolar (
    data DATE PRIMARY KEY,            
    compra DECIMAL(10,4) NOT NULL,
    venda  DECIMAL(10,4) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT data, venda FROM cotacao_dolar ORDER BY data DESC LIMIT 10;
SELECT data, venda FROM cotacao_dolar ORDER BY data DESC LIMIT 20;