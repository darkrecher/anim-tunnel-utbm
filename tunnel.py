import os
import math
import numpy
import pygame
import pygame.locals
import pygame.surfarray
import pygame.mixer
from pygame.compat import geterror


main_dir = os.path.split(os.path.abspath(__file__))[0]
img_dir = os.path.join(main_dir, "img")

screen_size_x = 640
screen_size_y = 480

tunnel_diameter = 300
dist_focale = 100

# Liste des sons. Sous-tuple de 3 éléments :
#  - nom du fichier .wav
#  - durée du son (en secondes)
#  - date (en tick de jeu) à laquelle il faut le jouer
ALL_SOUNDS = (
    ("partout_univers", 1.916, 50),
    ("pere200_1", 7.561, 600),
    ("dechaine_les_enfers", 2.337, 200),
    ("tu_n_a_pas_eu_tes_bn", 2.224, 350),
    ("morceaux_utbm", 9.954, 1950),
)


def load_image(name, colorkey=None, use_alpha=False):

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
        image.set_colorkey(colorkey, RLEACCEL)

    return image, image.get_rect()


def cylinder_coords_from_screen_coords(pix_x, pix_y):
    a_x = pix_x - screen_size_x / 2
    a_y = pix_y - screen_size_y / 2
    if (a_x, a_y) == (0, 0):
        raise ValueError(
            "La coordonnée du milieu de l'écran ne peut pas atteindre le cylindre"
        )
    # https://stackoverflow.com/questions/15994194/how-to-convert-x-y-coordinates-to-an-angle
    angle = math.atan2(a_y, a_x)
    cylinder_z = dist_focale * tunnel_diameter / (math.sqrt(a_x ** 2 + a_y ** 2))
    return angle, cylinder_z


def tex_coord_from_screen_coords(pix_x, pix_y, texture_width, texture_height):
    try:
        angle, cylinder_z = cylinder_coords_from_screen_coords(pix_x, pix_y)
    except ValueError:
        return (0, 0)
    tex_x = int(cylinder_z % texture_width)
    tex_y = int(((angle + math.pi) * (texture_height - 1)) / (2 * math.pi))
    # on décale tout de un cinquième, pour que le raccord moche entre
    # le haut et le bas de l'image ne soit pas pil poil sur la partie gauche du tunnel.
    tex_y = (tex_y + texture_height // 5) % texture_height
    return (tex_x, tex_y)


def load_sounds():
    all_sounds = [
        (
            date_play,
            pygame.mixer.Sound(os.path.join("audio", sound_name+".wav")),
        ) for sound_name, duration, date_play
        in ALL_SOUNDS
    ]
    all_sounds.sort(key=lambda x:x[0])
    return all_sounds


def main():

    # Initialize Everything
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((screen_size_x, screen_size_y))
    pygame.display.set_caption("Tunnel 3D")
    pygame.mouse.set_visible(0)

    all_sounds = load_sounds()
    print(all_sounds)

    texture, texture_rect = load_image("texture.png")
    texture_width = texture_rect.w
    texture_height = texture_rect.h

    array_texture_origin = pygame.surfarray.array2d(texture)
    # TODO : euh... y'a vraiment besoin de copier ?
    array_texture = array_texture_origin.copy()

    timer_tick = 0

    fond_noir, fond_noir_rect = load_image("fond_noir.png", use_alpha=True)
    coord_fond_noir = (
        (screen_size_x - fond_noir_rect.w) // 2,
        (screen_size_y - fond_noir_rect.h) // 2,
    )

    # Si la taille (width ou height) de l'image de texture ne tient pas
    # dans un int 32 bits, ça va péter. Mais franchement osef.
    screen_from_tunnel_x = numpy.zeros((screen_size_x, screen_size_y), dtype="u4")
    screen_from_tunnel_y = numpy.zeros((screen_size_x, screen_size_y), dtype="u4")

    for x in range(screen_size_x):
        for y in range(screen_size_y):
            tex_coords = tex_coord_from_screen_coords(
                x, y, texture_width, texture_height
            )
            screen_from_tunnel_x[x, y] = tex_coords[0]
            screen_from_tunnel_y[x, y] = tex_coords[1]

    # TODO : duplicate code avec la main loop. De plus, j'affiche pas le fond noir.
    # Bref, beurk, à homogénéiser.
    pygame.surfarray.blit_array(
        screen,
        array_texture[
            (screen_from_tunnel_x + 10) % texture_width, screen_from_tunnel_y
        ],
    )
    pygame.display.flip()

    clock = pygame.time.Clock()
    going = True
    pause = False

    while going:

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

        pygame.surfarray.blit_array(
            screen,
            array_texture[
                (screen_from_tunnel_x + (timer_tick * 4)) % texture_width,
                screen_from_tunnel_y,
            ],
        )
        screen.blit(fond_noir, coord_fond_noir)
        pygame.display.flip()

        while all_sounds and all_sounds[0][0] < timer_tick:
            date_play, current_sound = all_sounds.pop(0)
            current_sound.play()

    pygame.quit()


if __name__ == "__main__":
    main()
