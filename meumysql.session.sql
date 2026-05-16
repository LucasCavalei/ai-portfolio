SELECT id, telefone_whatsapp, nome, cpf, fase_funil, ultima_interacao
FROM clientes
ORDER BY ultima_interacao DESC
LIMIT 20;