import os
import pygame
import pygame.mixer

from code.anim_object import AnimationObject


class Sounds(AnimationObject):
    """
    TODO : à expliquer, mais c'est assez simple.
    """

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


    def _load_sounds(self):
        # TODO : mot "audio" dans une constante.
        all_sounds = []
        for sound_name, duration, date_play, volume_factor in Sounds.ALL_SOUNDS:
            sound = pygame.mixer.Sound(os.path.join("audio", sound_name + ".ogg"))
            if volume_factor != 1:
                sound.set_volume(volume_factor)
            all_sounds.append((date_play, sound))
        all_sounds.sort(key=lambda x:x[0])
        self.all_sounds = all_sounds


    def __init__(self):
        """
        """
        self._load_sounds()


    def make_loop_action(self, screen, timer_tick):
        """
        """
        while self.all_sounds and self.all_sounds[0][0] < timer_tick:
            date_play, current_sound = self.all_sounds.pop(0)
            current_sound.play()


