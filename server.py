"""
-------------------------------------------------------------------------------
Fichier de serveur Flask pour servir l'application via web.
-------------------------------------------------------------------------------
"""

from flask import Flask, request, send_file
import waitress
import os

from cqa.sources.certainty import certainty

app = Flask(__name__)

# =============================================================================
# ----------------------------------------------------------------------- index
@app.route('/', methods=['GET'])
def index():
    with open('src/html/main.html', 'r') as f:
        html = f.read()
    return html

# ---------------------------------------------------------------------- static
@app.route('/src/<path:path>')
def send_src_file(path):
    """
    Fonction pour servir les fichiers statiques.
    """
    return send_file(os.path.join('src', path))

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
    threads=8,
    backlog=100,
    )