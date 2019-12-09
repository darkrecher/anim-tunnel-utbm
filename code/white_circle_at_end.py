import numpy
import pygame
from code.helpers import screen_size_x, screen_size_y
from code.anim_object import AnimationObject

class WhiteCircleAtEnd(AnimationObject):
    """
    BIG TODO : arranger tout ce code.
    """
    time_show_white_circle = 2000


    def __init__(self):
        print("precalc circle alpha source")
        self.white_circle = pygame.Surface((screen_size_x, screen_size_y), flags=pygame.SRCALPHA)
        self.white_circle.fill((255, 255, 255))
        # Matrice contenant la distance (en pixels) par rapport au centre de l'écran.
        white_circle_alpha_source = numpy.zeros((screen_size_x, screen_size_y), dtype="u4")
        for x in range(screen_size_x):
            for y in range(screen_size_y):
                val = ((x-screen_size_x//2)**2 + (y-screen_size_y//2)**2)**0.5
                white_circle_alpha_source[x, y] = val

        # Précalcul de la transparence du cercle blanc qui apparaît à la fin
        print("precalc white_circle_alphas")
        self.white_circle_alphas = []
        white_circle_temp = numpy.zeros((screen_size_x, screen_size_y), dtype="u4")
        min_circles = [0] * 50 + [ int(r**1.2) for r in range(150) ]
        max_circles = [ 1+int(r**1.2) for r in range(200) ]

        for min_dist, max_dist in zip(min_circles, max_circles):
            white_circle_temp[:] = 255-((white_circle_alpha_source-min_dist)*255)//(max_dist-min_dist)
            white_circle_temp[white_circle_alpha_source < min_dist] = 255
            white_circle_temp[white_circle_alpha_source >= max_dist] = 0
            white_circle_next = numpy.zeros((screen_size_x, screen_size_y), dtype="u1")
            white_circle_next[:] = white_circle_temp
            self.white_circle_alphas.append(white_circle_next)


    def make_loop_action(self, screen, timer_tick):
        """
        """
        # Affichage de la lumière finale.
        if timer_tick > WhiteCircleAtEnd.time_show_white_circle:
            circle_index = timer_tick - WhiteCircleAtEnd.time_show_white_circle
            if circle_index < len(self.white_circle_alphas):
                white_circle_alpha = pygame.surfarray.pixels_alpha(self.white_circle)
                white_circle_alpha[:] = self.white_circle_alphas[circle_index]
                # On est obligé de deleter pour délocker la Surface correspondante,
                # pour faire comprendre à pygame qu'il peut récupérer les modifs
                # qu'on a effectuées sur la Surface.
                del white_circle_alpha
            screen.blit(self.white_circle, (0, 0))
