#!/bin/bash

# Script de mise a jour automatique lors de l'appel d'un webhook
# -------------------------------------------------------------

# On se place dans le dossier du projet
cd /home/azureuser/Memoire-implementation

git pull origin main

# On redémarre le sservice (serveur)
sudo systemctl restart cqa_server.service