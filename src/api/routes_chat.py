# ARQUIVO: src/api/routes_chat.py

from flask import Blueprint, Flask, request, jsonify
from flask_cors import CORS
from agents.lucas.bot_lucas import executar_chat
from flask.json.provider import DefaultJSONProvider
import logging
import time

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criamos o Blueprint (é ele que exporta a rota para o main.py)
chat_blueprint = Blueprint('chat', __name__)

@chat_blueprint.route('/chat', methods=['POST'])
def endpoint_chat():
    """Endpoint principal do chat - processa perguntas sobre Lucas Rodrigues"""
    start_time = time.time()
    
    try:
        # Validação dos dados de entrada
        dados = request.json
        if not dados:
            return jsonify({
                "status": "erro", 
                "mensagem": "Nenhum dado JSON recebido"
            }), 400
        
        pergunta_usuario = dados.get("pergunta", "").strip()
        
        if not pergunta_usuario:
            return jsonify({
                "status": "erro", 
                "mensagem": "Pergunta vazia ou não fornecida"
            }), 400
        
        if len(pergunta_usuario) > 1000:
            return jsonify({
                "status": "erro", 
                "mensagem": "Pergunta muito longa. Máximo 1000 caracteres."
            }), 400
        
        # Log da pergunta (sem dados sensíveis)
        logger.info(f"Recebida pergunta: {pergunta_usuario[:50]}...")
        
        # Chama o seu agente que está na outra pasta
        conteudo_resposta = executar_chat(pergunta_usuario)
        
        # Calcula tempo de processamento
        processing_time = round((time.time() - start_time) * 1000, 2)
        
        # Log da resposta
        logger.info(f"Resposta gerada em {processing_time}ms")
        
        return jsonify({
            "status": "sucesso",
            "resposta": conteudo_resposta,
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
        teste_resposta = executar_chat("teste")
        
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