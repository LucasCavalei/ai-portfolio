CAMINHO_DB = "db"

prrompt_template = """ Responda a pergunta do usuario:
{pergunta}

Com base nessas informacoes:

{Base_conhecimento}

Se você não encontrar a resposta para a pergunta do usuario nessas informacoes, responda não sei te dizer isso"""

pergunta = input("Escreva sua pergunta: ")

#carregar o banco de dados
db = Chroma()

# comparar a pergunta do usuario (embeddings) com o banco de dados