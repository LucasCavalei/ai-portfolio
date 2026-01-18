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

@app.route('/')
def endpoint_chat():
    try:
        conteudo_resposta = executar_chat("me fale de uma tecnica de venda bastante eficiente")
        # Agora o Flask retorna um objeto JSON real para o navegador
        return jsonify({
            "status": "sucesso",
            "resposta": conteudo_resposta
        })
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

if __name__ == '__main__':

    app.run(debug=True, use_reloader=False) # use_reloader=False evita duplicar o carregamento da IA no Windows
