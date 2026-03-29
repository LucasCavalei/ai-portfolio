from flask import Blueprint, request, jsonify

from .graph import app_graph, executar_chat




# Mudei o nome do blueprint para fazer mais sentido, mas a estrutura do Flask é a mesma
portfolio_blueprint = Blueprint('portfolio', __name__)


