import math
import random
import pygame

from code.helpers import load_image, screen_size_x, screen_size_y
from code.anim_object import AnimationObject


class Boulette(AnimationObject):
    """
    AnimationObject affichant une boulette de papier qui se promène autour du tunnel.

    Les mouvements sont calculés par des coordonnées polaires, centrée sur le centre
    de l'écran. On fait varier l'angle et la distance de manière à-peu-près aléatoire.

    On définit l'angle, la vitesse de variation de l'angle (positive ou négative),
    et l'accélération de la variation de l'angle. La vitesse est contrainte entre deux
    bornes, pour ne pas que la boulette tourne trop vite dans le tunnel.
    La contrainte est appliqué de manière progressive, c'est à dire que si la vitesse
    devient trop grande, on applique une accélération négative. Si la vitesse
    est trop grande négativement, on applique une accélération positive.

    Pour la distance, c'est pareil. Mais on ajoute une contrainte supplémentaire :
    la valeur de la distance est bornée (en plus de sa vitesse), pour que la boulette
    reste à peu près à mi-chemin du tunnel, au fur et à mesure qu'il avance.

    La boulette est constituée de plusieurs sprites, on les fait cycler périodiquement.

    En plus de cycler les sprites, on les tourne, en fonction de la position dans le
    tunnel, pour montrer que la boulette tourne au fur et à mesure qu'elle se déplace
    sur la paroi du tunnel. Les images rotationnées sont précalculées.

    Et en plus de cycler et de tourner, on ajuste la taille de la boulette, selon
    qu'elle est plus ou moins proche du centre, pour simuler une vue en 3D.
    (Vous aurez compris qu'il n'y a absolument pas de 3D dans toute cette anim).
    """

    # Facteur de conversion degrés vers radians.
    DEG_TO_RAD_FACTOR = (2 * math.pi) / 360
    # Facteur de réduction des images de la boulette de papier.
    # Ces images sont super grandes au départ, mais je veux les garder tel quels,
    # si jamais j'ai besoin de les avoir en grande taille pour une raison ou une autre.
    # Par exemple, si cette variable vaut 4, les sprites seront 4 fois plus petits
    # que les images originales.
    IMG_ORIGINAL_SCALE_DIVISOR = 4

    # Précision, en degrés, des angles de rotations pour les images de la boulette.
    # Par exemple, si cette valeur vaut 15, on précalcule une rotation à 0 degrés,
    # une autre à 15 degrés, une troisième à 30 degrés. Etc.
    # Cette valeur doit être un diviseur de 360, sinon ça ne va pas tomber juste.
    IMG_ROTATION_PRECISION = 15

    # Nombre de sprites de la boulette de papier.
    # Ces sprites seront lus à partir de fichiers png, dans le répertoire "img".
    # Le noms de ces fichiers est de la forme "boulette_xx.png", avec xx variant
    # de 1 à NB_IMG_BOULETTES, écrit sur 2 chiffres.
    # "boulette_01.png", "boulette_02.png", ...
    NB_IMG_BOULETTES = 5

    # Valeur initiale de l'angle permettant de positionner la boulette de papier
    # dans le tunnel (en degrés).
    ANGLE_START = 20.0

    # Distance min et max, en pixels, entre le centre de l'écran et la boulette.
    # Si la boulette se rapproche trop ou s'éloigne trop, on modifie l'accélération
    # pour ramener la distance entre ces deux bornes.
    DIST_MIN = 50
    DIST_MAX = 100

    # Vitesse max (en positif et en négatif, et en degrés) de variation de l'angle de
    # la boulette. Si ça dépasse, on modifie l'accélération pour diminuer la vitesse.
    DELTA_ANGLE_MAX = 1.0
    # Vitesse max (en positif et en négatif, et en pixels) de variation de la distance
    # de la boulette par rapport au centre de l'écran.
    # Si ça dépasse, on modifie l'accélération pour diminuer la vitesse.
    DELTA_DIST_MAX = 0.5

    # Amplitude (en positif et en négatif) de l'accélération de l'angle de la boulette.
    # C'est presque en degrés, à un facteur de division près : ACCEL_ANGLE_DIVISOR.
    ACCEL_ANGLE_SEMI_AMPLITUDE = 50
    # Amplitude (en positif et en négatif) de l'accélération de la distance de la
    # boulette par rapport au centre de l'écran.
    # C'est presque en pixels, à un facteur de division près : ACCEL_DIST_DIVISOR.
    ACCEL_DIST_SEMI_AMPLITUDE = 50
    # Diviseur de l'accélération de l'angle.
    ACCEL_ANGLE_DIVISOR = 500
    # Diviseur de l'accélération de la distance par rapport au centre de l'écran.
    ACCEL_DIST_DIVISOR = 1000

    # Facteur de limitation de l'accélération pour l'angle.
    # Si la vitesse de l'angle devient trop grande (en valeur absolue), on modifie
    # l'accélération. On prend l'accélération qui vient d'être déterminée de manière
    # aléatoire, puis on prend son opposé, puis on la multiplie par ce facteur.
    ACCEL_ANGLE_LIMITING_FACTOR = 1
    # Facteur de limitation de l'accélération pour la distance. Ça fonctionne de la
    # même manière que le facteur de limitation pour l'angle.
    ACCEL_DIST_LIMITING_FACTOR = 0.5

    # Période (en tick d'horloge) entre deux changements de sprites de la boulette
    # de papier.
    IMG_COUNTER_PERIOD = 50

    # La facteur d'échelle déterminant la taille de la boulette est une fonction
    # affine de la distance par rapport au centre de l'écran.
    # facteur = a * dist + b.
    # Avec a = 1 / SCALE_FACTOR_DIVISOR, et b = SCALE_FACTOR_OFFSET.
    SCALE_FACTOR_OFFSET = 0.1
    SCALE_FACTOR_DIVISOR = 400


    def __init__(self):
        """
        Chargement des images de sprites, précalcul des images rotationnées,
        rangement de toutes ces images dans la structure self.boulette_imgs_all.

        self.boulette_imgs_all est une imbrication de tuples.
        Chaque élément du tuple représente l'un des sprites de la boulette de papier, et
        est constitué d'un sous-tuple. Chaque élément de ce sous-tuple représente une
        image rotationnée de la boulette, ils sont rangés par ordre d'angle : tourné à
        0 degré, à 15 degrés, 30 degrés, etc.

        Chaque élément de ce sous-tuple est un sous-sous-tuple, représentant une image
        tournée d'un sprite. Ce sous-sous-tuple contient 3 éléments :
         - l'image en elle-même (pygame.Surface),
         - la taille du rectangle englobant de l'image (pygame.Rect)
         - le vecteur (x, y) de déplacement, depuis le "hotpoint" de la boulette,
         jusqu'au coin supérieur gauche du sprite.

        Le "hotpoint" est une point, dans une image de sprite, permettant de savoir
        où la positionner par rapport aux autres. Lorsqu'on échange l'image d'un sprite,
        on place le hotpoint de la nouvelle image sur le hotpoint de l'ancienne.

        Cette fonction effectue également l'init des variables membres positionnant
        la boulette (angle, distance, vitesse d'angle, vitesse de distance, ...).
        """

        # Liste de pygame.Surface, contenant les images originales des sprites de
        # boulette, sur lesquels on a appliqué la réduction de taille de départ.
        img_boulette_originals = []

        for img_index in range(Boulette.NB_IMG_BOULETTES):

            # Chargement d'une image de sprite.
            filename_img = "boulette_0" + str(img_index + 1) + ".png"
            img_boulette, boul_rect = load_image(filename_img, use_alpha=True)
            # Réduction de sa taille, selon IMG_ORIGINAL_SCALE_DIVISOR.
            boulette_scaled = pygame.transform.scale(
                img_boulette,
                (
                    boul_rect.w // Boulette.IMG_ORIGINAL_SCALE_DIVISOR,
                    boul_rect.h // Boulette.IMG_ORIGINAL_SCALE_DIVISOR
                ),
            )
            img_boulette_originals.append(boulette_scaled)

        self.boulette_imgs_all = []

        # Précalcul de toutes les images rotationnées et des hotpoints.
        for img_boulette_original in img_boulette_originals:
            boulette_imgs = []
            for angle in range(0, 360, Boulette.IMG_ROTATION_PRECISION):
                # Vecteur de déplacement, depuis le centre de l'image, vers le hotpoint.
                # Pour toutes les images originales, le hotpoint est situé en bas,
                # et il est centrée horizontalement.
                vect_center_to_middle_down = pygame.math.Vector2(
                    0,
                    (boul_rect.h // Boulette.IMG_ORIGINAL_SCALE_DIVISOR) // 2
                )
                # Comme on rotate l'image, il faut aussi rotater le hotpoint.
                #
                # Je sais pas pourquoi faut mettre "-angle" et pas "angle".
                # Sûrement un truc compliqué de matheux.
                vect_center_to_middle_down = vect_center_to_middle_down.rotate(-angle)
                boulette_rotated = pygame.transform.rotate(img_boulette_original, angle)
                rect_rotated = boulette_rotated.get_rect()
                # Coordonnées du hotpoint de l'image rotatée, par rapport à l'origine,
                # c'est à dire le coin supérieur gauche de l'image.
                coord_hotpoint = (
                    -rect_rotated.w // 2 - vect_center_to_middle_down.x,
                    -rect_rotated.h // 2 - vect_center_to_middle_down.y
                )
                boulette_imgs.append((boulette_rotated, rect_rotated, coord_hotpoint))
            self.boulette_imgs_all.append(boulette_imgs)

        # Nombre de rotation pour chaque image de sprite.
        # Ça correspond à 360 / Boulette.IMG_ROTATION_PRECISION.
        # On prend ce nombre à partir de la première image de boulette, d'où le "[0]".
        # On pourrait le prendre à partir de n'importe laquelle, puisque toutes les
        # images de boulettes ont été rotationnées avec le même angle.
        self.nb_rotation_img = len(self.boulette_imgs_all[0])

        # On sépare la génération de nombres aléatoires de la boulette, de la génération
        # de nombre de tout le reste du programme.
        # Comme ça, les déplacements de la boulette sont totalement indépendamment
        # de tout le reste.
        # Ça ne sert à rien car aucun autre AnimObject n'utilise de nombres random,
        # mais ça fait classe.
        other_state = random.getstate()
        random.seed("Des morceaux de l'uuuutééééébéééééhèèèèèème !")
        # self.my_randgen_state conserve l'état de génération de nombres aléatoires
        # pour la boulette.
        self.my_randgen_state = random.getstate()
        random.setstate(other_state)

        # Angle de positionnement de la boulette dans le tunnel.
        self.angle = Boulette.ANGLE_START
        # Distance de positionnement de la boulette par rapport au centre de l'écran.
        # On fait exprès de partir d'une distance de 0 : le centre de l'écran.
        # Au début, la boulette va progressivement s'éloigner de l'écran, pour arriver
        # jusqu'à self.dist == Boulette.DIST_MIN.
        self.dist = 0.0
        # Vitesse de variation de l'angle de positionnement.
        self.delta_angle = 0.0
        # Vitesse de variation de la distance de positionnement.
        self.delta_dist = 0.0
        # Compteur pour savoir à quel moment il faut changer d'image du sprite.
        self.img_counter = 0
        # Index de l'image de sprite actuellement affichée.
        self.main_img_index = 0


    def _update_polar_coords(self):
        """
        Met à jour les coordonnées polaires de positionnement de la boulette,
        ainsi que la variation de ces coordonnées.
        c'est à dire les variables membres angle, dist, delta_angle, delta_dist.
        """

        # Génération aléatoire de l'accélération d'angle (accel_angle)
        # et de l'accélération de distance (accel_dist).
        # Comme expliqué dans la fonction __init__, on sépare la génération de nombres
        # aléatoires de la boulette, de la génération de nombre de tout le reste.
        # D'où tout un tas de bin's avec les variables other_state et my_randgen_state.
        other_state = random.getstate()
        random.setstate(self.my_randgen_state)
        a_amp = Boulette.ACCEL_ANGLE_SEMI_AMPLITUDE
        accel_angle = random.randint(-a_amp, a_amp) / Boulette.ACCEL_ANGLE_DIVISOR
        d_amp = Boulette.ACCEL_DIST_SEMI_AMPLITUDE
        accel_dist = random.randint(-d_amp, d_amp) / Boulette.ACCEL_DIST_DIVISOR
        self.my_randgen_state = random.getstate()
        random.setstate(other_state)

        # Contrainte sur la variation de l'angle. Si elle devient trop grande
        # (en valeur absolue), et que l'accélération d'angle risque de la
        # rendre encore plus grande, on modifie l'accélération d'angle
        # pour faire revenir la variation à une valeur plus raisonnable.
        if any((
            self.delta_angle < -Boulette.DELTA_ANGLE_MAX and accel_angle < 0,
            self.delta_angle > Boulette.DELTA_ANGLE_MAX and accel_angle > 0,
        )):
            accel_angle = -accel_angle * Boulette.ACCEL_ANGLE_LIMITING_FACTOR

        # Application de l'accélération et de la variation sur l'angle.
        self.delta_angle += accel_angle
        self.angle += self.delta_angle
        # Contraignage à un angle entre 0 et 360.
        # Normalement, pas besoin de faire un modulo, car la variation ne fait jamais
        # changer l'angle de plus de 360 degrés (en positif ou en négatif).
        if self.angle < 0: self.angle += 360
        if self.angle > 360: self.angle -= 360

        # Contrainte sur la variation de distance. Pareil que l'angle, avec une
        # contrainte en plus :
        # Si la valeur de distance est plus petite que dist_min ou plus grande que
        # dist_max, on modifie l'accélération de distance pour faire revenir
        # la variation à une valeur plus raisonnable.
        #
        # Du coup : pas de garantie absolue que la distance ne sortira jamais de
        # [dist_min, dist_max]. Mais osef.
        if any((
            self.delta_dist < -Boulette.DELTA_DIST_MAX and accel_dist < 0,
            self.dist < Boulette.DIST_MIN and accel_dist < 0,
            self.delta_dist > Boulette.DELTA_DIST_MAX and accel_dist > 0,
            self.dist > Boulette.DIST_MAX and accel_dist > 0,
        )):
            accel_dist -= accel_dist * Boulette.ACCEL_DIST_LIMITING_FACTOR

        # Application de l'accélération et de la variation sur la distance.
        self.delta_dist += accel_dist
        self.dist += self.delta_dist


    def _update_main_img_counter(self):
        """
        Met à jour les variables membres img_counter et main_img_index.
        Lorsque main_img_index change, l'image de sprite change.
        Lorsque main_img_index arrive après la dernière image de sprite, elle se
        remet à zéro pour revenir à la première image.
        """

        self.img_counter += 1
        if self.img_counter >= Boulette.IMG_COUNTER_PERIOD:
            self.img_counter = 0
            self.main_img_index += 1
            if self.main_img_index >= len(self.boulette_imgs_all):
                self.main_img_index = 0


    def _get_cartez_coords(self):
        """
        Renvoie un tuple de deux entiers, représentant les coordonnées (en pixels),
        de la position du hot point de la boulette.
        Ces coordonnées sont calculées à partir des coordonnées polaires de la boulette.
        C'est à dire self.dist et self.angle.
        """
        angle_radian = self.angle * Boulette.DEG_TO_RAD_FACTOR
        return (
            int(screen_size_x // 2 + math.cos(angle_radian) * self.dist),
            int(screen_size_y // 2 + math.sin(angle_radian) * self.dist)
        )


    def _get_img_and_coords(self):
        """
        Renvoie un tuple de deux éléments :
         - l'image à afficher :
            * choisie en fonction de l'index d'image de sprite (main_img_index),
            * choisie en fonction de l'angle d'affichage, dépendant lui-même de
              l'angle de positionnement de la boulette,
            * mise à l'échelle en fonction de la distance d'affichage.
         - la position du coin supérieur droit de l'image à afficher, définie
           en fonction de la position de la boulette, la taille de l'image,
           et son hotpoint.
        """

        boulette_imgs_current = self.boulette_imgs_all[self.main_img_index]
        # Calcul de l'angle de l'image de boulette, en fonction de son angle de
        # positionnement dans le tunnel.
        # Il faut se décaler de "Boulette.IMG_ROTATION_PRECISION / 2", car l'image
        # de boulette tournée à 15 degrés correspond à une position entre 7.5 et
        # 22.5 degrés, l'image tournée à 30 degrés correspond à une position entre
        # 22.5 degrés et 37.5 degrés, et ainsi de suite. On prend l'angle au milieu.
        #
        # Par contre, les autres ajustements, je ne me les justifie pas trop. Je les
        # ais trouvés empiriquement. Il faut ajouter 90 car on doit tourner d'un quart
        # de tour, sûrement parce que l'angle initial est par rapport à l'axe
        # horizontal (cercle trigo) et que la boulette est initialement orientée vers
        # le haut, et non pas vers la droite.
        # En plus de tout ça, il faut tout retourner en faisant 360 - angle,
        # et ça je ne sais vraiment pas pourquoi. Mais ça marche comme ça, youpi !
        adjusted_angle = 360 - self.angle + Boulette.IMG_ROTATION_PRECISION / 2 + 90

        # Petite règle de 3, entre un angle qui varie de 0 à 360, et un index d'image
        # rotatée, qui varie entre 0 et self.nb_rotation_img-1
        index_boulette_rotation = int((adjusted_angle * self.nb_rotation_img) / 360)
        # Petit ajustement de l'index, parce que l'angle initial varie bien entre
        # 0 et 360, mais comme on l'a ajusté avec un "+ 90", ça peut dépasser un peu.
        if index_boulette_rotation >= self.nb_rotation_img:
            index_boulette_rotation -= self.nb_rotation_img
        # Et on peut enfin récupérer la bonne image, avec son hotpoint !
        boulette_rotated, rect_rotated, coord_hotpoint = boulette_imgs_current[
            index_boulette_rotation
        ]

        # Calcul du facteur d'échelle, avec la fonction affine qui va bien.
        scale_factor = (
            Boulette.SCALE_FACTOR_OFFSET + self.dist / Boulette.SCALE_FACTOR_DIVISOR
        )
        # Mise à l'échelle de l'image. Plus elle est près du centre de l'écran,
        # plus elle paraît petite, pour donner l'impression qu'elle est plus loin
        # dans le tunnel.
        boulette_scaled = pygame.transform.scale(
            boulette_rotated,
            (int(rect_rotated.w * scale_factor), int(rect_rotated.h * scale_factor))
        )
        # Récupération des coordonnées x, y en pixels de la boulette.
        # Ajustement par rapport au hot-point, afin d'avoir les coordonnées du coin
        # supérieur droit de l'image à afficher.
        boulette_coords = self._get_cartez_coords()
        coord_img_left_up = (
            int(boulette_coords[0] + coord_hotpoint[0] * scale_factor),
            int(boulette_coords[1] + coord_hotpoint[1] * scale_factor)
        )
        return boulette_scaled, coord_img_left_up


    def make_loop_action(self, screen, timer_tick):
        """
        Gestion complète de la boulette de papier.
        On la déplace, on la tourne, on détermine la bonne image à afficher,
        et on l'affiche.
        """
        self._update_polar_coords()
        self._update_main_img_counter()
        boulette_scaled, coord_img_left_up = self._get_img_and_coords()
        screen.blit(boulette_scaled, coord_img_left_up)

