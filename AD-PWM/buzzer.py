from machine import Pin, PWM, ADC
from utime import sleep

# --- Setup ---
buzzer = PWM(Pin(27))
potentiometer_adc = ADC(2)  # ADC2 → Pin 28
LED = Pin(18, Pin.OUT)
BUTTON = Pin(16, Pin.IN, Pin.PULL_DOWN)

# --- Volume ---
vol = 0

# --- Interrupt bouton ---
def button_pressed(pin):
    global current_melody
    current_melody = 2 if current_melody == 1 else 1

BUTTON.irq(trigger=Pin.IRQ_RISING, handler=button_pressed)
current_melody = 1  # Initialisation de la mélodie
last_melody = current_melody

def current_melody_changed():
    global current_melody, last_melody
    if current_melody != last_melody:
        return True
    return False
    

def read_volume():
    global vol
    vol = potentiometer_adc.read_u16() // 2
    if vol > 32768:
        vol = 32768
    return vol

# --- Fonction générique pour jouer une note ---
def play(freq, time):
    if current_melody_changed():  # on vérifie si le bouton a été pressé
            buzzer.duty_u16(0)
            LED.value(0)
            return False  # arrêter la note immédiatement

    buzzer.freq(freq)
    buzzer.duty_u16(read_volume())
    LED.value(1)
    sleep(time)
    LED.value(0)

def N(time):
    # Silence
    if current_melody_changed():  # on vérifie si le bouton a été pressé
            buzzer.duty_u16(0)
            LED.value(0)
            return False  # arrêter la note immédiatement
    buzzer.duty_u16(0)
    LED.value(0)
    sleep(time)

# --- Notes ---
def DO(time): play(1046, time)
def RE(time): play(1175, time)
def MI(time): play(1318, time)
def FA(time): play(1397, time)
def SO(time): play(1568, time)
def LA(time): play(1760, time)
def SI(time): play(1967, time)



# --- Au clair de lune ---
def melody1():
    DO(0.5)
    N(0.1)
    RE(0.5)
    N(0.1)
    MI(0.5)
    N(0.1)
    DO(0.5)
    N(0.1)

    DO(0.5)
    N(0.1)
    RE(0.5)
    N(0.1)
    MI(0.5)
    N(0.1)
    DO(0.5)
    N(0.1) 

    MI(0.4)
    N(0.15) 
    FA(0.4)
    N(0.15) 
    SO(0.6)
    N(0.3) 

    MI(0.4)
    N(0.15) 
    FA(0.4)
    N(0.15) 
    SO(0.6)
    N(0.3) 



# --- Friteuse McDo (Trauma) ---
def melody2():
    DO(0.125)
    N(0.1)
    FA(0.125)
    N(0.1)
    DO(0.125)
    N(0.1)
    FA(0.125)
    N(0.1)
    DO(0.125)
    N(0.1)
    N(1)

    DO(0.125)
    N(0.1)
    FA(0.125)
    N(0.1)
    DO(0.125)
    N(0.1)
    N(1)

    DO(0.125)
    N(0.1)
    FA(0.125)
    N(0.1)
    DO(0.125)
    N(0.1)
    FA(0.125)
    N(0.1)
    DO(0.125)
    N(0.1)

    LA(0.125)
    N(0.1)
    LA(0.125)
    N(0.1)

    DO(0.125)
    N(0.1)
    FA(0.125)
    N(0.1)
    DO(0.125)
    N(0.1)
    FA(0.125)
    N(0.1)
    DO(0.125)
    N(0.1)

    SI(0.125)
    N(0.0625)
    SI(0.125)
    N(0.02)   
    SI(0.125)
    N(0.02)  
    SI(0.125)
    N(0.2)

    SI(0.125)
    N(0.0625)
    SI(0.125)
    N(0.02)   
    SI(0.125)
    N(0.02)  
    SI(0.125)
    N(0.65)   

    

# --- Main loop ---
try:
    while True:
        if current_melody == 1:
            melody1()
            last_melody = current_melody
            
        else:
            melody2()
            last_melody = current_melody
except KeyboardInterrupt:
    pass
finally:
    buzzer.deinit()
    LED.value(0)
