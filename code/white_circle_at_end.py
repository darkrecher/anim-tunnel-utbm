import numpy
import pygame
from code.helpers import screen_size_x, screen_size_y
from code.anim_object import AnimationObject


class WhiteCircleAtEnd(AnimationObject):
    """
    Animation Object affichant à la fin de l'animation un cercle blanc
    qui grandit progressivement.
    À la fin, le cercle prend tout l'écran, et on ne voit plus que du blanc à l'écran.

    Les images représentant ce cercle sont entièrement de la couleur blanche. Ce qui
    varie, c'est la transparence. Certains pixels sont transparents, d'autres non.

    Le cercle est affiché avec un dégradé, c'est à dire que les bords du cercle
    passent progressivement de la couleur blanche non transparente à la couleur
    blanche totalement transparente, en fonction de la taille du cercle.

    Le temps entre le début d'affichage du cercle et le moment où il prend
    tout l'écran est de 200 ticks d'horloge. C'est non configurable
    (ou alors il faut changer le code de la fonction __init__).

    Les 200 mappings de transparence des 200 cercles à afficher sont précalculés,
    et stockés dans la variable white_circle_alphas.
    """

    # Temps (en tick d'horloge) à partir duquel on commence d'afficher le cercle blanc
    # en le faisant grandir progressivement.
    time_show_white_circle = 2000


    def __init__(self):
        """
        Pré-calcul des cercles. Cette fonction définit deux variables membres :

        self.white_circle : objet pygame.Surface ayant la taille de l'écran, et
        entièrement constitué de pixels blancs. Cette Surface possède une transparence
        (alpha channel), mais celle-ci n'est pas prédéfinie dans la Surface.

        self.white_circle_alphas : liste de 200 éléments (un par tick d'horloge).
        Chaque élément est une matrice numpy, ayant les mêmes dimensions que l'écran,
        et contenant un octet dans chacune de ces cases. Cet octet définit le alpha
        channel du pixel concerné, du tick d'horloge concerné.
        """

        # Construction d'une surface entièrement blanche, de la taille de l'écran,
        # avec un alpha channel. Mais on ne définit pas le alpha channel pour l'instant.
        self.white_circle = pygame.Surface(
            (screen_size_x, screen_size_y),
            flags=pygame.SRCALPHA
        )
        self.white_circle.fill((255, 255, 255))

        # Matrice contenant, pour chaque pixel de l'écran,
        # la distance (en pixels) par rapport au centre de l'écran.
        # On met le dtype en "i4", c'est à dire que ce sont des entiers signés.
        # Ça a l'air bizarre, parce qu'une distance peut normalement être stockée
        # dans un entier non signé.
        # Mais ensuite, on effectue des opérations avec cette matrice qui peuvent
        # aboutir à des valeurs signées (même si c'est une valeur intermédiaire
        # dans un calcul).
        # Pour éviter que le calcul ne se plante, il faut avoir des valeurs signées
        # dès le départ. Je ne sais pas bien pourquoi, mais ça doit être une subtilité
        # de numpy.
        dist_from_center = numpy.zeros((screen_size_x, screen_size_y), dtype="i4")
        semi_size_x = screen_size_x // 2
        semi_size_y = screen_size_y // 2

        # Calcul de cette distance pour chaque pixel.
        # C'est du pythagore : racine de (x² + y²)
        for x in range(screen_size_x):
            for y in range(screen_size_y):
                val = ((x-semi_size_x) ** 2 + (y-semi_size_y) ** 2) ** 0.5
                dist_from_center[x, y] = val

        # --- Précalcul des transparences ---

        # min_circles est une liste de 200 floats, représentant les rayons minimaux
        # des 200 cercles à afficher. Pour un tick donné, tous les pixels ayant une
        # distance par rapport au centre de l'écran, inférieure à min_circles,
        # seront affichés totalement en blanc.
        # min_circles commence par 50 valeurs à zéros, suivis de 150 valeurs évoluant
        # progressivement (0**1.2, 1**1.2, 2**1.2, 3**1.2, ..., juste parce que ça me
        # semble esthétiquement potable comme cela).
        min_circles = [ 0 ] * 50
        min_circles += [ int(r**1.2) for r in range(150) ]
        # min_circles est une liste de 200 floats, représentant les rayons maximaux
        # des 200 cercles à afficher. Pour un tick donné, tous les pixels ayant une
        # distance par rapport au centre de l'écran, supérieure à max_circles,
        # seront affichés totalement en blanc.
        # Les pixels dont la distance se situe entre min_circles et max_circles seront
        # plus ou moins transparents, progressivement. La transparence augmente au fur
        # et à mesure qu'on s'éloigne du centre de l'écran.
        # max_circles contient 200 valeurs évoluant progressivement.
        # (1 + 0**1.2, 1 + 1**1.2, 1 + 2**1.2, 1 + 3**1.2, ...)
        max_circles = [ 1 + int(r**1.2) for r in range(200) ]

        # Variable membre qui recevra les 200 matrices numpy.
        self.white_circle_alphas = []
        white_circle_temp = numpy.zeros((screen_size_x, screen_size_y), dtype="i4")

        for min_dist, max_dist in zip(min_circles, max_circles):

            amplitude = max_dist - min_dist
            # Attention ça tue, c'est des opérations sur des matrices, à la numpy.
            # Tout d'abord, white_circle_temp prend des valeurs pouvant aller de 0
            # à 255 ou plus.
            # C'est une relation linéaire avec la distance par rapport au centre,
            # mais inversement proportionnel. C'est à dire que la valeur du pixel
            # du milieu vaut beaucoup, et au fur et à mesure qu'on s'éloigne du centre,
            # ça diminue.
            # C'est ce super-calcul qui oblige dist_from_center à être en "i4", et
            # non pas en "u4". Ce calcul peut faire intervenir des valeurs
            # intermédiaires signées, et donc si on l'effectue à partir d'une matrice
            # avec des entiers non signés, ça donne des valeurs bizarres.
            white_circle_temp[:] = 255 - ((dist_from_center-min_dist)*255) // amplitude

            # Bornage du min et du max. Tous les éléments de la matrice inférieurs
            # à 0 sont fixés à 0, tout ceux qui sont supérieurs à 255 sont fixés à 255.
            white_circle_temp[ white_circle_temp > 255 ] = 255
            white_circle_temp[ white_circle_temp < 0 ] = 0

            # Recopie des valeurs calculées dans une matrice contenant des octets
            # non signés. En ajout de cette matrice dans la liste white_circle_alphas.
            white_circle_next = numpy.zeros((screen_size_x, screen_size_y), dtype="u1")
            white_circle_next[:] = white_circle_temp
            self.white_circle_alphas.append(white_circle_next)


    def make_loop_action(self, screen, timer_tick):
        """
        Affichage d'un cercle blanc représentant la lumière finale,
        si on est suffisamment avancé dans le temps de l'animation.
        """

        if timer_tick <= WhiteCircleAtEnd.time_show_white_circle:
            # Pas assez avancé dans le temps, on n'a rien à afficher.
            return

        circle_index = timer_tick - WhiteCircleAtEnd.time_show_white_circle

        if circle_index < len(self.white_circle_alphas):
            # Connexion entre la mémoire vidéo pygame contenant le alpha channel
            # de la surface white_circle, et white_circle_alpha : une matrice numpy
            # que l'on fabrique pour l'occasion
            white_circle_alpha = pygame.surfarray.pixels_alpha(self.white_circle)
            # Recopie, dans white_circle_alpha, de l'une des 200 matrices
            # numpy précalculées lors de l'__init__. Cette recopie va directement
            # modifier les valeurs de alpha channel de la surface white_circle_alpha,
            # grâce au lien qu'on a établi juste avant.
            white_circle_alpha[:] = self.white_circle_alphas[circle_index]
            # On est obligé de deleter pour la matrice linkée, pour délocker
            # la Surface correspondante (self.white_circle).
            # Ce délockage va permettre à pygame de récupérer dans sa mémoire vidéo
            # les nouvelles valeurs de l'alpha channel qu'on a recopiée juste avant.
            # Il ne restera plus qu'à afficher cette surface modifiée.
            #
            # Cette opération de recopie via une matrice numpy est super-rapide et
            # super optimisée, avec la mémoire vidéo, la lib SDL et tout le bastringue.
            del white_circle_alpha

        # Si on est arrivé jusqu'ici sans être passé par le "if" ci-dessus,
        # alors la surface self.white_circle n'a pas été modifiée. Son dernier contenu
        # correspondait à un rectangle entièrement blanc, sans aucune transparence.
        # On affiche directement ce rectangle.
        screen.blit(self.white_circle, (0, 0))

