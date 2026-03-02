# Chat AI RAG - Lucas Rodrigues 🤖

Sistema de chat modular com RAG (Retrieval-Augmented Generation) para responder perguntas sobre Lucas Rodrigues, desenvolvedor de software.

## 📁 Estrutura do Projeto

```
chatAiRag/
├── src/                          # Código fonte modular
│   ├── main.py                   # Ponto de entrada Flask
│   ├── database/                 # Configuração do Vector DB
│   │   ├── __init__.py
│   │   └── vector_db.py          # Pinecone + Cohere embeddings
│   ├── agents/                   # Lógica do chat
│   │   ├── __init__.py
│   │   └── bot_lucas.py          # Prompt + Groq + Chain
│   └── api/                      # Rotas Flask
│       ├── __init__.py
│       └── routes_chat.py        # Blueprint + Endpoints
├── frontend/                     # React app (chat interface)
├── base/                         # Documentos para RAG
├── .env                          # Variáveis de ambiente
└── requirements_new.txt          # Dependências Python
```

## 🚀 Como Executar

### 1. Instalar Dependências
```bash
pip install -r requirements_new.txt
```

### 2. Configurar Variáveis de Ambiente
Criar arquivo `.env` com:
```env
COHERE_API_KEY=sua_chave_cohere
PINECONE_API_KEY=sua_chave_pinecone
PINECONE_INDEX_NAME=meu-indice-rag
GROQ_API_KEY=sua_chave_groq
```

### 3. Iniciar Servidor
```bash
cd src
python main.py
```

### 4. Acessar Endpoints
- **Chat:** `POST http://localhost:5000/api/chat`
- **Health:** `GET http://localhost:5000/health`
- **Teste UTF-8:** `GET http://localhost:5000/test`

## 🔧 Módulos Explicados

### `database/vector_db.py`
- Configuração do Pinecone Vector Store
- Embeddings com Cohere API
- Função `buscar_contexto()` para RAG

### `agents/bot_lucas.py`
- Template de prompt personalizado
- Configuração do modelo Groq
- Gerenciamento de histórico de conversa
- Função `executar_chat()` principal

### `api/routes_chat.py`
- Blueprint Flask com rotas
- Validação de entrada
- Tratamento de erros
- Logging de requisições

### `main.py`
- Aplicação Flask principal
- Configuração UTF-8
- Registro de Blueprints
- CORS para frontend

## 📱 Exemplo de Uso

### Request:
```json
POST /api/chat
{
  "pergunta": "Quem é Lucas Rodrigues?"
}
```

### Response:
```json
{
  "status": "sucesso",
  "resposta": "Lucas é um desenvolvedor de software focado em tecnologias modernas. Quer saber mais sobre alguma área específica dele, como experiências ou projetos?",
  "processing_time_ms": 245.67
}
```

## 🛠️ Tecnologias

- **Backend:** Flask + Blueprint (modular)
- **AI:** LangChain + Groq (LLM)
- **Vector DB:** Pinecone + Cohere (embeddings)
- **Frontend:** React (interface chat)
- **RAG:** Retrieval-Augmented Generation

## 🎯 Features

- ✅ **Modular:** Código organizado em módulos
- ✅ **UTF-8:** Suporte completo a acentuação
- ✅ **Logging:** Monitoramento de requisições
- ✅ **Error Handling:** Tratamento robusto de erros
- ✅ **Health Checks:** Endpoints de verificação
- ✅ **Conversation Memory:** Histórico de conversa
- ✅ **Responsive:** Interface mobile-friendly

## 🔍 Debug e Monitoramento

### Logs do Sistema:
```bash
# Ver logs em tempo real
python main.py
```

### Health Checks:
```bash
# Health geral
curl http://localhost:5000/health

# Health do chat específico
curl http://localhost:5000/api/chat/health
```

### Teste UTF-8:
```bash
curl http://localhost:5000/test
```

## 📝 Melhorias Implementadas

1. **Estrutura Modular:** Separação clara de responsabilidades
2. **UTF-8 Fix:** Configuração completa para acentuação
3. **Response Control:** Limite de tokens e caracteres
4. **Error Handling:** Try/catch em todas as camadas
5. **Logging:** Monitoramento detalhado
6. **Validation:** Validação de entrada de dados
7. **Performance:** Tempo de processamento nas respostas

## 🚨 Próximos Passos

- [ ] Implementar cache de respostas
- [ ] Adicionar rate limiting
- [ ] Sistema de autenticação
- [ ] Analytics de conversas
- [ ] Deploy em produção
