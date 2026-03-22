-- TABELA 1: LEADS E CLIENTES
-- Em chatbots, o cliente nasce apenas com o telefone. Os outros dados são enriquecidos durante a conversa.
CREATE TABLE clientes (
    id UUID PRIMARY KEY,
    telefone_whatsapp VARCHAR(20) UNIQUE NOT NULL,
    nome VARCHAR(100),
    cpf VARCHAR(14),
    opt_in_marketing BOOLEAN DEFAULT TRUE,
    fase_funil VARCHAR(50) DEFAULT 'Novo Lead', -- Ex: Novo Lead, Em Atendimento, Qualificado, Frio
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_interacao TIMESTAMP
);

-- TABELA 2: ESTOQUE DE VEÍCULOS
-- Focada no que interessa para a vitrine do bot e transações.
CREATE TABLE veiculos (
    id UUID PRIMARY KEY,
    placa VARCHAR(10) UNIQUE,
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(100) NOT NULL,
    ano_fabricacao INT,
    ano_modelo INT,
    valor_venda DECIMAL(10, 2),
    valor_aluguel_diaria DECIMAL(10, 2),
    status VARCHAR(30) DEFAULT 'Disponível', -- Disponível, Reservado, Vendido, Alugado
    tipo_veiculo VARCHAR(30) -- Novo, Seminovo
);

-- TABELA 3: SESSÕES E INTERAÇÕES DO WHATSAPP
-- Fundamental para rastrear o que o chatbot fez e quando passar para um humano.
CREATE TABLE sessoes_whatsapp (
    id UUID PRIMARY KEY,
    cliente_id UUID REFERENCES clientes(id),
    intencao_principal VARCHAR(50), -- Compra, Venda, Troca, Aluguel, Duvida
    transbordo_humano BOOLEAN DEFAULT FALSE,
    historico_conversa JSONB, -- Armazena o log da conversa de forma flexível
    data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_fim TIMESTAMP
);

-- TABELA 4: NEGOCIAÇÕES (OPORTUNIDADES)
-- Centraliza as intenções de transação geradas pelo chatbot.
CREATE TABLE negociacoes (
    id UUID PRIMARY KEY,
    cliente_id UUID REFERENCES clientes(id),
    veiculo_interesse_id UUID REFERENCES veiculos(id), -- Pode ser NULL se o cliente quer vender o carro dele
    tipo_transacao VARCHAR(30) NOT NULL, -- Compra, Venda (do cliente para loja), Troca, Aluguel
    status_negociacao VARCHAR(50) DEFAULT 'Aberto', -- Aberto, Proposta Enviada, Fechado, Perdido
    valor_proposta DECIMAL(10, 2),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


O Gemini disse
Entendo perfeitamente o seu objetivo. Você não quer um tutorial acadêmico, mas sim a arquitetura "pé no chão" de como as coisas funcionam nos bastidores de uma operação de captação ágil via WhatsApp. Em sistemas reais de chatbot para concessionárias, o foco não é um ERP complexo, mas sim a velocidade de captura do lead, o rastreamento da intenção e a conversão.

Abaixo, apresento a estrutura de tabelas (pensada para bancos relacionais como PostgreSQL ou MySQL) exatamente como seria modelada para um sistema focado em WhatsApp, onde o telefone é a chave de entrada e a interação é o motor do negócio.

1. A Estrutura Base de Dados (SQL)
Aqui estão as tabelas essenciais para gerenciar clientes, veículos, o fluxo de mensagens e as negociações.

SQL
-- TABELA 1: LEADS E CLIENTES
-- Em chatbots, o cliente nasce apenas com o telefone. Os outros dados são enriquecidos durante a conversa.
CREATE TABLE clientes (
    id UUID PRIMARY KEY,
    telefone_whatsapp VARCHAR(20) UNIQUE NOT NULL,
    nome VARCHAR(100),
    cpf VARCHAR(14),
    opt_in_marketing BOOLEAN DEFAULT TRUE,
    fase_funil VARCHAR(50) DEFAULT 'Novo Lead', -- Ex: Novo Lead, Em Atendimento, Qualificado, Frio
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_interacao TIMESTAMP
);

-- TABELA 2: ESTOQUE DE VEÍCULOS
-- Focada no que interessa para a vitrine do bot e transações.
CREATE TABLE veiculos (
    id UUID PRIMARY KEY,
    placa VARCHAR(10) UNIQUE,
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(100) NOT NULL,
    ano_fabricacao INT,
    ano_modelo INT,
    valor_venda DECIMAL(10, 2),
    valor_aluguel_diaria DECIMAL(10, 2),
    status VARCHAR(30) DEFAULT 'Disponível', -- Disponível, Reservado, Vendido, Alugado
    tipo_veiculo VARCHAR(30) -- Novo, Seminovo
);

-- TABELA 3: SESSÕES E INTERAÇÕES DO WHATSAPP
-- Fundamental para rastrear o que o chatbot fez e quando passar para um humano.
CREATE TABLE sessoes_whatsapp (
    id UUID PRIMARY KEY,
    cliente_id UUID REFERENCES clientes(id),
    intencao_principal VARCHAR(50), -- Compra, Venda, Troca, Aluguel, Duvida
    transbordo_humano BOOLEAN DEFAULT FALSE,
    historico_conversa JSONB, -- Armazena o log da conversa de forma flexível
    data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_fim TIMESTAMP
);

-- TABELA 4: NEGOCIAÇÕES (OPORTUNIDADES)
-- Centraliza as intenções de transação geradas pelo chatbot.
CREATE TABLE negociacoes (
    id UUID PRIMARY KEY,
    cliente_id UUID REFERENCES clientes(id),
    veiculo_interesse_id UUID REFERENCES veiculos(id), -- Pode ser NULL se o cliente quer vender o carro dele
    tipo_transacao VARCHAR(30) NOT NULL, -- Compra, Venda (do cliente para loja), Troca, Aluguel
    status_negociacao VARCHAR(50) DEFAULT 'Aberto', -- Aberto, Proposta Enviada, Fechado, Perdido
    valor_proposta DECIMAL(10, 2),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
2. O Que Está Faltando Neste Sistema?
Para que essa aplicação de WhatsApp deixe de ser apenas um "anotador de recados" e se torne uma ferramenta comercial completa (mas ainda assim separada do ERP gigante da empresa), faltam os seguintes módulos estruturais:

Tabela de Atendentes (Vendedores): O chatbot sempre tem um limite. Quando o lead esquenta ou faz uma pergunta complexa, ocorre o transbordo (handoff). O sistema precisa saber quais vendedores estão online, qual a fila de atendimento e quem é o dono daquele lead.

Tabela de Agendamentos (Test-Drive e Vistorias): Em aplicações reais, o bot já agenda a visita física. É necessário cruzar a agenda do cliente, a disponibilidade do veículo e o horário da loja.

Tabela de Avaliação de Usados (Trade-in): Na "Troca" ou "Venda" (quando a concessionária compra o carro do cliente), o bot geralmente pede fotos do painel, pneus e chassi. Faltam tabelas para registrar os dados desse veículo de terceiros e o laudo de avaliação feito pelo avaliador da loja.

Tabela de Mídias/Anexos: No WhatsApp, os clientes enviam fotos da CNH, comprovante de residência e fotos do carro para troca. É preciso uma estrutura para armazenar as URLs (geralmente num bucket como AWS S3) e vinculá-las à negociação correta.

Integração de Tabela FIPE: Não é necessariamente uma tabela local, mas o banco de dados precisaria de uma estrutura ou cache para consultar a API da Tabela FIPE e fornecer estimativas automáticas de preços no chat.