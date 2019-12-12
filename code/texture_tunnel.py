import math
import numpy
import pygame

from code.helpers import load_image, screen_size_x, screen_size_y
from code.anim_object import AnimationObject


class TextureTunnel(AnimationObject):
    """
    Animation Object le plus important. C'est celui qui affiche le tunnel qui avance.
    Comme il s'affiche sur tout l'écran, il n'est pas nécessaire d'effacer
    toute la surface d'affichage avec un carré noir.

    Cette Animation Object utilise une image de texture ayant une très grande largeur,
    et une hauteur qui peut être plus ou moins grande.

    Elle effectue un truc qui ressemble à du raytracing. C'est à dire que pour
    chaque pixel de l'écran, elle détermine le pixel correspondant de la texture,
    en considérant que cette texture est dessinée sur un cylindre.

    C'est du raytracing tout simple. Un fois le point d'intersection trouvé, on prend
    le pixel voisin le plus proche sur la texture. Pas de calcul de proportion compliqué
    avec les pixels alentour, ni d'anti-aliasing, ni quoi que ce soye.

    Les correspondances entre pixels d'écran et pixels de texture sur le tunnel sont
    précalculées. La seule chose à faire pour faire avancer l'image sur le tunnel,
    est d'appliquer un offset sur la coordonnée Z (profondeur) du cylindre.
    """

    # Diamètre du cylindre, en "pixels". C'est pas vraiment des pixels car on imagine
    # que le cylindre est positionné en 3D derrière l'écran. La notion de "pixels"
    # n'a pas vraiment de sens dans ce contexte, mais bon, vous voyez l'idée quoi.
    diameter = 300
    # Distance focale. Distance entre la "caméra" et l'écran de l'ordinateur.
    # C'est pas super clair. Ça mériterait un petit schéma. Soyons fou, faisons cela
    # à l'arrache. En vue de dessus, ça donne ça :
    #
    #    Diamètre du cylindre
    #    |...................|
    #
    #    c         |         c
    #    c         |         c       axe des z (profondeur)
    #    Z         A         c          ^
    #    c\        |         c          |
    #    c|        |         c          |
    #    c \       |         c          |
    #    c |       |         c          .-------> axe des x (abscisse)
    #    c  \      |         c
    #    c  |      |         c
    #    c   \     |         c
    #    c   |     |         c
    #    c    \    |         c
    #    c    |    |         c
    #    c     \   |         c
    #    c     |   |         c
    #          \   |
    #     eeeeeePeeOeeeeeeeee   -
    #           \  |            .
    #           |  |            .
    #            \ |            . Distance focale
    #            | |            .
    #             \|            .
    #              K            -
    #
    # c = le cylindre
    # e = l'écran de l'ordinateur
    # O = le point d'origine du repère.
    # K = la caméra
    # P = l'un des points de l'écran. On connait ses coordonnées : pix_x, pix_y
    # Z = le point d'intersection de la droite (K, X) avec le cylindre.
    # A = point projet de Z sur l'axe des z partant de l'origine.
    # On cherche ses coordonnées.
    dist_focale = 100
    # Vitesse d'avancement du cylindre, en "pixels" par tick d'horloge.
    forward_speed_factor = 4

    def _cylinder_coords_from_screen_coords(self, pix_x, pix_y):
        """
        À partir des coordonnées d'un pixel P de l'écran : pix_x, pix_y,
        renvoie un tuple de deux éléments :

        1) l'angle entre l'axe des abscisses et la droite (O, P)
        O étant le point d'origine du repère, placé au milieu de l'écran.

        2) la coordonnée z (profondeur) du point d'intersection de la
        droite (O, pixel) avec le cylindre.

        Bon, en fait, c'est la coondonnée z + la distance focale.
        Il y a un décalage idiot à cause du théorème de ce crétin de Thalès,
        mais on s'en fout, c'est juste un décalage fixe qui n'a pas d'importance.

        Cette fonction lève une exception si on passe en paramètre les
        coordonnées du milieu de l'écran (c'est à dire le point O).
        Ce point ne s'intersecte pas avec le cylindre, car la droite (K, O) est
        parallère au cylindre.
        """
        # coordonnées du vecteur O -> X.
        # Vecteur allant de l'origine du repère vers le pixel à l'écran.
        vect_x = pix_x - screen_size_x / 2
        vect_y = pix_y - screen_size_y / 2

        if (vect_x, vect_y) == (0, 0):
            # On a passé en paramètre le point O. Paf, exception.
            raise ValueError("Le milieu de l'écran n'intersecte pas le cylindre")

        # Angle entre l'axe des abscisses et la droite (O, P).
        # https://stackoverflow.com/questions/15994194/
        # how-to-convert-x-y-coordinates-to-an-angle
        angle = math.atan2(vect_y, vect_x)
        # Distance [O, P]
        dist_center = math.sqrt(vect_x ** 2 + vect_y ** 2)
        # Théorème de Thales avec les triangles KAZ et KOP.
        # KA / KO == AZ / OP
        # KA == KO * AZ / OP
        # KA == dist_focale * diamètre / dist_center
        # KO + OA == dist_focale * diamètre / dist_center
        # dist_focale + (coordonnée z du point Z) == dist_focale * diamètre / dist_center
        #
        # Petit décalage de triche, on enlève la dist_focale dans la partie gauche
        # de l'équation, juste parce que c'est pas ça qu'on veut.
        #
        # cylinder_z == dist_focale * diamètre / dist_center
        cylinder_z = TextureTunnel.dist_focale * TextureTunnel.diameter / dist_center

        return angle, cylinder_z


    def _tex_coord_from_screen_coords(self, pix_x, pix_y):
        """
        À partir des coordonnées d'un pixel P de l'écran : pix_x, pix_y,
        renvoie les coordonnées tex_x, tex_y du pixel de texture, du point projeté
        sur le cylindre.

        On considère que le cylindre n'a pas du tout avancé.
        Pour le faire avancer, il suffit d'augmenter directement tex_x

        Si on passe en paramètre le milieu de l'écran, c'est à dire le pixel qui
        ne s'intersecte pas avec le cylindre, on renvoie pas défaut les coordonnées
        de texture (0, 0).
        """
        try:
            # Récupération de l'angle (OP, axe des x) et de la coordonnée Z
            # du point d'intersection avec le cylindre. (Voir docstring et comm
            # de la fonction ci-dessus)
            angle, cylinder_z = self._cylinder_coords_from_screen_coords(pix_x, pix_y)
        except ValueError:
            # Cas du pixel de milieu de l'écran. On renvoie (0, 0) par défaut.
            return (0, 0)

        pi = math.pi
        # Correspondance directe entre cylinder_z (profondeur du cylindre)
        # et coordonnée x de la texture appliquée sur le cylindre.
        # Si on dépasse le cylindre (le cas peut arriver pour un point proche du milieu
        # de l'écran, la projection ira trop loin), on prend alors la coordonnée x
        # du bord droit de la texture. On ne peut pas aller plus loin.
        tex_x = min(int(cylinder_z), self.texture_width)
        # L'angle varie entre -pi et +pi. La coordonnée y du pixel sur la texture varie
        # entre 0 et texture_height-1. On fait une simple règle de trois.
        tex_y = int(((angle + pi) * (self.texture_height - 1)) / (2 * pi))
        # on décale tout de un cinquième de la hauteur de texture. Cela revient à tourner
        # le cylindre d'un cinquième de tour. De cette manière, le raccord moche entre
        # le haut et le bas de la texture ne s'affichera pas à l'écran le long d'une ligne
        # verticale ou horizontale. Il s'affichera le long d'une ligne droite oblique.
        # Ça rend le raccord un peu moins moche.
        # Si la texture était correctement repliée sur elle-même, c'est à dire que les
        # pixels du bord supérieur se corresponde parfaitement avec les pixels du bord
        # inférieur, ce raccord ne se verrait pas du tout. Mais je ne suis pas parvenu
        # à faire cela avec ma superbe texture. Pourtant, Paint.Net, ça permet plein
        # de trucs. Mais je ne suis pas assez bon (voire pas du tout bon) en graphisme.
        tex_y = tex_y + self.texture_height // 5
        if tex_y >= self.texture_height:
            tex_y -= self.texture_height

        return tex_x, tex_y


    def __init__(self):
        """
        Chargement de l'image de texture et précalcul des raytracings pour afficher
        cette texture sous forme d'un tunnel.
        """
        # Chargement de l'image de la texture appliquée sur le tunnel.
        # Récupération de la taille de l'image.
        texture, texture_rect = load_image("texture.png")
        self.texture_width = texture_rect.w
        self.texture_height = texture_rect.h
        # Conversion de cette image en un array numpy à 2 dimensions.
        # Chaque case de l'array contient les couleurs RVB du pixel correspondant.
        self.array_texture = pygame.surfarray.array2d(texture)

        matrix_dimensions = (screen_size_x, screen_size_y)
        # Création de deux matrices (array numpy) ayant les dimensions de l'écran.
        # La première contiendra la correspondance entre les pixels écran en entrée,
        # et la coordonnée x du pixel sur la texture en sortie.
        # La deuxième matrice contiendra la correspondance entre le pixel écran
        # et la coordonnée y du pixel texture.
        #
        # Si la taille (width ou height) de l'image de texture est très grande
        # et qu'elle ne tient pas dans un int 32 bits, ça va péter. Mais osef.
        self.screen_from_tunnel_x = numpy.zeros(matrix_dimensions, dtype="u4")
        self.screen_from_tunnel_y = numpy.zeros(matrix_dimensions, dtype="u4")
        # Une dernière matrice, de même dimensions, mais dont toutes les cases
        # contiennent la même valeur : la coordonnée x du bord droit de la texture.
        # On en a besoin au moment de l'affichage, pour s'arrêter au dernier pixel
        # de texture, dans le cas où on a fait trop avancer le cylindre.
        self.screen_from_tunnel_x_lim = numpy.zeros(matrix_dimensions, dtype="u4")

        # Remplissage des trois matrices sus-mentionnées, en effectuant le calcul
        # de projection pour chaque pixel.
        for x in range(screen_size_x):
            for y in range(screen_size_y):
                tex_coords = self._tex_coord_from_screen_coords(x, y)
                self.screen_from_tunnel_x[x, y] = tex_coords[0]
                self.screen_from_tunnel_y[x, y] = tex_coords[1]
                self.screen_from_tunnel_x_lim[x, y] = self.texture_width - 1


    def make_loop_action(self, screen, timer_tick):
        """
        Utilisation du raytracing précalculé pour afficher le cylindre texturée sur la
        surface screen.

        Pour l'affichage, on fait avancer le cylindre d'un certain nombre de pixels,
        en fonction de timer_tick.
        La vitesse d'avancement est définie par TextureTunnel.forward_speed_factor.
        """
        # Calcul de l'avancement du cylindre.
        x_offset = timer_tick * TextureTunnel.forward_speed_factor

        # copie d'une matrice de couleurs de pixels sur la surface screen.
        # Voir doc de blit_array pour plus de précision.
        pygame.surfarray.blit_array(
            screen,
            # On part de array_texture, et on fait directement les correspondances
            # de coordonnées entre pixel écran et pixel texture.
            # Pour plus de détail sur la manière dont la correspondance se fait, voir :
            # https://docs.scipy.org/doc/numpy/user/basics.indexing.html#index-arrays
            self.array_texture[
                # On prend la coordonnée x de texture décalée de x_offset.
                # Mais si l'offset est trop grand, c'est à dire si on a trop fait
                # avancer le cylindre, on risque de ne pas avoir de pixels dans la
                # texture, car l'image ne serait pas assez large.
                # Donc on utilise numpy.minimum. Si c'est allé trop loin à cause de
                # l'offset, on prend le pixel qui sera sur le bord droit du cylindre.
                numpy.minimum(
                    self.screen_from_tunnel_x + x_offset,
                    self.screen_from_tunnel_x_lim
                ),
                self.screen_from_tunnel_y,
            ],
        )


