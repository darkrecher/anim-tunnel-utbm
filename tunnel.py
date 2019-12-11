import sys
import os
import time
import math
import random
import numpy
import pygame
import pygame.locals
import pygame.surfarray
import pygame.mixer
from pygame.compat import geterror

from code.texture_tunnel import TextureTunnel
from code.black_circle import BlackCircle
from code.white_circle_at_end import WhiteCircleAtEnd

# TODO : in helpers
main_dir = os.path.split(os.path.abspath(__file__))[0]
img_dir = os.path.join(main_dir, "img")

# TODO : in helpers
screen_size_x = 640
screen_size_y = 480



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


# TODO : in helpers
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
        # TODO : ça va planter, ça. On n'a pas de RLEACCEL.
        image.set_colorkey(colorkey, RLEACCEL)

    return image, image.get_rect()


def load_sounds():
    all_sounds = []
    for sound_name, duration, date_play, volume_factor in ALL_SOUNDS:
        sound = pygame.mixer.Sound(os.path.join("audio", sound_name + ".ogg"))
        if volume_factor != 1:
            sound.set_volume(volume_factor)
        all_sounds.append((date_play, sound))
    all_sounds.sort(key=lambda x:x[0])
    return all_sounds


class Boulette():
    # BIG TODO : si on met l'anim en pause, la boulette continue de se déplacer. Woups...

    DEG_TO_RAD_FACTOR = (2*math.pi) / 360

    def __init__(self, boulette_imgs_all):
        self.boulette_imgs_all = boulette_imgs_all
        self.len_boulette_imgs_rot = len(self.boulette_imgs_all[0])
        self.angle = 20.0
        self.dist = 0.0
        self.delta_angle = 0.0
        self.delta_angle_lim = 1.0
        self.delta_dist = 0.0
        self.delta_dist_lim = 0.5
        self.dist_min = 50
        self.dist_max = 100
        self.main_img_counter = 0

    def change_polar_coords(self):
        # TODO : constantes, plize.
        accel_angle = random.randint(-50, 50) / 2000
        self.delta_angle += accel_angle
        if self.delta_angle < -self.delta_angle_lim:
            self.delta_angle -= accel_angle * 45
            #print("lim down", accel_angle, self.delta_angle, self.angle)
        if self.delta_angle > self.delta_angle_lim:
            self.delta_angle -= accel_angle * 45
            #print("lim up", accel_angle, self.delta_angle, self.angle)
        self.angle += self.delta_angle
        if self.angle < 0:
            self.angle += 360
        if self.angle > 360:
            self.angle -= 360

        accel_dist = random.randint(-50, 50) / 1000
        self.delta_dist += accel_dist
        # Du coup: pas de garantie absolu que dist ne va pas sortir de [dist_min, dist_max]
        # Mais osef.
        if self.delta_dist < -self.delta_dist_lim and accel_dist < 0:
            self.delta_dist -= accel_dist / 2
        elif self.dist < self.dist_min and accel_dist < 0:
            self.delta_dist -= accel_dist / 2
        if self.delta_dist > self.delta_dist_lim and accel_dist > 0:
            self.delta_dist -= accel_dist / 2
        elif self.dist > self.dist_max and accel_dist > 0:
            self.delta_dist -= accel_dist / 2
        self.dist += self.delta_dist

        #print(accel_angle, self.delta_angle, self.angle)
        #print(accel_dist, self.delta_dist, self.dist)

        self.main_img_counter += 1
        # TODO : constante, plize.
        if self.main_img_counter >= len(self.boulette_imgs_all) * 50:
            self.main_img_counter = 0

    def get_cartez_coords(self):
        return (
            int(screen_size_x//2 + math.cos(self.angle*Boulette.DEG_TO_RAD_FACTOR)*self.dist),
            int(screen_size_y//2 + math.sin(self.angle*Boulette.DEG_TO_RAD_FACTOR)*self.dist)
        )

    def get_img_and_coords(self):

        # TODO : constante, plize.
        boulette_imgs_current = self.boulette_imgs_all[self.main_img_counter//50]

        index_boulette_rotation = int(((self.angle+7.5) / 360) * self.len_boulette_imgs_rot) % self.len_boulette_imgs_rot
        index_boulette_rotation = self.len_boulette_imgs_rot - index_boulette_rotation - 1
        index_boulette_rotation += self.len_boulette_imgs_rot//4
        if index_boulette_rotation >= self.len_boulette_imgs_rot:
            index_boulette_rotation -= self.len_boulette_imgs_rot

        # TODO : re constantes, plize.
        scale_factor = 0.1 + self.dist / 400
        boulette_rotated, rect_rotated, coord_hotpoint = boulette_imgs_current[
            index_boulette_rotation
        ]
        boulette_scaled = pygame.transform.scale(
            boulette_rotated,
            (int(rect_rotated.w*scale_factor), int(rect_rotated.h*scale_factor))
        )
        boulette_coords = self.get_cartez_coords()
        coord_img_left_up = (
            int(boulette_coords[0] + coord_hotpoint[0]*scale_factor),
            int(boulette_coords[1] + coord_hotpoint[1]*scale_factor)
        )
        return boulette_scaled, coord_img_left_up


def main():

    # Initialize Everything
    random.seed("Des morceaux de l'uuuutééééébéééééhèèèèèème !")
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

    anim_objects = [ black_circle, white_circle_at_end ]

    img_boulette_originals = []

    for img_index in range(1, 6):
        img_boulette, boul_rect = load_image("boulette_0" + str(img_index) + ".png", use_alpha=True)
        boul_rect = pygame.Rect(0, 0, int(boul_rect.w*0.25), int(boul_rect.h*0.25))
        boulette_scaled = pygame.transform.scale(
            img_boulette,
            (boul_rect.w, boul_rect.h),
        )
        img_boulette_originals.append(boulette_scaled)

    print("precalc boulette rotations")
    # TODO : constantes pour le nombre d'image de boulette, et le step de rotation.
    # tuples imbriqués.
    # Chaque elem du tuple le plus haut représente l'une des 6 images possibles de la boulette de papier.
    # C'est un sous-tuple. Chaque elem de ce sous-tuple représente une image rotatée de la boulette.
    # Rotatée à 15 degrés, puis 30, 45, etc. Ce sont des sous-sous-tuple.
    # Le premier elem du sous-sous-tuple est l'image elle-même.
    # Le deuxième est la taille de l'image.
    # Le troisième est le vecteur (x, y) de décalage.
    boulette_imgs_all = []
    for img_boulette_original in img_boulette_originals:
        boulette_imgs = []
        for angle in range(0, 360, 15):
            vect_center_to_middle_down = pygame.math.Vector2(0, boul_rect.h//2)
            # Je sais pas pourquoi faut mettre "-angle" et pas "angle".
            # Sûrement un truc compliqué de matheux.
            vect_center_to_middle_down = vect_center_to_middle_down.rotate(-angle)
            boulette_rotated = pygame.transform.rotate(img_boulette_original, angle)
            rect_rotated = boulette_rotated.get_rect()
            coord_hotpoint = (
                -rect_rotated.w//2 - vect_center_to_middle_down.x,
                -rect_rotated.h//2 - vect_center_to_middle_down.y
            )
            boulette_imgs.append((boulette_rotated, rect_rotated, coord_hotpoint))
        boulette_imgs_all.append(boulette_imgs)

    pygame.display.flip()

    clock = pygame.time.Clock()
    going = True
    pause = False
    boulette = Boulette(boulette_imgs_all)

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

        texture_tunnel.make_loop_action(screen, timer_tick)

        # Gestion de la boulette de papier.
        boulette.change_polar_coords()
        boulette_scaled, coord_img_left_up = boulette.get_img_and_coords()
        screen.blit(boulette_scaled, (coord_img_left_up[0], coord_img_left_up[1]))

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
