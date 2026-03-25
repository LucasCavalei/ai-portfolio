# Entendendo o `with_structured_output` no LangChain

Este documento explica a diferença entre usar ferramentas tradicionais (`bind_tools`) e forçar saídas estruturadas (`with_structured_output`) em agentes LLM com LangChain, focando em aplicações no mundo real e integrações com APIs.

---
## 1. Contexto: Por que não usar no Chatbot SQL tradicional?

Em um chatbot focado em conversação (como um agente SQL que explica dados para o usuário), geralmente usamos `llm.bind_tools(tools)`. 

* **O que o `bind_tools` faz:** Ele ensina o LLM que existem "ferramentas" à disposição (como uma função que consulta um banco de dados). O LLM usa um formato estruturado *por baixo dos panos* apenas para invocar a ferramenta.
* **O Resultado:** A resposta final gerada e devolvida para a API (ex: Flask) é uma simples string em linguagem natural, como: *"A query retornou que Carlos vendeu um Notebook por R$ 4500,00"*.

O objetivo aqui é entregar um texto livre e amigável para o usuário ler.

---

## 2. O Problema da Extração de Dados (Antes do `with_structured_output`)

Modelos de linguagem (LLMs) geram nativamente apenas **texto livre**. Eles não geram objetos Python, arrays ou dicionários JSON puros.

Antigamente, para fazer uma API Flask devolver um JSON perfeitamente formatado para o front-end (React, Angular, etc.), era necessário usar "engenharia de prompt" frágil:
> *"Responda estritamente no formato JSON. Não adicione nenhum texto antes ou depois. Use as chaves 'nome' e 'idade'. Exemplo: {{ "nome": "Carlos", "idade": 30 }}."*

O problema é que, muitas vezes, a IA respondia com "alucinações de formatação":
`Aqui está o seu JSON: { "nome": "Carlos", "idade": 30 }`

Esse texto extra ("Aqui está o seu JSON:") quebrava a aplicação na hora de rodar o `json.loads()` no Python.

---

## 3. A Solução: Para que serve o `with_structured_output`?

O `with_structured_output` serve para **forçar** a Inteligência Artificial a devolver a resposta em um formato de dados rígido e previsível, em vez de texto livre. Ele resolve o problema do JSON fazendo três coisas automaticamente:

1. **Gera o Schema:** Traduz a estrutura definida (classe Pydantic ou JSON Schema) para o formato que o modelo entende (usando *Function/Tool Calling*).
2. **Força a Saída:** Trava o modelo para que a resposta final seja obrigatoriamente uma string de um JSON válido, sem textos extras.
3. **Faz o Parsing:** Converte a string JSON gerada pela IA diretamente para um objeto ou dicionário Python, pronto para uso no código.

### Casos de Uso Comuns:
* **Extração de Dados:** Ler o texto de um contrato em PDF e devolver um objeto contendo estritamente `{ "nome_contratante": "...", "cpf": "...", "valor": 1000 }`.
* **APIs Restritas:** Quando o front-end espera receber variáveis separadas e exatas da API, e não um bloco de texto contínuo.
* **Roteamento (Routing):** Em fluxos complexos, forçar a IA a responder apenas `"IR_PARA_PESQUISA"` ou `"IR_PARA_ATENDENTE"`.

---

## 4. Exemplos Práticos de Implementação

### Exemplo A: Usando a biblioteca Pydantic

Ideal para quando queremos que a API retorne não só a resposta em texto, mas também a query exata executada e um nível de confiança.

```python
from pydantic import BaseModel, Field

# 1. Definimos o "molde" (schema) rígido do que queremos que a IA responda
class RespostaFormatada(BaseModel):
    query_sql: str = Field(description="A query SQL exata que foi gerada e executada.")
    explicacao_usuario: str = Field(description="A resposta em linguagem natural explicando o dado.")
    nivel_confianca: int = Field(description="Nível de confiança da resposta de 1 a 10.")

# 2. Aplicamos esse molde ao LLM
llm_estruturado = llm.with_structured_output(RespostaFormatada)

# 3. Exemplo de como a IA responderia (sem o fluxo de tools, apenas para ilustrar)
resultado = llm_estruturado.invoke("Traduza para SQL e me explique: Quais as vendas do Carlos?")

# 'resultado' é um objeto Python com atributos exatos:
print(resultado.query_sql)          # Saída: "SELECT * FROM vendas WHERE vendedor = 'Carlos';"
print(resultado.explicacao_usuario) # Saída: "O Carlos possui as seguintes vendas registradas..."
print(resultado.nivel_confianca)    # Saída: 10