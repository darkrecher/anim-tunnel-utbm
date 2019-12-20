import os
import pygame
import pygame.mixer

from code.helpers import audio_dir
from code.anim_object import AnimationObject


class Sounds(AnimationObject):
    """
    Animation Object qui n'affiche rien à l'écran, mais qui joue les sons
    aux bons moments.
    La musique de fond (celle de la soupe aux choux) n'est pas gérée par cet AnimObject,
    celui-ci ne joue que les sons de blablatage.
    """

    # Liste des sons à jouer.
    # Tuple dont chaque élément est un sous-tuple de 4 éléments :
    #  - nom du fichier .ogg
    #  - durée du son (en secondes)
    #  - date (en tick d'horloge de l'anim) à laquelle il faut le jouer
    #  - facteur de volume
    #
    # Si j'ai bien compris coment fonctionne pygame.mixer, on ne peut modifier le
    # volume d'un son que en le mettant moins fort, pas plus fort.
    # Donc le facteur de volume doit être compris entre 0 et 1. Si on met plus que 1,
    # ça ne change rien.
    # Ce facteur de volume permet d'équilibrer les sons entre eux, par exemple si l'un
    # d'eux est trop fort par rapport aux autres.
    #
    # Le deuxième élément (durée du son en secondes) n'est pas utilisé dans le code,
    # mais je l'ai laissé à titre indicatif, et j'en avais besoin pour vérifier que
    # les sons n'allaient pas se chevaucher.
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


    def __init__(self):
        """
        Chargement des fichiers sons, et rangement dans la variable membre all_sounds.
        all_sounds est une liste de tuple de 2 éléments :
         - la date à laquelle il faut jouer le son (en tick d'horloge),
         - le son à jouer (objet pygame.mixer.Sound).
        Cette liste est triée par ordre croissant de date.
        """
        all_sounds = []

        for sound_name, duration, date_play, volume_factor in Sounds.ALL_SOUNDS:
            fullname = os.path.join(audio_dir, sound_name + ".ogg")
            sound = pygame.mixer.Sound(fullname)
            if volume_factor != 1:
                sound.set_volume(volume_factor)
            all_sounds.append((date_play, sound))

        # Tri par ordre croissant du premier élément de chaque tuple,
        # c'est à dire la date du son.
        all_sounds.sort(key=lambda x:x[0])
        self.all_sounds = all_sounds


    def make_loop_action(self, screen, timer_tick):
        """
        Lancement des sons, en fonction de la date actuelle de l'anim (timer_tick).
        Come la variable all_sounds est triée par date, il suffit de vérifier uniquement
        le premier élément. Si c'est le moment de jouer le son, on le joue, et on
        l'enlève de la liste. Il suffira ensuite de ne vérifier à nouveau que le
        premier élément.
        """
        # On met quand même dans une boucle la vérification du premier élément,
        # comme ça, si plusieurs sons doivent être joués exactement à la même date,
        # ils le seront.
        while self.all_sounds and self.all_sounds[0][0] < timer_tick:
            date_play, current_sound = self.all_sounds.pop(0)
            current_sound.play()
