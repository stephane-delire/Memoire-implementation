echo "Starting service"
cd /home/azureuser/venv
echo "Activating virtual environment"
source bin/activate
echo "Activating virtual environment done"
cd /home/azureuser/Memoire-implementation/server
echo "Starting server"
python web.py