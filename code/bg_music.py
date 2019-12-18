import os
import pygame
import pygame.mixer

from code.anim_object import AnimationObject


class BackgroundMusic(AnimationObject):
    """
    TODO : à expliquer, mais c'est assez simple.
    """


    def __init__(self):
        """
        """
        # Déclenchement de la musique de fond.
        pygame.mixer.music.load("audio\\Synthesia_La_Soupe_Aux_Choux_theme.ogg")
        pygame.mixer.music.set_volume(0.95)



    def make_loop_action(self, screen, timer_tick):
        """
        """
        # TODO : ajouter une constante pour ces nombres, please.
        if timer_tick == 100:
            pygame.mixer.music.play()

        if timer_tick == 1870:
            pygame.mixer.music.fadeout(500)



