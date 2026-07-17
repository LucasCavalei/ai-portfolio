import re
from typing import Literal

from langchain_core.messages import AIMessage

from .embedding_router import classificar_por_embedding
from .state import DadosCliente, State, llm, llm_with_tools, llm_roteador
from .tools import cadastrar_cliente, consultar_base_de_conhecimento

# Llama/Groq às vezes ecoa chamadas de ferramenta como texto (<function=...>) em vez de tool_calls.
_FAKE_TOOL_NO_TEXTO = re.compile(
    r"\s*<function=[^>]+>.*?</function>\s*",
    re.DOTALL | re.IGNORECASE,
)

# Remove blocos <function=...>...</function> do content se não houver tool_calls estruturados.
#Alguns modelos (ex.: Groq/Llama) escrevem coisas como <function=...> no content em vez de preencher tool_calls. 
def _sem_vazamento_tool_no_texto(msg: AIMessage) -> AIMessage:
    """Remove blocos <function=...>...</function> do content se não houver tool_calls estruturados."""
    tool_calls = getattr(msg, "tool_calls", None) or []
    if tool_calls:
        return msg
    raw = msg.content
    if not isinstance(raw, str) or not raw.strip():
        return msg
    cleaned = _FAKE_TOOL_NO_TEXTO.sub(" ", raw)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    if cleaned == raw.strip():
        return msg
    return msg.model_copy(update={"content": cleaned})


# Saudações curtas: não dispara busca vetorial automática (evita ruído e custo).
_SAUDACAO_OU_VAGA = re.compile(
    r"^(oi|ol[áa]|opa|e a[ií]|tudo bem|td bem|bom dia|boa tarde|boa noite|ok|certo|valeu|obrigad[oa]|blz)\b",
    re.IGNORECASE,
)


def _ultima_pergunta_usuario(state: State) -> str:
    for m in reversed(state.get("messages") or []):
        if _eh_mensagem_usuario(m):
            return _conteudo_msg(m)
    return ""


def _evitar_rag_automatico(texto: str) -> bool:
    t = (texto or "").strip()
    if len(t) < 6:
        return True
    if _SAUDACAO_OU_VAGA.match(t) and len(t) < 45:
        return True
    return False


def _topico(state: State) -> str:
    t = (state.get("topico") or "whamais").strip().lower()
    return t if t in ("whamais", "lucas") else "whamais"


def _prompt_bate_papo(topico: str) -> str:
    if topico == "lucas":
        return (
            "Você é um assistente amigável do portfólio de Lucas Rodrigues, "
            "fundador da Whamais. "
            "Sua postura é profissional e prestativa. "
            "O usuário está apenas puxando assunto ou te cumprimentando. "
            "Responda de forma breve, educada e natural. "
            "Se perguntarem o que você faz, diga que ajuda a responder perguntas "
            "sobre a carreira e os projetos do Lucas."
        )
    return (
        "Você é o assistente virtual da Whamais — Comunicação Inteligente. "
        "Sua postura é profissional e prestativa. "
        "O usuário está apenas puxando assunto ou te cumprimentando. "
        "Responda de forma breve, educada e natural. "
        "Se perguntarem o que você faz, diga que ajuda a responder perguntas sobre "
        "a Whamais (IA, WhatsApp, voz, agenda) e seus serviços."
    )


