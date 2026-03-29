from typing import Literal

from .state import State, DadosCliente, llm, llm_with_tools, llm_roteador
from .tools import cadastrar_cliente

def agente_cadastro(state: State):
    # 1. Resgatamos o que o LangGraph já memorizou nas rodadas anteriores
    nome_salvo = state.get("nome")
    cpf_salvo = state.get("cpf")
    telefone_salvo = state.get("telefone")

    # Pegamos APENAS a última mensagem digitada pelo usuário
    ultima_msg = state["messages"][-1].content

    # 2. Configura o LLM extrator usando a sua classe
    llm_extrator = llm.with_structured_output(DadosCliente)
    
    # O prompt agora é simples e direto para analisar apenas a última fala
    dados_extraidos = llm_extrator.invoke(
        f"Extraia nome, cpf ou telefone do seguinte texto (retorne null para o que não achar): '{ultima_msg}'"
    )
    
    # 3. Atualizamos a nossa "memória" se a IA tiver achado algo novo agora
    if dados_extraidos.nome: nome_salvo = dados_extraidos.nome
    if dados_extraidos.cpf: cpf_salvo = dados_extraidos.cpf
    if dados_extraidos.telefone: telefone_salvo = dados_extraidos.telefone

    # ==========================================
    # 4. Lógica de Feedback e Roteamento (SUA LÓGICA MANTIDA)
    # ==========================================
    
    # Cenário A: Falta o Nome
    if not nome_salvo:
        # Verifica se ele já mandou o CPF logo de cara
        if cpf_salvo:
            msg = "Anotei o seu CPF. Qual o seu nome completo?"
        # Verifica se ele mandou o telefone primeiro
        elif telefone_salvo:
            msg = "Anotei o seu telefone. Para continuarmos, qual o seu nome completo?"
        # Não mandou nada ainda
        else:
            msg = "Olá! Para começarmos o seu cadastro, qual é o seu nome completo?"
            
        # IMPORTANTE: Além da mensagem, retornamos os dados para o LangGraph guardar!
        return {
            "messages": [("assistant", msg)], 
            "nome": nome_salvo, "cpf": cpf_salvo, "telefone": telefone_salvo
        }

    # Cenário B: Temos o Nome, mas falta o CPF
    if not cpf_salvo:
        msg = f"Prazer, {nome_salvo}! Agora só preciso do seu CPF."
        return {
            "messages": [("assistant", msg)], 
            "nome": nome_salvo, "cpf": cpf_salvo, "telefone": telefone_salvo
        }

    # Cenário C: Temos Nome e CPF, mas falta o Telefone
    if not telefone_salvo:
        msg = f"Certo, {nome_salvo}! Já anotei seu CPF. Por fim, qual o seu telefone com DDD?"
        return {
            "messages": [("assistant", msg)], 
            "nome": nome_salvo, "cpf": cpf_salvo, "telefone": telefone_salvo
        }

    # ==========================================
    # 5. Todos os dados preenchidos! Chama a Tool
    # ==========================================
    try:
        cadastrar_cliente.invoke({
            "nome": nome_salvo,
            "cpf": cpf_salvo,
            "telefone": telefone_salvo,
        })
        mensagem_final = f"Pronto, {nome_salvo}! Seu cadastro foi finalizado com sucesso."
        return {
            "messages": [("assistant", mensagem_final)], 
            "nome": nome_salvo, "cpf": cpf_salvo, "telefone": telefone_salvo
        }
        
    except Exception as e:
        return {
            "messages": [("assistant", f"Ops, ocorreu um erro ao salvar: {e}")],
            "nome": nome_salvo, "cpf": cpf_salvo, "telefone": telefone_salvo
        }
def roteador_semantico(state: State) -> Literal["chat_node", "especialista_node", "cadastro_node"]:
    """Analisa a última mensagem e decide para qual especialista enviar."""
    ultima_mensagem = state["messages"][-1].content
    try:
        decisao = llm_roteador.invoke(ultima_mensagem)
        return decisao.destino
    except Exception as e:
        print(f"Erro ao falar com a Groq no roteador: {e}")
        return "chat_node"

# ==========================================
# 4. OS NÓS ESPECIALISTAS (Personas)
# ==========================================
def agente_bate_papo(state: State):
    """Especialista em interações humanas. Não tem acesso a ferramentas."""
    mensagem_sistema = {
        "role": "system", 
        "content": (
            "Você é um assistente amigável do portfólio de Lucas Rodrigues. "
            "Sua postura é profissional e prestativa. "
            "O usuário está apenas puxando assunto ou te cumprimentando. "
            "Responda de forma breve, educada e natural. "
            "Se perguntarem o que você faz, diga que ajuda a responder perguntas sobre a carreira e os projetos do Lucas."
        )
    }
    mensagens_para_ia = [mensagem_sistema] + state["messages"]
    resposta = llm.invoke(mensagens_para_ia)
    return {"messages": [resposta]}

def agente_especialista(state: State):
    """Especialista sobre o Lucas. Tem acesso à base de conhecimento (tool)."""
    # Inserido EXATAMENTE o seu prompt aqui
    mensagem_sistema = {
        "role": "system", 
        "content": (
            "Você é um assistente amigável que conversa sobre Lucas Rodrigues, desenvolvedor de software. "
            "Use a ferramenta 'consultar_base_de_conhecimento' para buscar informações e responder de forma natural e conversada, como se estivesse numa conversa real.\n\n"
            "Instruções importantes:\n"
            "1. Responda de forma CONVERSADA e NATURAL, não como um robô\n"
            "2. Dê informações de forma GRADUAL - não junte tudo de uma vez\n"
            "3. Se perguntarem 'quem é Lucas', dê uma introdução breve e sugira perguntas específicas\n"
            "4. Use frases como 'Sobre isso...', 'Ah, sim...', 'Posso te contar que...' para soar mais humano\n"
            "5. Responda apenas ao que foi perguntado, não adicione informações extras não solicitadas\n"
            "6. Seja breve e direto nas respostas (2-3 frases no máximo)\n"
            "7. Se não tiver a informação, diga 'Sobre isso não tenho detalhes específicos, mas posso te ajudar com outras coisas sobre o trabalho dele'\n"
            "8. Use acentuação corretamente (á, é, í, ó, ú, ç, ã, õ)\n\n"
            "Exemplos de como responder:\n"
            "Pergunta: 'Quem é Lucas?'\n"
            "Resposta: 'Lucas é um desenvolvedor de software focado em tecnologias modernas. Quer saber mais sobre alguma área específica dele, como experiências ou projetos?'\n\n"
            "Pergunta: 'Quais projetos ele fez?'\n"
            "Resposta: 'Ele trabalhou em alguns projetos interessantes na área de desenvolvimento. Tem algum tipo de projeto específico que você gostaria de saber mais?'\n\n"
            "Pergunta: 'Onde ele estudou?'\n"
            "Resposta: 'Lucas tem formação na área de tecnologia. Quer saber mais sobre sua formação acadêmica ou cursos específicos?'"
        )
    }
    mensagens_para_ia = [mensagem_sistema] + state["messages"]
    resposta_ia = llm_with_tools.invoke(mensagens_para_ia)
    return {"messages": [resposta_ia]}

