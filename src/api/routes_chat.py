# ARQUIVO: src/api/routes_chat.py

from flask import Blueprint, Flask, request, jsonify
from flask_cors import CORS
from agents.lucas.bot_lucas import executar_chat, app_graph
from flask.json.provider import DefaultJSONProvider
import logging
import time
import uuid

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criamos o Blueprint (é ele que exporta a rota para o main.py)
chat_blueprint = Blueprint('chat', __name__)

@chat_blueprint.route('/chat', methods=["POST"])
def chat_endpoint():
    start_time = time.time()
    
    try:
        # Validação dos dados de entrada
        dados = request.get_json()
        if not dados:
            return jsonify({
                "status": "erro", 
                "mensagem": "Nenhum dado JSON recebido"
            }), 400
        
        pergunta = dados.get("pergunta", "").strip()
        
        if not pergunta:
            return jsonify({
                "status": "erro", 
                "mensagem": "Pergunta vazia ou não fornecida"
            }), 400
        
        if len(pergunta) > 1000:
            return jsonify({
                "status": "erro", 
                "mensagem": "Pergunta muito longa. Máximo 1000 caracteres."
            }), 400
            
        # Log da pergunta (sem dados sensíveis)
        logger.info(f"Recebida pergunta: {pergunta[:50]}...")
        
        # 1. Pega o session_id do frontend. Se não vier, cria um UUID único.
        session_id = dados.get("session_id", str(uuid.uuid4()))
        
        # 2. Configura a memória do LangGraph para usar esse ID
        config = {"configurable": {"thread_id": session_id}}
        
        # 3. Executa o grafo com a memória correta
        resultado = app_graph.invoke({"messages": [("user", pergunta)]}, config)
        
        # 4. Pega a resposta gerada
        resposta_final = resultado["messages"][-1].content
        
        # Calcula tempo de processamento
        processing_time = round((time.time() - start_time) * 1000, 2)
        logger.info(f"Resposta gerada em {processing_time}ms para a sessão {session_id}")
        
        # 5. Retorna a resposta da IA e também o ID para o frontend
        return jsonify({
            "status": "sucesso",
            "resposta": resposta_final,
            "session_id": session_id,
            "processing_time_ms": processing_time
        })
        
    except Exception as e:
        # Log detalhado do erro
        logger.error(f"Erro no endpoint: {str(e)}", exc_info=True)
        
        return jsonify({
            "status": "erro", 
            "mensagem": "Erro interno no servidor. Tente novamente em alguns instantes.",
            "error_code": "INTERNAL_ERROR"
        }), 500

@chat_blueprint.route('/chat/health', methods=['GET'])
def chat_health():
    """Health check específico do chat"""
    try:
        # Testa se a função do bot está funcionando
        teste_resposta = executar_chat("teste", "health_check_session")
        
        return jsonify({
            "status": "healthy",
            "service": "chat-lucas-api",
            "bot_status": "online" if teste_resposta else "offline",
            "timestamp": time.time()
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "service": "chat-lucas-api",
            "error": str(e)
        }), 500