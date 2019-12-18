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
from code.sounds import Sounds
from code.bg_music import BackgroundMusic


def main():

    # Initialize Everything
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((screen_size_x, screen_size_y), pygame.NOFRAME)
    pygame.display.set_caption("Tunnel 3D")
    pygame.mouse.set_visible(0)

    timer_tick = 0

    print("precalculating 'texture tunnel'.")
    texture_tunnel = TextureTunnel()
    print("precalculating 'black circle'.")
    black_circle = BlackCircle()
    print("precalculating 'white circle for the end'.")
    white_circle_at_end = WhiteCircleAtEnd()
    print("precalculating 'the boulette'.")
    boulette = Boulette()
    print("precalculating 'background music'.")
    background_music = BackgroundMusic()
    print("precalculating 'sounds'.")
    sounds = Sounds()

    anim_objects = [
        texture_tunnel,
        boulette,
        black_circle,
        white_circle_at_end,
        background_music,
        sounds,
    ]

    pygame.display.flip()

    clock = pygame.time.Clock()
    going = True
    pause = False

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

    pygame.quit()


if __name__ == "__main__":
    main()
