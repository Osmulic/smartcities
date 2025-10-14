# Contrôle de LED avec Bouton et Animation

Ce projet permet de contrôler une LED à l'aide d'un bouton poussoir, avec différentes fréquences et une animation visuelle lors de certains changements d'état.

## Matériel requis

- Microcontrôleur compatible MicroPython (ex. Raspberry Pi Pico)
- LED
- Bouton poussoir
- Fils de connexion et breadboard

## Schéma de câblage

- **LED** → Pin 18  
- **Bouton** → Pin 16

## Fonctionnalités

- Compteur qui s’incrémente à chaque pression du bouton (0 → 7 puis revient à 0).
- Différentes fréquences de clignotement de la LED selon la valeur du compteur :
  - 0 : LED éteinte
  - 2 : clignotement à 2 Hz
  - 4 : clignotement à 5 Hz
  - 6 : clignotement à 15 Hz
- Animation spéciale (flash rapide) lorsque le compteur atteint 0, 2, 4 ou 6.
- Affichage de la valeur du compteur dans la console.

## Installation

1. Flasher MicroPython sur votre microcontrôleur.
2. Copier le script Python sur la carte (`main.py` ou un autre nom de fichier).
3. Connecter les composants selon le schéma.
4. Lancer le script depuis un terminal ou directement depuis l’IDE MicroPython.

## Utilisation

- Appuyer sur le bouton pour incrémenter le compteur.
- La LED s’allume ou clignote en fonction de la valeur du compteur.
- Lorsque le compteur est sur 0, 2, 4 ou 6, une animation rapide de la LED est jouée.

## Notes techniques

- Le script utilise une interruption (`irq`) pour détecter les pressions du bouton en temps réel.
- La fonction `animation()` fait clignoter rapidement la LED 5 fois pour signaler certains états.
- La fréquence de clignotement est ajustée dynamiquement selon la valeur du compteur.
