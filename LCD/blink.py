from machine import I2C, Pin, ADC, PWM
from dht20 import DHT20
from lcd1602 import LCD1602
from utime import sleep
from math import sin, pi
GPSCL =9
GPSDA = 8
i2c_temp= I2C(0, scl=Pin(GPSCL), sda=Pin(GPSDA), freq=100000)
i2c_screen= I2C(1)
LED = PWM(18, freq=1000)
buzzer = PWM(Pin(27))
potentiometer_adc = ADC(2)  # ADC2 → Pin 28

d = LCD1602(i2c_screen, 2, 16)
d.display()
dht20 = DHT20(i2c_temp)

def setTemp():
    value = potentiometer_adc.read_u16()
    normalized_value = value / 65535.0
    set_temp = 15 + (normalized_value * 20) #35 - 15 = 20
    return set_temp

# Déclaration de la variable globale pour la position de défilement
# Placez cette ligne en dehors de votre fonction, au niveau global de votre script
scroll_pos = 0

def mesure_affichage(temp, set_temp, cpt):
    global scroll_pos  # Permet de modifier la variable globale scroll_pos

    if cpt == 0:
        temp = dht20.dht20_temperature()
        set_temp = setTemp()

    if temp - set_temp > 3:
        msg = "ALARM ALARM "
        
        # Le modulo % len(msg) assure que la position revient au début
        # Le compteur 'cpt' est implicitement le mécanisme de "temps"
        start_index = scroll_pos % len(msg)
        
        # Largeur d'affichage de l'écran LCD 16 * 2
        display_width = 16 
        
        # Crée la chaîne à afficher en tenant compte du défilement
        if start_index + display_width < len(msg):
            # Le message entier tient sur la ligne sans coupure de fin
            text_to_display = msg[start_index : start_index + display_width]
        else:
            # Le message est coupé et revient au début (effet "looping")
            part1 = msg[start_index:]
            part2 = msg[:display_width - len(part1)]
            text_to_display = part1 + part2
            
        d.clear()
        d.setCursor(0, 0)
        if cpt < 6 : #Clignottement
            d.print(text_to_display)
        
        # Incrémente la position pour le prochain appel
        # On ne défile qu'une fois sur 2 ou 3 appels pour ralentir l'effet
        if cpt % 2 == 0: # Défilement un peu plus lent
             scroll_pos += 1
        
    else:
        # Réinitialisez la position de défilement quand l'alerte est terminée
        scroll_pos = 0 
        d.clear()
        d.setCursor(0, 0)
        d.print("Set:"+str(set_temp)+"C")
        d.setCursor(0, 1)
        d.print("Ambient:"+str(temp)+"C")
        
    return temp, set_temp

def verif_led(temp, set_temp, cpt_led):
    if temp - set_temp > 3:
        buzzer.duty_u16(32768)  # 50% duty cycle
        buzzer.freq(1000)  # 1 kHz
        # Oscillation plus rapide
        LED.duty_u16(int((sin(cpt_led * pi *2/ 10)**2) * 65535))

    elif temp - set_temp > 0:
        
        LED.duty_u16(int((sin(cpt_led * pi / 10)**2) * 65535))
        buzzer.duty_u16(0)  # Couper le buzzer
        
    else:
        LED.duty_u16(0)
        cpt_led = 0
        buzzer.duty_u16(0)  # Couper le buzzer

    cpt_led += 1
    if cpt_led == 10:  # 10 * 0.1s = 1s (0.5s ON / 0.5s OFF)
            cpt_led = 0
    return cpt_led

try:
    cpt =0
    cpt_led=0
    temp= 0
    set_temp= 0

    while True:

            temp, set_temp = mesure_affichage(temp, set_temp, cpt)

            cpt_led = verif_led(temp, set_temp, cpt_led)

            cpt += 1
            if cpt == 10:
                cpt = 0

            sleep(0.1)


except KeyboardInterrupt:
    pass
finally:
    LED.duty_u16(0)
    buzzer.duty_u16(0)  # Turn off the buzzer
    d.clear()
    d.print("Goodbye!")
