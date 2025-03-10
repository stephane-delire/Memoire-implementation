from flask import Flask, request, send_file, send_from_directory, abort
from waitress import serve
import subprocess
import os
import json

app = Flask(__name__)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ------------------------------------------------------------------------------
# Index
@app.route("/")
def index():
    print("Index")
    with open("../main.html", "r") as f:
        return f.read()


# ------------------------------------------------------------------------------
# Static files
@app.route("/<path:path>")
def static_file(path):
    print("Path: ", path)
    if path == "update":
        return update_server()
    file_path = os.path.join(PROJECT_ROOT, path)

    # Vérifier si le fichier existe
    if os.path.isfile(file_path):
        return send_file(file_path)
    else:
        abort(404)


# ------------------------------------------------------------------------------
# Update route
@app.route("/update", methods=["POST", "GET"])
def update_server():
    # try:
    #     req = json.loads(request.data)
    # except:
    #     return 'Invalid JSON', 400
    # if 'pusher' not in req:
    #     return 'Invalid JSON', 400
    #     if req['pusher']["name"] != "stephane-delire":
    #         return 'Invalid', 400

    process = subprocess.run(
        ["bash", "-c", "git pull"],
        capture_output=True,
        text=True,
        cwd="/home/azureuser/Memoire-implementation",
    )
    # Exécute le script de mise à jour
    # process = subprocess.run(
    #     ["./update.sh"],
    #     capture_output=True,
    #     text=True,
    #     cwd="/home/azureuser/Memoire-implementation/server",
    # )
    print("STDOUT:", process.stdout)
    print("STDERR:", process.stderr)

    # Retourne le résultat
    return f"STDOUT: {process.stdout}\nSTDERR: {process.stderr}"


# ==============================================================================
# Run the server
if __name__ == "__main__":
    serve(app, host="127.0.0.1", port=5050, threads=8, backlog=2048)
