from time import sleep
import network

# --- Connexion Wi-Fi ---
ssid = "SSID"
password = "MDP"
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# --- Déplacement du servo si Wi-Fi connecté ---
try:  
    if wlan.isconnected():
        print("Wi-Fi connecté, mouvement du servo...")
        print("Adresse IP:", wlan.ifconfig()[0])
    else:
        print("Wi-Fi non connecté.")
except Exception as e:
    print("Erreur :", e)
