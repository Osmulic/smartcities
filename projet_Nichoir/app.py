from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# --- Configuration de la base de données ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Configuration du dossier d'upload ---
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# Assurez-vous que le dossier 'templates' existe pour index.html
os.makedirs('templates', exist_ok=True)

# --- Modèle de la base de données ---
class Photo(db.Model):
    __tablename__ = 'photos'
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    # J'ai rendu le niveau de batterie optionnel
    niveau_batterie = db.Column(db.Float, nullable=True) 

with app.app_context():
    db.create_all()

# -----------------------------------------------------------------
# --- ROUTE CORRIGÉE (C'EST LA PARTIE IMPORTANTE) ---
# -----------------------------------------------------------------
@app.route('/post', methods=['POST'])  # <- CHANGÉ en '/post'
def receive_picture():
    try:
        # L'Arduino envoie des données brutes, pas un "fichier"
        # Donc nous utilisons request.data, PAS request.files
        image_data = request.data
        
        if not image_data:
            return "Pas de données d'image reçues", 400

        # L'Arduino n'envoie pas le niveau de batterie.
        # Nous mettons une valeur par défaut (ex: 100.0) ou None.
        niveau_batterie = 100.0 

        # Créer un nom de fichier unique
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Écrire les données brutes dans un fichier
        with open(filepath, 'wb') as f:
            f.write(image_data)

        # Enregistrer dans la base de données
        # On enregistre juste le nom du fichier, pas le chemin complet
        nouvelle_photo = Photo(
            image_path=filename,  # <-- CHANGÉ (était 'filepath')
            niveau_batterie=niveau_batterie
        )
        db.session.add(nouvelle_photo)
        db.session.commit()

        print(f"Photo reçue et enregistrée : {filepath}")
        return jsonify({"message": "Photo reçue et enregistrée", "path": filepath}), 201

    except Exception as e:
        print(f"Erreur lors de la réception : {e}")
        return str(e), 500

# --- Route pour afficher la galerie ---
@app.route('/')
def index():
    try:
        photos = Photo.query.order_by(Photo.date.desc()).all()
        return render_template('index.html', photos=photos)
    except Exception as e:
        # Si index.html n'existe pas, cela affichera une erreur
        return f"Erreur lors du rendu du template : {e}. Assurez-vous que 'templates/index.html' existe."

# --- Route pour servir les images uploadées ---
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    print("Serveur démarré sur http://0.0.0.0:80")
    print("En attente de photos sur l'endpoint /post ...")
    app.run(host="0.0.0.0", port=80, debug=True)