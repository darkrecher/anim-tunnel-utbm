from code.helpers import load_image, screen_size_x, screen_size_y
from code.anim_object import AnimationObject


class BlackCircle(AnimationObject):
    """
    Animation Object affichant un cercle noir (avec les bords un peu transparents,
    donc de moins en moins noir).

    Le cercle est affiché au milieu de l'écran, durant toute l'anim.
    On ne le voit plus à la fin de l'anim car il est recouvert par le cercle blanc.
    """

    def __init__(self):
        """
        Chargement de l'image du cercle noir, et définition des coordonnées d'affichage.
        """
        self.black_circle, black_circle_rect = load_image("fond_noir.png", use_alpha=True)
        self.coord_black_circle = (
            (screen_size_x - black_circle_rect.w) // 2,
            (screen_size_y - black_circle_rect.h) // 2,
        )


    def make_loop_action(self, screen, timer_tick):
        """
        Affichage du cercle noir.
        """
        screen.blit(self.black_circle, self.coord_black_circle)

