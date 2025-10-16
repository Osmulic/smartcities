from ws2812 import WS2812
from utime import sleep
from machine import ADC
from random import randint


BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 150, 0)
CYAN = (0, 255, 255)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)
ORANGE = (255, 50, 0)
PINK = (255, 0, 100)

COLORS = [RED, GREEN, BLUE, YELLOW, CYAN, PURPLE, WHITE, ORANGE, PINK]

led = WS2812(18,1) # WS2812 on pin 18, 1 LED
SOUND_SENSOR = ADC(2)

THRESHOLD = 105  # À ajuster selon votre capteur
prev_sound = SOUND_SENSOR.read_u16() // 256

cpt = 0
pulsation = 0
bpm = 0
moyenne_bpm = []
while True:
    sound = SOUND_SENSOR.read_u16() // 256
    # Détection de pic sonore simple
    if sound - prev_sound > THRESHOLD:
        color = COLORS[randint(0, len(COLORS) - 1)]
        led.pixels_fill(color)
        led.pixels_show()
        pulsation += 1

    prev_sound = sound
    cpt +=1
    if cpt >= 200:
        bpm = pulsation * 30
        print("BPM:", bpm)
        moyenne_bpm.append(bpm)
        pulsation = 0
        cpt = 0
        if len(moyenne_bpm) == 30 :
            avg_bpm = sum(moyenne_bpm) // len(moyenne_bpm)
            print("BPM moyen sur 1min:", avg_bpm)
            with open("bpm_log.txt", "a") as f:
                f.write("moyenne : {} bpm\n".format(avg_bpm))
            moyenne_bpm = []
            
    sleep(0.01)  # Fréquence d'échantillonnage