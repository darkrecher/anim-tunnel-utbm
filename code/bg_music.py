import os
import pygame
import pygame.mixer

from code.helpers import audio_dir
from code.anim_object import AnimationObject


class BackgroundMusic(AnimationObject):
    """
    Animation Object qui n'affiche rien à l'écran, mais qui joue la musique de fond.
    """

    # Fichier son de la musique à jouer.
    MUSIC_FILE_NAME = "Synthesia_La_Soupe_Aux_Choux_theme.ogg"
    # Volume de la musique. On le met un peu moins forte que les autres sons,
    # parce que c'est censé être juste un fon sonore, et il faut qu'on puisse bien
    # entendre les supers trucs qui sont dits, "déchaine les enfers" et tout ça.
    MUSIC_VOLUME = 0.95
    # Date (en tick d'horloge) à laquelle il faut commencer de jouer la musique.
    DATE_START_PLAY = 100
    # Date (en tick d'horloge) à laquelle il faut baisser progressivement le
    # volume de la musique jusqu'à l'arrêter complètement.
    DATE_FADEOUT_PLAY = 1870
    # Temps (en millisecondes) durant lequel le volume de la musique baisse.
    FADEOUT_DURATION = 500

    # Les différents états possibles de la musique.
    # Je devrais mettre ça dans un enum dédié, mais bon, pfou...
    # Ça va bien comme ça, on va pas faire de l'over-engineering.
    #
    # La musique n'a pas encore été déclenchée
    PLAY_STATE_NOT_STARTED = 0
    # La musique est en train d'être jouée.
    PLAY_STATE_PLAYING = 1
    # La musique est en train de baisser de volume, ou bien elle est totalement arrêtée.
    PLAY_STATE_FINISHED = 2


    def __init__(self):
        """
        Chargement du fichier de musique et adaptation de son volume.
        Définition de la variable membre play_state, qui a pour valeur l'une des
        constantes PLAY_STATE_xxx.
        """
        fullname = os.path.join(audio_dir, BackgroundMusic.MUSIC_FILE_NAME)
        pygame.mixer.music.load(fullname)
        pygame.mixer.music.set_volume(BackgroundMusic.MUSIC_VOLUME)
        self.play_state = BackgroundMusic.PLAY_STATE_NOT_STARTED


    def make_loop_action(self, screen, timer_tick):
        """
        Déclenchement de la musique quand il faut, fadeout et arrêt quand il faut aussi.
        """

        if self.play_state == BackgroundMusic.PLAY_STATE_NOT_STARTED:
            if timer_tick >= BackgroundMusic.DATE_START_PLAY:
                # Déclenchement de la musique de fond.
                pygame.mixer.music.play()
                # Redéfinition de l'état actuel de la musique.
                self.play_state = BackgroundMusic.PLAY_STATE_PLAYING

        elif self.play_state == BackgroundMusic.PLAY_STATE_PLAYING:
            if timer_tick >= BackgroundMusic.DATE_FADEOUT_PLAY:
                # Fadeout de la musique de fond (son volume baisse progressivement).
                # Pas besoin de dire explicitement que la musique doit s'arrêter.
                # La fonction pygame.mixer.music.fadeout s'en occupe, lorsque le volume
                # a été diminué complètement.
                pygame.mixer.music.fadeout(BackgroundMusic.FADEOUT_DURATION)
                # Redéfinition de l'état actuel de la musique.
                # Cette fonction ne fait plus rien lorsque l'état est "FINISHED".
                self.play_state = BackgroundMusic.PLAY_STATE_FINISHED

