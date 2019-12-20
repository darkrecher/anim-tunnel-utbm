import sys
import time
import pygame
import pygame.locals
import pygame.mixer

from code.helpers import screen_size_x, screen_size_y
from code.texture_tunnel import TextureTunnel
from code.black_circle import BlackCircle
from code.white_circle_at_end import WhiteCircleAtEnd
from code.boulette import Boulette
from code.sounds import Sounds
from code.bg_music import BackgroundMusic


def main():
    """
    Fonction principale, qui initialise pygame, crée tous les AnimationObject
    et les fait avancer dans une loop.

    L'animation n'est pas déclenchée tout de suite dès le lancement du script,
    on attend 10 secondes. Le décompte s'affiche dans la sortie standard.

    J'avais besoin de ce temps d'attente, pour déclencher correctement
    l'enregistrement de l'animation dans un fichier vidéo.

    Cette fonction récupère le premier paramètre passé en ligne de commande
    (si il est présent), et l'utilise comme temps d'attente, en secondes.
    Si pas de paramètre, c'est 10 secondes par défaut.

    Pour lancer sans temps d'attente, il faut exécuter la commande :
    python tunnel.py 0

    Il est possible de mettre en pause l'animation en appuyant sur la touche espace.
    Mais ça ne marche pas super bien, car la musique continue d'être jouée, ainsi
    que le son en cours de jeu si il y en a un.
    Je n'ai ni le temps ni l'envie de corriger ça, donc ça va rester ainsi. Désolé !

    La touche Esc permet de quitter l'animation.
    """

    # Initialisation de tout ce qu'il faut.
    pygame.init()
    pygame.mixer.init()
    # On crée une fenêtre pour afficher l'animation, mais sans les bordures standard.
    # C'est pas pratique, car on ne peut pas bouger la fenêtre, ni cliquer sur la
    # croix pour la fermer,
    screen = pygame.display.set_mode((screen_size_x, screen_size_y), pygame.NOFRAME)
    pygame.display.set_caption("Tunnel 3D")
    pygame.mouse.set_visible(0)

    # Chargement et init des AnimationObject. On logge à chaque fois, car certains
    # prennent un peu de temps.
    print("loading 'texture tunnel'.")
    texture_tunnel = TextureTunnel()
    print("loading 'black circle'.")
    black_circle = BlackCircle()
    print("loading 'white circle for the end'.")
    white_circle_at_end = WhiteCircleAtEnd()
    print("loading 'the boulette'.")
    boulette = Boulette()
    print("loading 'background music'.")
    background_music = BackgroundMusic()
    print("loading 'sounds'.")
    sounds = Sounds()

    # Liste de tous les AnimationObjects à gérer pour l'animation.
    anim_objects = [
        texture_tunnel,
        boulette,
        black_circle,
        white_circle_at_end,
        background_music,
        sounds,
    ]

    # Objet pygame gérant le temps. Il s'arrange au mieux pour exécuter
    # la main loop 50 fois par seconde.
    clock = pygame.time.Clock()
    # Indique si l'utilisateur veut arrêter l'animation.
    playing_anim = True
    # Indique si l'utilisateur a mis en pause.
    pause = False

    if len(sys.argv) > 1:
        # Ça va planter si le param de ligne de commande n'est pas convertible en int.
        # Osef. C'est pas le script du siècle et si il est pas totalement secure
        # c'est pas un drame.
        seconds = abs(int(sys.argv[1]))
    else:
        # Valeur par défaut si le param n'est pas spécifié.
        seconds = 10

    # Attente du nombre de secondes.
    print("Ready. On va déclencher l'anim dans %s secondes." % seconds)
    while seconds:
        print(seconds)
        time.sleep(1)
        seconds -= 1

    print("start")
    # timer_tick est la variable comptant le nombre de cycle d'horloge
    # (Il y a 50 cycles par secondes).
    # Cette variable est transmise à tous les AnimationObject,
    # pour qu'ils puisse se gérer et faire avancer leur état interne.
    timer_tick = 0

    while playing_anim:

        # La fonction pour que la game loop s'exécute 50 fois par secondes.
        clock.tick(50)

        # Gestion des événements d'input : les touches et la fermeture de la fenêtre.
        for event in pygame.event.get():
            # Fermeture de la fenêtre, on doit arrêter l'anim.
            if event.type == pygame.locals.QUIT:
                playing_anim = False
            elif event.type == pygame.locals.KEYDOWN:
                # Appui sur la touche Esc, on doit arrêter l'anim.
                if event.key == pygame.locals.K_ESCAPE:
                    playing_anim = False
                # Appui sur la touche Espace, on met en pause.
                if event.key == pygame.locals.K_SPACE:
                    pause = not pause

        if not pause:
            # Je voulais mettre ce "1" en constante, pour qu'on puisse jouer l'animation
            # plus ou moins rapidement. Mais certains AnimationObject (en particulier
            # celui gérant la boulette de papier) ne savent pas gérer correctement des
            # modifications de timer_tick plus grande que 1.
            # Donc tant pis, je laisse tomber, ça reste à 1 et on ne peut pas mettre
            # autre chose.
            timer_tick += 1
            # On fait avancer l'état de tous les anims objects, et on déclenche leurs
            # actions (affichage d'images, sons, musiques, ...)
            for anim_object in anim_objects:
                anim_object.make_loop_action(screen, timer_tick)

        # Gestion du double buffer d'affichage. On affiche réellement dans la fenêtre
        # l'image qu'on a préparé sur la surface "screen".
        # Voir doc de pygame pour plus d'infos.
        pygame.display.flip()

    # Libération de toutes les ressources de pygame, fermeture de la fenêtre, etc.
    pygame.quit()


if __name__ == "__main__":
    main()
