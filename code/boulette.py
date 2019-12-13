import math
import random
import pygame

from code.helpers import load_image, screen_size_x, screen_size_y
from code.anim_object import AnimationObject


class BouletteOld():
    # BIG TODO : si on met l'anim en pause, la boulette continue de se déplacer. Woups...

    DEG_TO_RAD_FACTOR = (2*math.pi) / 360


    def __init__(self, boulette_imgs_all):

        # On sépare l'état random de la boulette et l'état de toutes les autres choses.
        # Comme ça les nombres aléatoires des déplacements de la boulette sont gérés
        # indépendamment du reste.
        # Ça sert à rien car aucun autre AnimObject n'utilise le random,
        # mais ça fait classe.
        other_state = random.getstate()
        random.seed("Des morceaux de l'uuuutééééébéééééhèèèèèème !")
        self.my_randgen_state = random.getstate()
        random.setstate(other_state)

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

        other_state = random.getstate()
        random.setstate(self.my_randgen_state)
        accel_angle = random.randint(-50, 50) / 500
        accel_dist = random.randint(-50, 50) / 1000
        self.my_randgen_state = random.getstate()
        random.setstate(other_state)

        if self.delta_angle < -self.delta_angle_lim and accel_angle < 0:
            accel_angle = -accel_angle
            #print("lim down", accel_angle, self.delta_angle, self.angle)
        if self.delta_angle > self.delta_angle_lim and accel_angle > 0:
            accel_angle = -accel_angle
            #print("lim up", accel_angle, self.delta_angle, self.angle)
        self.delta_angle += accel_angle
        self.angle += self.delta_angle
        if self.angle < 0:
            self.angle += 360
        if self.angle > 360:
            self.angle -= 360

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
            int(screen_size_x//2 + math.cos(self.angle*BouletteOld.DEG_TO_RAD_FACTOR)*self.dist),
            int(screen_size_y//2 + math.sin(self.angle*BouletteOld.DEG_TO_RAD_FACTOR)*self.dist)
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


class Boulette(AnimationObject):
    """
    """


    def __init__(self):
        """
        """
        img_boulette_originals = []

        for img_index in range(1, 6):
            img_boulette, boul_rect = load_image("boulette_0" + str(img_index) + ".png", use_alpha=True)
            boul_rect = pygame.Rect(0, 0, int(boul_rect.w*0.25), int(boul_rect.h*0.25))
            boulette_scaled = pygame.transform.scale(
                img_boulette,
                (boul_rect.w, boul_rect.h),
            )
            img_boulette_originals.append(boulette_scaled)

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

        self.boulette = BouletteOld(boulette_imgs_all)


    def make_loop_action(self, screen, timer_tick):
        """
        Gestion de la boulette de papier.
        """
        self.boulette.change_polar_coords()
        boulette_scaled, coord_img_left_up = self.boulette.get_img_and_coords()
        screen.blit(boulette_scaled, (coord_img_left_up[0], coord_img_left_up[1]))

