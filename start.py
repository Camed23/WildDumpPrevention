import os
import sys
import subprocess

# Ajoute le dossier courant au sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Exécute backend.app avec l'interpréteur Python du venv actif
python_executable = sys.executable  # Ce sera le bon venv (ex: venv\Scripts\python.exe)
subprocess.run([python_executable, "-m", "backend.app"])
