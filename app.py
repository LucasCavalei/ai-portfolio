from flask import Flask,  request, jsonify
from flask_cors import CORS
from main import executar_chat
from flask.json.provider import DefaultJSONProvider

class CustomJSONProvider(DefaultJSONProvider):
    ensure_ascii = False
    indent = 2

app = Flask(__name__)
app.json = CustomJSONProvider(app)
CORS(app)

@app.route('/api/chat', methods=['POST'])
def endpoint_chat():
    try:
        dados = request.json
        pergunta_usuario = dados.get("pergunta")
        
        if not pergunta_usuario:
            return jsonify({"status": "erro", "mensagem": "Pergunta vazia"}), 400

        conteudo_resposta = executar_chat(pergunta_usuario)
        return jsonify({
            "status": "sucesso",
            "resposta": conteudo_resposta
        })
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

if __name__ == '__main__':

    app.run(debug=True, use_reloader=False) # use_reloader=False evita duplicar o carregamento da IA no Windows
