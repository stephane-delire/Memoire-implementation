"""
-------------------------------------------------------------------------------
Fichier de serveur Flask pour servir l'application via web.
-------------------------------------------------------------------------------
"""

from flask import Flask, request, send_file
import waitress
import os
import json

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
    if 'Secret' not in request.headers:
        return 'No secret key provided', 400
    if request.headers['Secret'] != '@zeer-sdf-zertik-234kj':
        return 'Invalid secret key', 400
    if request.json is None:
        return 'No data received', 400
    if 'query' not in request.json:
        return 'No query received', 400

    text = request.json['query']
    if not isinstance(text, str):
        return 'Invalid query format', 400
    if len(text) == 0:
        return 'Empty query', 400
    
    data, guarded, graph, cycle, certain = certainty(text, graph_png=True)

    res = {
        'data': data,
        'guarded': guarded,
        'graph_txt': graph.get('txt') if graph else None,
        'graph_png': graph.get('png') if graph else None,
        'cycle': cycle,
        'certain': certain
    }

    return json.dumps(res), 200, {'Content-Type': 'application/json'}



waitress.serve(
    app, 
    host='0.0.0.0', 
    port=8080,
    threads=8,
    backlog=100,
    )