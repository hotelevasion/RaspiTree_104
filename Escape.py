#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import datetime
import lgpio
import os
import threading
import pygame

# Configuration des broches GPIO
SENSOR_PINS = [5, 6, 7, 8, 9, 10, 11, 12]
# PAUME_PIN = 18  # Pin pour la détection de la paume (commentée)
OUTPUT_PINS = [2, 3, 4, 27]
PORTE_PIN = 19

# Initialiser pygame mixer
pygame.mixer.init()

# Variable globale pour le handle du chip GPIO
gpio_chip_handle = None
aimants = [0] * len(SENSOR_PINS)

# Précharger les fichiers audio
sound_files = {
    'CrystalIN1': pygame.mixer.Sound('/home/pi/sound/CrystalIN1.wav'),
    'CrystalOUT1': pygame.mixer.Sound('/home/pi/sound/CrystalOUT1.wav'),
    'CrystalIN2': pygame.mixer.Sound('/home/pi/sound/CrystalIN2.wav'),
    'CrystalOUT2': pygame.mixer.Sound('/home/pi/sound/CrystalOUT2.wav'),
    'CrystalIN3': pygame.mixer.Sound('/home/pi/sound/CrystalIN3.wav'),
    'CrystalOUT3': pygame.mixer.Sound('/home/pi/sound/CrystalOUT3.wav'),
    'CrystalIN4': pygame.mixer.Sound('/home/pi/sound/CrystalIN4.wav'),
    'CrystalOUT4': pygame.mixer.Sound('/home/pi/sound/CrystalOUT4.wav'),
    'CrystalVictory': pygame.mixer.Sound('/home/pi/sound/CrystalVictory.wav')
}

def sensor_callback(chip, gpio, level, tick):
    global gpio_chip_handle, aimants
    sensor_index = SENSOR_PINS.index(gpio)
    timestamp = time.time()
    stamp = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
    if lgpio.gpio_read(gpio_chip_handle, gpio) == 0:
        #print(f"sensor {gpio} LOW {stamp}")
        aimants[sensor_index] = 1
    else:
        #print(f"sensor {gpio} HIGH {stamp}")
        aimants[sensor_index] = 0

def setup_gpio():
    global gpio_chip_handle
    gpio_chip_handle = lgpio.gpiochip_open(0)  # Ouvre le chip 0 (par défaut pour les Raspberry Pi)

    for pin in SENSOR_PINS:  # Commenté : + [PAUME_PIN]
        lgpio.gpio_claim_input(gpio_chip_handle, pin)
        lgpio.gpio_set_debounce_micros(gpio_chip_handle, pin, 200000)
        lgpio.gpio_claim_alert(gpio_chip_handle, pin, lgpio.BOTH_EDGES)
        lgpio.callback(gpio_chip_handle, pin, lgpio.BOTH_EDGES, sensor_callback)

    for pin in OUTPUT_PINS + [PORTE_PIN]:
        lgpio.gpio_claim_output(gpio_chip_handle, pin)

    # Initial readings
    for pin in SENSOR_PINS:
        sensor_callback(gpio_chip_handle, pin, 0, 0)

def cleanup_gpio():
    global gpio_chip_handle
    lgpio.gpiochip_close(gpio_chip_handle)

def play_sound(sound):
    sound.play()

def play_sound_thread(sound_name):
    sound = sound_files.get(sound_name)
    if sound:
        threading.Thread(target=play_sound, args=(sound,)).start()
    else:
        print(f"Audio file {sound_name} not found")

def main():
    global aimants
    setup_gpio()

    etatcrystal1 = 0
    etatcrystal2 = 0
    etatcrystal3 = 0
    etatcrystal4 = 0
    son1 = 0
    son2 = 0
    son3 = 0
    son4 = 0
    sonOut1 = 0
    sonOut2 = 0
    sonOut3 = 0
    sonOut4 = 0
    codeCrystal = "0000"

    text_file = open("/var/www/html/SerialLog.txt", "w+")
    text_file.write("ready\n")
    text_file.close()

    try:
        while True:
            time.sleep(0.1)

            # Crystal 1
            if aimants[0] == 1 or aimants[1] == 1:
                etatcrystal1 = 1
                lgpio.gpio_write(gpio_chip_handle, 2, 1)
                if son1 == 0:
                    play_sound_thread('CrystalIN1')
                    son1 = 1
                    sonOut1 = 0
                    codeCrystal = codeCrystal[0:3] + "1"
            else:
                etatcrystal1 = 0
                lgpio.gpio_write(gpio_chip_handle, 2, 0)
                son1 = 0
                if sonOut1 == 0:
                    play_sound_thread('CrystalOUT1')
                    sonOut1 = 1

            # Crystal 2
            if aimants[2] == 1 or aimants[3] == 1:
                etatcrystal2 = 1
                lgpio.gpio_write(gpio_chip_handle, 3, 1)
                if son2 == 0:
                    play_sound_thread('CrystalIN2')
                    son2 = 1
                    sonOut2 = 0
                    codeCrystal = codeCrystal[0:2] + "2" + codeCrystal[3]
            else:
                etatcrystal2 = 0
                lgpio.gpio_write(gpio_chip_handle, 3, 0)
                son2 = 0
                if sonOut2 == 0:
                    play_sound_thread('CrystalOUT2')
                    sonOut2 = 1

            # Crystal 3
            if aimants[4] == 1 or aimants[5] == 1:
                etatcrystal3 = 1
                lgpio.gpio_write(gpio_chip_handle, 4, 1)
                if son3 == 0:
                    play_sound_thread('CrystalIN3')
                    son3 = 1
                    sonOut3 = 0
                    codeCrystal = codeCrystal[0:1] + "3" + codeCrystal[2:]
            else:
                etatcrystal3 = 0
                lgpio.gpio_write(gpio_chip_handle, 4, 0)
                son3 = 0
                if sonOut3 == 0:
                    play_sound_thread('CrystalOUT3')
                    sonOut3 = 1

            # Crystal 4
            if aimants[6] == 1 or aimants[7] == 1:
                etatcrystal4 = 1
                lgpio.gpio_write(gpio_chip_handle, 27, 1)
                if son4 == 0:
                    play_sound_thread('CrystalIN4')
                    son4 = 1
                    sonOut4 = 0
                    codeCrystal = "4" + codeCrystal[1:]
            else:
                etatcrystal4 = 0
                lgpio.gpio_write(gpio_chip_handle, 27, 0)
                son4 = 0
                if sonOut4 == 0:
                    play_sound_thread('CrystalOUT4')
                    sonOut4 = 1

            # Condition de victoire
            if (aimants[0] == 1 and aimants[1] == 1 and
                aimants[2] == 1 and aimants[3] == 1 and
                aimants[4] == 1 and aimants[5] == 1 and
                aimants[6] == 1 and aimants[7] == 1):
                print("Playing CrystalVictory sound")
                play_sound_thread('CrystalVictory')
                lgpio.gpio_write(gpio_chip_handle, 19, 1)
                #print("Porte activée")
            else:
                lgpio.gpio_write(gpio_chip_handle, 19, 0)
                #print("Porte désactivée")

    except KeyboardInterrupt:
        print("Exiting program")
    finally:
        cleanup_gpio()

if __name__ == '__main__':
    main()
