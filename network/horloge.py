from machine import Pin, PWM
from time import sleep
import network

# --- Configuration du servo ---
servo = PWM(Pin(20))
servo.freq(100)

# --- Connexion Wi-Fi ---
ssid = "SSID"
password = "MDP"
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

def set_angle(angle):
    # Limite les angles dans une plage sûre
    if angle < 0: angle = 0
    if angle > 180: angle = 180
    min_u16 = 4000    # ~0.61 ms
    max_u16 = 16020   # ~2.6 ms
    duty = int(min_u16 + (max_u16 - min_u16) * angle / 180)
    servo.duty_u16(duty)

# --- Déplacement du servo si Wi-Fi connecté ---
try:  
    if wlan.isconnected():
        print("Wi-Fi connecté, mouvement du servo...")
        print("Adresse IP:", wlan.ifconfig()[0])
        for a in range(0, 181, 90):
            set_angle(a)
            print("Angle:", a)
            sleep(1)
    else:
        print("Wi-Fi non connecté.")
except Exception as e:
    print("Erreur :", e)
