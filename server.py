"""
-------------------------------------------------------------------------------
Fichier de serveur Flask pour servir l'application via web.
-------------------------------------------------------------------------------
"""

from flask import Flask
import waitress
import os

from cqa.sources.certainty import certainty

app = Flask(__name__)

# ----------------------------------------------------------------------- index
@app.route('/', methods=['GET'])
def index():
    return 'Hello World!'

# ------------------------------------------------------------------------- cqa
@app.route('/cqa', methods=['POST'])
def cqa():
    """
    Fonction pour traiter les requêtes de cqa.
    """
    return 'CQA endpoint'



waitress.serve(
    app, 
    host='0.0.0.0', 
    port=8080,
    threads=4,
    backlog=100,
    )