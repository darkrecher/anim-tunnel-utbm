import sys
import os
import time
import math
import numpy
import pygame
import pygame.locals
import pygame.surfarray
import pygame.mixer
from pygame.compat import geterror

from code.helpers import screen_size_x, screen_size_y
from code.texture_tunnel import TextureTunnel
from code.black_circle import BlackCircle
from code.white_circle_at_end import WhiteCircleAtEnd
from code.boulette import Boulette


# Liste des sons. Sous-tuple de 3 éléments :
#  - nom du fichier .wav
#  - durée du son (en secondes)
#  - date (en tick de jeu) à laquelle il faut le jouer
#  - facteur de volume
ALL_SOUNDS = (
    ("partout_univers", 1.916, 5, 1),
    ("vous_elite", 2.435, 210, 10000),
    ("dechaine_les_enfers", 2.337, 360, 1),
    ("bar_ouvert", 1.488, 510, 0.5),
    ("pere200", 7.561, 590, 1),
    ("eni_ou_ipse", 2.363, 990, 1),
    ("tu_n_a_pas_eu_tes_bn", 2.224, 1150, 1),
    ("vous_nuls", 2.453, 1300, 1),
    ("pas_uv_pas_deutec", 4.058, 1430, 1),
    ("la_boheme", 4.789, 1640, 1),
    ("morceaux_utbm", 9.954, 1900, 1),
)


def load_sounds():
    all_sounds = []
    for sound_name, duration, date_play, volume_factor in ALL_SOUNDS:
        sound = pygame.mixer.Sound(os.path.join("audio", sound_name + ".ogg"))
        if volume_factor != 1:
            sound.set_volume(volume_factor)
        all_sounds.append((date_play, sound))
    all_sounds.sort(key=lambda x:x[0])
    return all_sounds


def main():

    # Initialize Everything
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((screen_size_x, screen_size_y), pygame.NOFRAME)
    pygame.display.set_caption("Tunnel 3D")
    pygame.mouse.set_visible(0)

    all_sounds = load_sounds()

    timer_tick = 0

    print("precalculating 'texture tunnel'.")
    texture_tunnel = TextureTunnel()
    print("precalculating 'black circle'.")
    black_circle = BlackCircle()
    print("precalculating 'white circle for the end'.")
    white_circle_at_end = WhiteCircleAtEnd()
    print("precalculating 'the boulette'.")
    boulette = Boulette()

    anim_objects = [ texture_tunnel, boulette, black_circle, white_circle_at_end ]

    pygame.display.flip()

    clock = pygame.time.Clock()
    going = True
    pause = False

    # Déclenchement de la musique de fond.
    pygame.mixer.music.load("audio\\Synthesia_La_Soupe_Aux_Choux_theme.ogg")
    pygame.mixer.music.set_volume(0.95)

    if len(sys.argv) > 1:
        # Ça va planter si on passe en paramètre une chaîne qui n'est pas convertible
        # en int. Osef.
        seconds = abs(int(sys.argv[1]))
    else:
        seconds = 10

    print("Ready. Balancer l'enregistrement dans %s secondes." % seconds)
    while seconds:
        print(seconds)
        time.sleep(1)
        seconds -= 1
    print("start loop")

    while going:

        # BIG TODO : si on met l'anim en pause, la boulette continue de se déplacer. Woups...

        clock.tick(50)

        # Gestion des événements d'input (les touches, et la fermeture de la fenêtre)
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                going = False
            elif event.type == pygame.locals.KEYDOWN:
                if event.key == pygame.locals.K_ESCAPE:
                    going = False
                if event.key == pygame.locals.K_SPACE:
                    pause = not pause

        # TODO : c'est un peu à l'arrache tout ça. Faudrait des constantes
        # pour configurer plus clairement la vitesse d'avancée du tunnel
        # et les dates de jeu des sons.
        if not pause:
            timer_tick += 1

        for anim_object in anim_objects:
            anim_object.make_loop_action(screen, timer_tick)

        pygame.display.flip()

        while all_sounds and all_sounds[0][0] < timer_tick:
            date_play, current_sound = all_sounds.pop(0)
            current_sound.play()

        # TODO : ajouter une constante pour ces nombres, please.
        if timer_tick == 100:
            pygame.mixer.music.play()

        if timer_tick == 1870:
            pygame.mixer.music.fadeout(500)

    pygame.quit()


if __name__ == "__main__":
    main()
