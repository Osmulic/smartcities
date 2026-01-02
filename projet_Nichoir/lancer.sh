#!/bin/bash

# 1. On attend 30 secondes que le réseau et le système soient prêts
sleep 20

# 2. On se déplace dans le dossier EXACT (Chemin absolu)
cd /home/alex/Desktop/projet_Nichoir

# 3. On active l environnement virtuel
source venv/bin/activate

# 4. On lance l application
python app.py