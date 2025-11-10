from machine import Pin, PWM
from time import sleep
import time
import network
import ntptime

# --- Synchronisation initiale de l'heure ---
def time_sync(timezone_offset_hours=0):
    try:
        ntptime.settime()  # synchronise l'heure UTC
        t = time.localtime()
        h = (t[3] + timezone_offset_hours) % 24
        return h
    except Exception as e:
        print("Échec de la synchronisation de l'heure :", e)
        return None

# --- Contrôle du servo ---
def set_angle(hour):
    angle = (hour % 12) * 15
    # Limites sécurité
    min_u16 = 4000
    max_u16 = 16020
    duty = int(min_u16 + (max_u16 - min_u16) * angle / 180)
    servo.duty_u16(duty)
    return angle

# --- Configuration du servo ---
servo = PWM(Pin(20))
servo.freq(100)

# --- Connexion Wi-Fi ---
ssid = "SSID"
password = "MDP"
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

while not wlan.isconnected():
    print("Connexion au Wi-Fi en cours...")
    sleep(1)

print("Wi-Fi connecté, IP:", wlan.ifconfig()[0])

# --- Synchronisation initiale ---
current_hour = time_sync(1)  # UTC+1 pour Belgique
if current_hour is None:
    current_hour = 0  # fallback
angle = set_angle(current_hour)
print(f"Heure initiale: {current_hour}, angle: {angle}")

# --- Boucle principale ---
while True:
    t = time.localtime()
    hour = (t[3] + 1) % 24  # UTC+1

    if hour != current_hour:  # seulement si l'heure change
        current_hour = hour
        angle = set_angle(hour)
        print(f"Heure: {hour}, angle servo: {angle}")
    sleep(10)  # vérifie toutes les 10 secondes
