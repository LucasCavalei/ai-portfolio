# ARQUIVO: src/main.py
# Ponto de entrada principal da aplicação

import os
import sys
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from api.routes_chat import chat_blueprint
# from agents.sql_simple import sql_blueprint
# from agents.lucas.test_sql import sql_blueprint  # Temporariamente desativado
from flask.json.provider import DefaultJSONProvider

load_dotenv()

# 2. Configuração UTF-8 para evitar problemas com acentuação
if sys.version_info >= (3, 7):
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
        except:
            pass  # Manter default se não funcionar

# 3. Configuração para não bugar a acentuação no JSON (que você já usava)
class CustomJSONProvider(DefaultJSONProvider):
    ensure_ascii = False
    indent = 2
    
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)
base_dir = os.path.abspath(os.path.dirname(__file__))

# 4. Inicializa o App Flask
app = Flask(__name__, instance_path=base_dir)
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False
app.json = CustomJSONProvider(app)

# Libera o CORS para o seu Frontend conseguir conversar com a API
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])

# 5. Conecta os "mini apps" (Blueprints) no app principal. 
# app.register_blueprint(sql_blueprint, url_prefix='/api')  # Temporariamente desativado
app.register_blueprint(chat_blueprint, url_prefix='/api')

# Rota de health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "chat-lucas-api"})

# Rota de teste
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "API está funcionando com UTF-8! Teste: á é í ó ú ç ã õ"})

if __name__ == '__main__':
    print("🚀 Iniciando o servidor Flask modular...")
    print("📍 Endpoints disponíveis:")
    print("   - POST /api/chat - Chat com Lucas (RAG)")
    print("   - POST /api/sql - Chat SQL com banco de dados")
    print("   - GET  /health  - Health check geral")
    print("   - GET  /api/sql/health - Health check do SQL")
    print("   - GET  /test    - Teste UTF-8")
    print("🌐 Servidor rodando em: http://localhost:5000")
    # use_reloader=False evita duplicar o carregamento da IA no Windows
    app.run(debug=True, use_reloader=False, port=5000)
