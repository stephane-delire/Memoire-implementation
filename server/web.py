from flask import Flask, request, send_file, send_from_directory, abort
from waitress import serve
import subprocess
import os

app = Flask(__name__)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ------------------------------------------------------------------------------
# Index
@app.route('/')
def index():
    with open('../main.html', 'r') as f:
        return f.read()

# ------------------------------------------------------------------------------
# Static files
@app.route('/<path:path>')
def static_file(path):
    file_path = os.path.join(PROJECT_ROOT, path)

    # Vérifier si le fichier existe
    if os.path.isfile(file_path):
        return send_file(file_path)
    else:
        abort(404)

# ------------------------------------------------------------------------------
# Update route
@app.route('/update', methods=['POST'])
def update_server():
    # Exécute le script de mise à jour
    process = subprocess.run(["./update.sh"], capture_output=True, text=True)
    return ''

# ==============================================================================
# Run the server
if __name__ == '__main__':
    serve(app, host='127.0.0.1', port=5050, threads=8, backlog=2048)