def _prompt_especialista(topico: str) -> str:
    if topico == "lucas":
        return (
            "Você é um assistente amigável que conversa sobre Lucas Rodrigues, "
            "desenvolvedor Full Stack e fundador da Whamais. "
            "Use a ferramenta 'consultar_base_de_conhecimento' para buscar informações "
            "e responder de forma natural e conversada.\n\n"
            "Instruções importantes:\n"
            "1. Responda de forma CONVERSADA e NATURAL, não como um robô\n"
            "2. Dê informações de forma GRADUAL - não junte tudo de uma vez\n"
            "3. Se perguntarem 'quem é Lucas', dê uma introdução breve e sugira perguntas específicas\n"
            "4. Use frases como 'Sobre isso...', 'Ah, sim...', 'Posso te contar que...' para soar mais humano\n"
            "5. Responda apenas ao que foi perguntado, não adicione informações extras não solicitadas\n"
            "6. Seja breve e direto nas respostas (2-3 frases no máximo)\n"
            "7. Se não tiver a informação, diga que não tem detalhes específicos e ofereça outro assunto sobre a carreira ou projetos dele\n"
            "8. Use acentuação corretamente (á, é, í, ó, ú, ç, ã, õ)\n"
            "9. NUNCA escreva na mensagem ao usuário tags como <function=...>, JSON de ferramenta ou o texto "
            "'consultar_base_de_conhecimento' como se fosse parte da resposta.\n"
            "10. Se perguntarem sobre a empresa, mencione brevemente a Whamais e volte ao foco em Lucas, "
            "salvo se o usuário quiser detalhes da empresa."
        )
    return (
        "Você é o assistente oficial da Whamais — Comunicação Inteligente, "
        "empresa de IA para atendimento e automação (WhatsApp, voz e agenda). "
        "Use a ferramenta 'consultar_base_de_conhecimento' para buscar informações "
        "e responder de forma natural e conversada.\n\n"
        "Instruções importantes:\n"
        "1. Priorize SEMPRE a Whamais: o que faz, soluções, benefícios e como contratar/conversar\n"
        "2. Responda de forma CONVERSADA e NATURAL, não como um robô\n"
        "3. Dê informações de forma GRADUAL - não junte tudo de uma vez\n"
        "4. Destaque WhatsApp 24h, voz, agendamentos automáticos e comunicação no piloto automático\n"
        "5. Responda apenas ao que foi perguntado; seja breve (2-3 frases)\n"
        "6. Se perguntarem sobre Lucas, explique que ele é o fundador/desenvolvedor e ofereça detalhes se quiserem\n"
        "7. Quando fizer sentido, convide a deixar contato ou falar com a equipe\n"
        "8. Se não tiver a informação, diga com honestidade e sugira outro ponto sobre a Whamais\n"
        "9. Use acentuação corretamente (á, é, í, ó, ú, ç, ã, õ)\n"
        "10. NUNCA escreva na mensagem ao usuário tags como <function=...>, JSON de ferramenta ou o texto "
        "'consultar_base_de_conhecimento' como se fosse parte da resposta."
    )


def _prompt_fallback_rag(topico: str, contexto: str) -> str:
    if topico == "lucas":
        return (
            "Você é o assistente do portfólio de Lucas Rodrigues (desenvolvedor e fundador da Whamais). "
            "Use o trecho abaixo da base de conhecimento (currículo, projetos, formação) para "
            "responder à última mensagem do usuário, em português, 2 a 3 frases, tom conversado.\n"
            "Se o trecho não permitir responder com segurança, diga que não tem detalhes específicos "
            "e sugira outro assunto sobre a carreira ou os projetos dele.\n"
            "Não mencione 'contexto', 'trecho' ou 'base de dados' na fala.\n\n"
            f"---\n{contexto}\n---"
        )
    return (
        "Você é o assistente da Whamais — Comunicação Inteligente. "
        "Use o trecho abaixo da base de conhecimento (empresa, soluções IA, WhatsApp, voz, agenda) para "
        "responder à última mensagem do usuário, em português, 2 a 3 frases, tom conversado.\n"
        "Priorize a Whamais. Se o trecho não permitir responder com segurança, diga que não tem "
        "detalhes específicos e sugira outro assunto sobre os serviços da empresa.\n"
        "Não mencione 'contexto', 'trecho' ou 'base de dados' na fala.\n\n"
        f"---\n{contexto}\n---"
    )


#Se não houve tool_calls, o modelo “falhou” em acionar a tool. Aí o código não deixa a resposta crua:
# faz um fallback — consulta a base com a última pergunta do usuário (quando não é saudação vaga)
# (quando não é saudação vaga) e gera uma resposta final com contexto RAG.
def _resposta_especialista_com_fallback_rag(state: State, rascunho: AIMessage) -> AIMessage:
    """
    Se o modelo não emitiu tool_calls, consulta a base com a última fala do usuário
    e gera a resposta final com o contexto (mesmo papel do ToolNode + novo turno).
    """
    pergunta = _ultima_pergunta_usuario(state)
    if _evitar_rag_automatico(pergunta):
        return rascunho

    try:
        contexto = consultar_base_de_conhecimento.invoke({"query": pergunta})
    except Exception as e:
        contexto = f"(Falha ao consultar a base: {e})"

    sintese = {
        "role": "system",
        "content": _prompt_fallback_rag(_topico(state), contexto),
    }
    return llm.invoke([sintese] + state["messages"])


