import math
import random
import pygame

from code.helpers import load_image, screen_size_x, screen_size_y
from code.anim_object import AnimationObject


class Boulette(AnimationObject):
    # BIG TODO : si on met l'anim en pause, la boulette continue de se déplacer. Woups...

    DEG_TO_RAD_FACTOR = (2*math.pi) / 360

    IMG_ORIGINAL_SCALE_DIVISOR = 4

    # Il faut mettre un diviseur de 360, sinon ça ne va pas tomber juste.
    IMG_ROTATION_PRECISION = 15

    NB_IMG_BOULETTES = 5

    ANGLE_START = 20.0

    # Distance min et max, en pixels, entre le centre de l'écran et la boulette.
    DIST_MIN = 50
    DIST_MAX = 100

    DELTA_ANGLE_MAX = 1.0
    DELTA_DIST_MAX = 0.5

    ACCEL_ANGLE_SEMI_AMPLITUDE = 50
    ACCEL_DIST_SEMI_AMPLITUDE = 50
    ACCEL_ANGLE_DIVISOR = 500
    ACCEL_DIST_DIVISOR = 1000

    ACCEL_ANGLE_LIMITING_FACTOR = 1
    ACCEL_DIST_LIMITING_FACTOR = 0.5

    IMG_COUNTER_PERIOD = 50

    SCALE_FACTOR_OFFSET = 0.1
    SCALE_FACTOR_DIVISOR = 400


    def __init__(self):

        img_boulette_originals = []

        for img_index in range(Boulette.NB_IMG_BOULETTES):

            filename_img = "boulette_0" + str(img_index + 1) + ".png"
            img_boulette, boul_rect = load_image(filename_img, use_alpha=True)

            boulette_scaled = pygame.transform.scale(
                img_boulette,
                (
                    boul_rect.w // Boulette.IMG_ORIGINAL_SCALE_DIVISOR,
                    boul_rect.h // Boulette.IMG_ORIGINAL_SCALE_DIVISOR
                ),
            )
            img_boulette_originals.append(boulette_scaled)

        # tuples imbriqués.
        # Chaque elem du tuple le plus haut représente l'une des 6 images possibles de la boulette de papier.
        # C'est un sous-tuple. Chaque elem de ce sous-tuple représente une image rotatée de la boulette.
        # Rotatée à 15 degrés, puis 30, 45, etc. Ce sont des sous-sous-tuple.
        # Le premier elem du sous-sous-tuple est l'image elle-même.
        # Le deuxième est la taille de l'image.
        # Le troisième est le vecteur (x, y) de décalage.
        self.boulette_imgs_all = []

        for img_boulette_original in img_boulette_originals:
            boulette_imgs = []
            for angle in range(0, 360, Boulette.IMG_ROTATION_PRECISION):
                vect_center_to_middle_down = pygame.math.Vector2(
                    0,
                    (boul_rect.h // Boulette.IMG_ORIGINAL_SCALE_DIVISOR) // 2
                )
                # Je sais pas pourquoi faut mettre "-angle" et pas "angle".
                # Sûrement un truc compliqué de matheux.
                vect_center_to_middle_down = vect_center_to_middle_down.rotate(-angle)
                boulette_rotated = pygame.transform.rotate(img_boulette_original, angle)
                rect_rotated = boulette_rotated.get_rect()
                coord_hotpoint = (
                    -rect_rotated.w // 2 - vect_center_to_middle_down.x,
                    -rect_rotated.h // 2 - vect_center_to_middle_down.y
                )
                boulette_imgs.append((boulette_rotated, rect_rotated, coord_hotpoint))
            self.boulette_imgs_all.append(boulette_imgs)

        self.nb_rotation_img = len(self.boulette_imgs_all[0])

        # On sépare l'état random de la boulette de l'état random de tout le reste.
        # Comme ça les nombres aléatoires des déplacements de la boulette sont gérés
        # indépendamment du reste.
        # Ça sert à rien car aucun autre AnimObject n'utilise le random,
        # mais ça fait classe.
        other_state = random.getstate()
        random.seed("Des morceaux de l'uuuutééééébéééééhèèèèèème !")
        self.my_randgen_state = random.getstate()
        random.setstate(other_state)

        self.angle = Boulette.ANGLE_START
        # On fait exprès de partir d'une distance de 0: le centre de l'écran.
        # Au début, la boulette va progressivement s'éloigner de l'écran, pour arriver
        # jusqu'à self.dist == Boulette.DIST_MIN
        self.dist = 0.0
        self.delta_angle = 0.0
        self.delta_dist = 0.0
        self.img_counter = 0
        self.main_img_index = 0


    def _update_polar_coords(self):

        other_state = random.getstate()
        random.setstate(self.my_randgen_state)
        a_amp = Boulette.ACCEL_ANGLE_SEMI_AMPLITUDE
        accel_angle = random.randint(-a_amp, a_amp) / Boulette.ACCEL_ANGLE_DIVISOR
        d_amp = Boulette.ACCEL_DIST_SEMI_AMPLITUDE
        accel_dist = random.randint(-d_amp, d_amp) / Boulette.ACCEL_DIST_DIVISOR
        self.my_randgen_state = random.getstate()
        random.setstate(other_state)

        if any((
            self.delta_angle < -Boulette.DELTA_ANGLE_MAX and accel_angle < 0,
            self.delta_angle > Boulette.DELTA_ANGLE_MAX and accel_angle > 0,
        )):
            accel_angle = -accel_angle * Boulette.ACCEL_ANGLE_LIMITING_FACTOR

        self.delta_angle += accel_angle
        self.angle += self.delta_angle
        if self.angle < 0: self.angle += 360
        if self.angle > 360: self.angle -= 360

        self.delta_dist += accel_dist
        # Du coup: pas de garantie absolue que dist ne va pas sortir de
        # [dist_min, dist_max]. Mais osef.
        if any((
            self.delta_dist < -Boulette.DELTA_DIST_MAX and accel_dist < 0,
            self.dist < Boulette.DIST_MIN and accel_dist < 0,
            self.delta_dist > Boulette.DELTA_DIST_MAX and accel_dist > 0,
            self.dist > Boulette.DIST_MAX and accel_dist > 0,
        )):
            self.delta_dist -= accel_dist * Boulette.ACCEL_DIST_LIMITING_FACTOR

        self.dist += self.delta_dist


    def _update_main_img_counter(self):

        self.img_counter += 1
        if self.img_counter >= Boulette.IMG_COUNTER_PERIOD:
            self.img_counter = 0
            self.main_img_index += 1
            if self.main_img_index >= len(self.boulette_imgs_all):
                self.main_img_index = 0


    def _get_cartez_coords(self):
        angle_radian = self.angle * Boulette.DEG_TO_RAD_FACTOR
        return (
            int(screen_size_x // 2 + math.cos(angle_radian) * self.dist),
            int(screen_size_y // 2 + math.sin(angle_radian) * self.dist)
        )


    def _get_img_and_coords(self):

        boulette_imgs_current = self.boulette_imgs_all[self.main_img_index]
        # TODO : va falloir expliquer ce bazar.
        adjusted_angle = 360 - self.angle + Boulette.IMG_ROTATION_PRECISION / 2 + 90

        index_boulette_rotation = int((adjusted_angle * self.nb_rotation_img) / 360)
        if index_boulette_rotation >= self.nb_rotation_img:
            index_boulette_rotation -= self.nb_rotation_img

        scale_factor = (
            Boulette.SCALE_FACTOR_OFFSET + self.dist / Boulette.SCALE_FACTOR_DIVISOR
        )
        boulette_rotated, rect_rotated, coord_hotpoint = boulette_imgs_current[
            index_boulette_rotation
        ]

        boulette_scaled = pygame.transform.scale(
            boulette_rotated,
            (int(rect_rotated.w * scale_factor), int(rect_rotated.h * scale_factor))
        )
        boulette_coords = self._get_cartez_coords()
        coord_img_left_up = (
            int(boulette_coords[0] + coord_hotpoint[0] * scale_factor),
            int(boulette_coords[1] + coord_hotpoint[1] * scale_factor)
        )
        return boulette_scaled, coord_img_left_up


    def make_loop_action(self, screen, timer_tick):
        """
        Gestion de la boulette de papier.
        """
        self._update_polar_coords()
        self._update_main_img_counter()
        boulette_scaled, coord_img_left_up = self._get_img_and_coords()
        screen.blit(boulette_scaled, coord_img_left_up)

