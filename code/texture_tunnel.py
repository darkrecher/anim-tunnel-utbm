import math
import numpy
import pygame

from code.helpers import load_image, screen_size_x, screen_size_y
from code.anim_object import AnimationObject


class TextureTunnel(AnimationObject):
    """
    TODO : commenter tout ce bazar
    """

    diameter = 300
    dist_focale = 100
    forward_speed_factor = 4

    def _cylinder_coords_from_screen_coords(self, pix_x, pix_y):
        vect_x = pix_x - screen_size_x / 2
        vect_y = pix_y - screen_size_y / 2

        if (vect_x, vect_y) == (0, 0):
            raise ValueError("Le milieu de l'écran n'intersecte pas le cylindre")

        # https://stackoverflow.com/questions/15994194/
        # how-to-convert-x-y-coordinates-to-an-angle
        angle = math.atan2(vect_y, vect_x)
        dist_center = math.sqrt(vect_x ** 2 + vect_y ** 2)
        cylinder_z = TextureTunnel.dist_focale * TextureTunnel.diameter / dist_center

        return angle, cylinder_z


    def _tex_coord_from_screen_coords(self, pix_x, pix_y):
        try:
            angle, cylinder_z = self._cylinder_coords_from_screen_coords(pix_x, pix_y)
        except ValueError:
            return (0, 0)

        pi = math.pi
        tex_x = min(int(cylinder_z), self.texture_width)
        tex_y = int(((angle + pi) * (self.texture_height - 1)) / (2 * pi))
        # on décale tout de un cinquième, pour que le raccord moche entre le haut
        # et le bas de l'image ne soit pas pil poil sur la partie gauche du tunnel.
        tex_y = tex_y + self.texture_height // 5
        if tex_y >= self.texture_height:
            tex_y -= self.texture_height

        return tex_x, tex_y


    def __init__(self):
        """
        """
        texture, texture_rect = load_image("texture.png")
        self.texture_width = texture_rect.w
        self.texture_height = texture_rect.h
        self.array_texture = pygame.surfarray.array2d(texture)

        # Si la taille (width ou height) de l'image de texture ne tient pas dans
        # un int 32 bits, ça va péter. Mais franchement osef.
        matrix_dimensions = (screen_size_x, screen_size_y)
        self.screen_from_tunnel_x = numpy.zeros(matrix_dimensions, dtype="u4")
        self.screen_from_tunnel_y = numpy.zeros(matrix_dimensions, dtype="u4")
        self.screen_from_tunnel_x_lim = numpy.zeros(matrix_dimensions, dtype="u4")

        for x in range(screen_size_x):
            for y in range(screen_size_y):
                tex_coords = self._tex_coord_from_screen_coords(x, y)
                self.screen_from_tunnel_x[x, y] = tex_coords[0]
                self.screen_from_tunnel_y[x, y] = tex_coords[1]
                self.screen_from_tunnel_x_lim[x, y] = self.texture_width - 1


    def make_loop_action(self, screen, timer_tick):
        """
        """
        x_offset = timer_tick * TextureTunnel.forward_speed_factor

        pygame.surfarray.blit_array(
            screen,
            self.array_texture[
                numpy.minimum(
                    self.screen_from_tunnel_x + x_offset,
                    self.screen_from_tunnel_x_lim
                ),
                self.screen_from_tunnel_y,
            ],
        )


