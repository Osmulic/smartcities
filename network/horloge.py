from machine import Pin, PWM
from time import sleep
import time
import network
import ntptime

def time_sync(timezone_offset_hours=0):
    global local_time
    try:
        ntptime.settime()  # synchronise l'heure UTC
        
        # Appliquer le décalage horaire
        t = time.localtime()
        h = (t[3] + timezone_offset_hours) % 24
        local_time = (h, t[4])

        return local_time
    except Exception as e:
        print("Échec de la synchronisation de l'heure :", e)
        return None


# --- Configuration du servo ---
servo = PWM(Pin(20))
servo.freq(100)

# --- Connexion Wi-Fi ---
ssid = "SSID"
password = "MDP"
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

time_sync(1)  # UTC+1 pour la Belgique)
print(f"Heure après synchronisation {local_time[0]} heures {local_time[1]} minutes")

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
        for a in range(0, 181, 15):
            set_angle(a)
            print("Angle:", a)
            sleep(1)
    else:
        print("Wi-Fi non connecté.")
except Exception as e:
    print("Erreur :", e)
