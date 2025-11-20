from flask import Flask, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import os
import paho.mqtt.client as mqtt

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Configuration MySQL/MariaDB ---
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://alex:mdp@localhost/battery_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_recycle': 300,
    'pool_pre_ping': True
}
db = SQLAlchemy(app)

class Photo(db.Model):
    __tablename__ = 'photos'
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    niveau_batterie = db.Column(db.Float, default=100.0, nullable=False)

with app.app_context():
    db.create_all()

# --- MQTT ---
MQTT_SERVER = "localhost"
MQTT_TOPIC = "nichoir/photo"

class MQTTManager:
    def __init__(self):
        self.client = None
        self.processed_messages = set()
        self.init_client()
    
    def init_client(self):
        if self.client is None:
            self.client = mqtt.Client()
            self.client.on_message = self.on_message
            self.client.on_connect = self.on_connect
            self.client.connect(MQTT_SERVER, 1883)
            self.client.loop_start()
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connecté au broker MQTT")
            client.subscribe(MQTT_TOPIC)
        else:
            print(f"Échec de connexion MQTT, code: {rc}")
    
    def on_message(self, client, userdata, msg):
        with app.app_context():
            # Vérification des doublons
            import hashlib
            message_hash = hashlib.md5(msg.payload).hexdigest()
            
            if message_hash in self.processed_messages:
                print("Message dupliqué ignoré")
                return
            
            self.processed_messages.add(message_hash)
            # Nettoyer les anciens hash (optionnel)
            if len(self.processed_messages) > 100:
                self.processed_messages.clear()
            
            print(f"Message MQTT reçu ({len(msg.payload)} octets)")
            
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
            filename = f"{timestamp}.jpg"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Vérifier si le fichier existe déjà
            if os.path.exists(filepath):
                print(f"Fichier existe déjà: {filename}")
                return
            
            with open(filepath, "wb") as f:
                f.write(msg.payload)
            
            # Vérifier en base de données
            existing_photo = Photo.query.filter_by(image_path=filename).first()
            if existing_photo:
                print(f"Photo déjà en base: {filename}")
                return
            
            try:
                new_photo = Photo(image_path=filename, niveau_batterie=100.0)
                db.session.add(new_photo)
                db.session.commit()
                print(f"Photo enregistrée : {filepath}")
            except Exception as e:
                db.session.rollback()
                print(f"Erreur base de données: {e}")

# Initialisation unique du manager MQTT
mqtt_manager = MQTTManager()

# --- Web interface ---
@app.route("/")
def index():
    try:
        photos = Photo.query.order_by(Photo.date.desc()).all()
        return render_template("index.html", photos=photos)
    except Exception as e:
        print(f"Erreur lors de la récupération des photos: {e}")
        return render_template("index.html", photos=[])

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    print("Serveur Flask démarré sur http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)