def roteador_semantico(state: State) -> Literal["chat_node", "especialista_node", "cadastro_node"]:
    """Analisa a última mensagem e decide para qual especialista enviar."""
    msgs = state.get("messages") or []
    if not msgs:
        return "chat_node"

    ultima_mensagem = _conteudo_msg(msgs[-1])

    if state.get("em_cadastro"):
        return "cadastro_node"

    if state.get("nome") or state.get("cpf") or state.get("telefone"):
        return "cadastro_node"

    if _intencao_cadastro_explicita(ultima_mensagem):
        return "cadastro_node"

    anterior_ai = _texto_ultimo_assistente_antes_do_usuario(msgs)
    if anterior_ai and _assistente_pediu_cadastro(anterior_ai):
        return "cadastro_node"

    try:
        dest_emb = classificar_por_embedding(ultima_mensagem)
        if dest_emb is not None:
            return dest_emb
    except Exception as e:
        print(f"Roteador por embedding falhou, usando LLM: {e}")

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
        "content": _prompt_bate_papo(_topico(state)),
    }
    mensagens_para_ia = [mensagem_sistema] + state["messages"]
    resposta = llm.invoke(mensagens_para_ia)
    return {"messages": [resposta]}


def agente_especialista(state: State):
    """Especialista Whamais (padrão) ou Lucas, conforme topico no state."""
    mensagem_sistema = {
        "role": "system",
        "content": _prompt_especialista(_topico(state)),
    }
    mensagens_para_ia = [mensagem_sistema] + state["messages"]
    resposta_ia = llm_with_tools.invoke(mensagens_para_ia)
    if isinstance(resposta_ia, AIMessage):
        resposta_ia = _sem_vazamento_tool_no_texto(resposta_ia)

    tool_calls = getattr(resposta_ia, "tool_calls", None) or []
    if tool_calls:
        return {"messages": [resposta_ia]}

    if isinstance(resposta_ia, AIMessage):
        resposta_ia = _resposta_especialista_com_fallback_rag(state, resposta_ia)
    return {"messages": [resposta_ia]}


def _cadastro_foi_persistido(retorno_tool: str) -> bool:
    """Mesmo critério que `cadastro_foi_persistido` em tools (evita import circular via package)."""
    return "cadastrado com sucesso! ID:" in (retorno_tool or "")


def agente_cadastro(state: State):
    nome_salvo = state.get("nome")
    cpf_salvo = state.get("cpf")
    telefone_salvo = state.get("telefone")

    ultima_msg = _conteudo_msg(state["messages"][-1])

    llm_extrator = llm.with_structured_output(DadosCliente)

    dados_extraidos = llm_extrator.invoke(
        f"Extraia nome, cpf ou telefone do seguinte texto (retorne null para o que não achar): '{ultima_msg}'"
    )

    if dados_extraidos.nome:
        nome_salvo = dados_extraidos.nome
    if dados_extraidos.cpf:
        cpf_salvo = dados_extraidos.cpf
    if dados_extraidos.telefone:
        telefone_salvo = dados_extraidos.telefone

    cpf_local = _cpf_onze_digitos(ultima_msg)
    if cpf_local and not cpf_salvo:
        cpf_salvo = cpf_local

    if _so_digitos(telefone_salvo) and _so_digitos(telefone_salvo) == _so_digitos(cpf_salvo):
        telefone_salvo = None

    if not nome_salvo:
        recuperado = _recuperar_nome_do_historico(state["messages"], llm_extrator)
        if recuperado:
            nome_salvo = recuperado

    if not nome_salvo:
        if cpf_salvo:
            msg = "Anotei o seu CPF. Qual o seu nome completo?"
        elif telefone_salvo:
            msg = "Anotei o seu telefone. Para continuarmos, qual o seu nome completo?"
        else:
            msg = "Olá! Para começarmos o seu cadastro, qual é o seu nome completo?"

        return {
            "messages": [("assistant", msg)],
            "nome": nome_salvo,
            "cpf": cpf_salvo,
            "telefone": telefone_salvo,
            "em_cadastro": True,
        }

    if not cpf_salvo:
        msg = f"Prazer, {nome_salvo}! Agora só preciso do seu CPF."
        return {
            "messages": [("assistant", msg)],
            "nome": nome_salvo,
            "cpf": cpf_salvo,
            "telefone": telefone_salvo,
            "em_cadastro": True,
        }

    if not telefone_salvo:
        msg = f"Certo, {nome_salvo}! Já anotei seu CPF. Por fim, qual o seu telefone com DDD?"
        return {
            "messages": [("assistant", msg)],
            "nome": nome_salvo,
            "cpf": cpf_salvo,
            "telefone": telefone_salvo,
            "em_cadastro": True,
        }

    try:
        retorno = cadastrar_cliente.invoke(
            {
                "nome": nome_salvo,
                "cpf": cpf_salvo,
                "telefone": telefone_salvo,
            }
        )
        retorno_str = retorno if isinstance(retorno, str) else str(retorno)
        if _cadastro_foi_persistido(retorno_str):
            mensagem_final = (
                f"Pronto, {nome_salvo}! Seu cadastro foi salvo com sucesso no sistema."
            )
            return {
                "messages": [("assistant", mensagem_final)],
                "nome": nome_salvo,
                "cpf": cpf_salvo,
                "telefone": telefone_salvo,
                "em_cadastro": False,
            }
        if "não configurado" in retorno_str or "indisponível" in retorno_str.lower():
            msg_usuario = (
                "Não consegui salvar seu cadastro agora: o banco de dados não está "
                "disponível. Seus dados continuam só nesta conversa até configurarmos o salvamento."
            )
        else:
            msg_usuario = retorno_str
        return {
            "messages": [("assistant", msg_usuario)],
            "nome": nome_salvo,
            "cpf": cpf_salvo,
            "telefone": telefone_salvo,
            "em_cadastro": True,
        }

    except Exception as e:
        return {
            "messages": [("assistant", f"Ops, ocorreu um erro ao salvar: {e}")],
            "nome": nome_salvo,
            "cpf": cpf_salvo,
            "telefone": telefone_salvo,
            "em_cadastro": True,
        }


