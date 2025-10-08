import machine
import utime

BUTTON = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_DOWN)
LED = machine.Pin(18, machine.Pin.OUT)

compteur = 0
frequence = 1


def animation():

    for i in range(5):
        LED.value(1)
        utime.sleep(0.07)
        LED.value(0)
        utime.sleep(0.07)


# fonction appelée lors du front montant du bouton
def button_pressed(pin):
    global compteur
    compteur += 1
    if compteur > 7:
        compteur = 0
    print("compteur =", compteur)

    if compteur ==2 or compteur ==4 or compteur ==6 or compteur ==0: 
        animation()

# configurer l'interrupt sur front montant
BUTTON.irq(trigger=machine.Pin.IRQ_RISING, handler=button_pressed)

while True:
    if compteur == 0:
        LED.value(0)
    else:
        if compteur == 2:
            frequence = 2
        elif compteur == 4:
            frequence = 5
        elif compteur == 6:
            frequence = 15
        if compteur >=2:
            LED.value(1)
            utime.sleep(1/frequence/2)
            LED.value(0)
            utime.sleep(1/frequence/2)
