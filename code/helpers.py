import os
import pygame
from pygame.compat import geterror

main_dir = os.getcwd()
img_dir = os.path.join(main_dir, "img")
audio_dir = os.path.join(main_dir, "audio")

screen_size_x = 640
screen_size_y = 480


def load_image(name, colorkey=None, use_alpha=False):
    """
    Charge une image à partir d'un fichier.

    Renvoie un tuple :
     - objet pygame.Surface, contenant l'image chargée.
     - objet pygame.Rect, contenant les dimensions (width, height) de l'image.

    Le paramètre colorkey est soit une couleur, soit la valeur -1, soit None.
    None : pas de transparence
    une couleur : tous les pixels ayant cette couleur seront transparents
    -1 : tous les pixels ayant la couleur correspondant au pixel en haut à gauche
         de l'écran seront transparents.

    Le paramètre use_alpha est un booléen.
    False : pas de transparence alpha.
    True : on utilise la transparence alpha stockée dans l'image
           (lorsque l'image est un fichier .png, par exemple).

    Il faut définir la transparence soit via colorkey, soit via use_alpha,
    mais pas avec les deux en même temps.
    """

    if colorkey and use_alpha:
        raise Exception("Soit colorkey, soit use_alpha, mais pas les deux.")
    fullname = os.path.join(img_dir, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print("Cannot load image:", fullname)
        raise SystemExit(str(geterror()))

    if use_alpha:
        image = image.convert_alpha()
    else:
        image = image.convert()

    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)

    return image, image.get_rect()