def _so_digitos(texto: str | None) -> str:
    return re.sub(r"\D", "", texto or "")


def _cpf_onze_digitos(texto: str) -> str | None:
    d = _so_digitos(texto)
    if len(d) == 11:
        return d
    return None


def _eh_mensagem_usuario(msg) -> bool:
    if isinstance(msg, tuple) and msg:
        return msg[0] in ("human", "user")
    t = getattr(msg, "type", None)
    return t in ("human", "user")


def _recuperar_nome_do_historico(msgs, llm_extrator) -> str | None:
    trechos = []
    for m in msgs[:-1]:
        if not _eh_mensagem_usuario(m):
            continue
        t = _conteudo_msg(m).strip()
        if not t:
            continue
        if len(re.sub(r"\D", "", t)) >= 10:
            continue
        tl = t.lower()
        if "cadast" in tl or "registr" in tl:
            continue
        trechos.append(t)
    if not trechos:
        return None
    blob = " | ".join(trechos[-5:])
    dados = llm_extrator.invoke(
        "Extraia apenas o nome completo do usuário nos trechos abaixo. "
        "Retorne null se não houver nome de pessoa.\n\n" + blob
    )
    return dados.nome if dados.nome else None


def _conteudo_msg(msg) -> str:
    if isinstance(msg, tuple) and len(msg) >= 2:
        raw = msg[1]
    else:
        raw = getattr(msg, "content", None)
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw.strip()
    if isinstance(raw, list):
        parts = []
        for block in raw:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text") or "")
        return " ".join(parts).strip()
    return str(raw).strip()


def _eh_mensagem_assistente(msg) -> bool:
    if isinstance(msg, tuple) and msg:
        return msg[0] in ("assistant", "ai")
    t = getattr(msg, "type", None)
    if t in ("ai", "assistant"):
        return True
    return type(msg).__name__ == "AIMessage"


def _texto_ultimo_assistente_antes_do_usuario(msgs) -> str:
    if len(msgs) < 2:
        return ""
    for m in reversed(msgs[:-1]):
        if _eh_mensagem_assistente(m):
            return _conteudo_msg(m)
    return ""


def _intencao_cadastro_explicita(texto: str) -> bool:
    t = texto.lower()
    if "cadast" in t:
        return True
    if any(
        k in t
        for k in (
            "me cadastra",
            "registr",
            "registar",
            "registrar",
            "deixar contato",
            "meu cpf",
            "meu telefone",
            "meu whatsapp",
            "deixar whatsapp",
        )
    ):
        return True
    if re.search(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}", texto):
        return True
    if re.search(r"\(?\d{2}\)?\s*\d{4,5}-?\d{4}", texto):
        return True
    return False


def _assistente_pediu_cadastro(texto: str) -> bool:
    t = texto.lower()
    return any(
        x in t
        for x in (
            "cadastro",
            "nome completo",
            "seu cpf",
            "seu telefone",
            "telefone com ddd",
            "anotei o seu cpf",
            "anotei o seu telefone",
        )
    )
