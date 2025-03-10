#!/bin/bash

# Script de mise a jour automatique lors de l'appel d'un webhook
# -------------------------------------------------------------

# On se place dans le dossier du projet
cd /home/azureuser/Memoire-implementation
echo "Mise à jour du serveur en cours...(pull)"
git pull

echo "Mise à jour du serveur effectuée avec succès"
# On redémarre le sservice (serveur)
sudo systemctl restart cqa_server.service