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

# ==========================================
# 6. ROTA DA API FLASK
# ==========================================
# ==========================================
# 6. ROTA DA API FLASK
# ==========================================
# ==========================================
# 6. ROTA DA API FLASK
# ==========================================
@chat_blueprint.route('/chat', methods=["POST"])
def chat_endpoint():
    try:
        # Marca o início do tempo de processamento
        start_time = time.time()
        
        dados = request.get_json()
        
        if not dados or "pergunta" not in dados:
            return jsonify({"erro": "Envie um JSON com o campo 'pergunta'."}), 400
            
        pergunta = dados["pergunta"]
        
        # 1. Pega o session_id do frontend. Se não vier (primeira mensagem), cria um UUID único na hora.
        session_id = dados.get("session_id", str(uuid.uuid4()))
        
        # 2. Configura a memória do LangGraph para usar esse ID específico
        config = {"configurable": {"thread_id": session_id}}
        
        # 3. Executa o grafo com a memória correta
        resposta_final = executar_chat(pergunta, session_id)
            
        # Calcula tempo de processamento
        processing_time = round((time.time() - start_time) * 1000, 2)
        logger.info(f"Resposta gerada em {processing_time}ms para a sessão {session_id}")
            
        # 4. Retorna o sucesso para o frontend
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