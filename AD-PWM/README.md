# Buzzer Musical avec Changement de Mélodie

Ce projet permet de jouer des mélodies sur un buzzer contrôlé par un pi pico avec un potentiomètre pour régler le volume et un bouton pour changer de mélodie.

## Matériel requis

- Microcontrôleur compatible MicroPython (ex. Raspberry Pi Pico)
- Buzzer passif
- Potentiomètre
- LED
- Bouton poussoir
- Fils de connexion et breadboard

## Schéma de câblage

- **Buzzer** → Pin 27  
- **Potentiomètre** → ADC2 (Pin 28)  
- **LED** → Pin 18  
- **Bouton** → Pin 16 

## Fonctionnalités

- Lecture de deux mélodies différentes :
  - Mélodie 1 : *Au clair de lune*  
  - Mélodie 2 : *Friteuse McDo (Trauma)*
- Changement de mélodie avec un bouton poussoir.
- Réglage du volume via un potentiomètre.
- LED qui s’allume pendant la durée d’une note.

## Installation

1. Flasher MicroPython sur votre microcontrôleur.
2. Copier le script Python sur la carte (`main.py` ou un autre nom de fichier).
3. Connecter les composants selon le schéma.
4. Lancer le script depuis un terminal ou directement depuis l’IDE MicroPython.

## Utilisation

- Tourner le potentiomètre pour ajuster le volume.
- Appuyer sur le bouton pour basculer entre les deux mélodies.
- La LED s’allume pendant que chaque note est jouée et s’éteint pendant les silences.

## Notes techniques

- Les fréquences des notes sont définies pour un buzzer standard :
  - DO = 1046 Hz, RE = 1175 Hz, MI = 1318 Hz, FA = 1397 Hz, SO = 1568 Hz, LA = 1760 Hz, SI = 1967 Hz.
- Le script utilise des interruptions (`irq`) pour détecter le bouton et changer la mélodie en temps réel.
- La fonction `read_volume()` lit la valeur du potentiomètre et limite le volume maximal à 32768.
- Les fonctions `DO(time)`, `RE(time)`, etc. permettent de jouer chaque note pour une durée donnée.
