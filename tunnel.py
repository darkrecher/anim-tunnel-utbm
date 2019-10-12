# coding: utf-8

import os
import math
import numpy
import pygame
import pygame.locals
import pygame.surfarray
from pygame.compat import geterror


main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

screen_size_x = 400
screen_size_y = 300

tunnel_diameter = 350
dist_focale = 200


def load_image(name, colorkey=None):
    fullname = os.path.join(data_dir, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print('Cannot load image:', fullname)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()


def cylinder_coords_from_screen_cords(pix_x, pix_y):
    a_x = pix_x - screen_size_x/2
    a_y = pix_y - screen_size_y/2
    if (a_x, a_y) == (0, 0):
        raise ValueError("La coordonnée du milieu de l'écran ne peut pas atteindre le cylindre")
    # https://stackoverflow.com/questions/15994194/how-to-convert-x-y-coordinates-to-an-angle
    angle = math.atan2(a_y, a_x)
    cylinder_z = dist_focale * tunnel_diameter / (math.sqrt(a_x**2 + a_y**2))
    return angle, cylinder_z


def colorval_from_screen_cords(pix_x, pix_y, offset_z_cylinder=0):
    try:
        angle, cylinder_z = cylinder_coords_from_screen_cords(pix_x, pix_y)
    except ValueError:
        return 0
    cylinder_z += offset_z_cylinder
    blue = ((angle+math.pi)*255)/(2*math.pi)
    blue = int(blue)
    red = int(cylinder_z) & 255
    green = 0
    return red<<16 | green<<8 | blue


def cycle_red(colorval):
    colorval = int(colorval)
    if colorval>>16 == 255:
        return colorval & 65535
    else:
        return colorval + 65536

v_cycle_red = numpy.vectorize(cycle_red)


def main():

    # Initialize Everything
    pygame.init()
    screen = pygame.display.set_mode((screen_size_x, screen_size_y))
    pygame.display.set_caption('Tunnel 3D')
    pygame.mouse.set_visible(0)

    # Create The Backgound
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))
    timer_tick = 0

    surf_array_background =  pygame.surfarray.pixels2d(background)
    #print(surf_array_background)
    #pygame.quit()

    #background.lock()
    #for x in range(screen_size_x):
    #    for y in range(screen_size_y):
    #        #background.set_at((x, y), (timer_color & 255, 0, 0))
    #        background.set_at((x, y), color_from_screen_cords(x, y, timer_tick))
    #background.unlock()

    for x in range(screen_size_x):
        for y in range(screen_size_y):
            surf_array_background[x, y] = colorval_from_screen_cords(x, y, timer_tick)

    del surf_array_background

    # Display The Background
    screen.blit(background, (0, 0))
    pygame.display.flip()

    clock = pygame.time.Clock()
    going = True

    #speed_test = [ pygame.Surface(screen.get_size()) for _ in range(256) ]
    #for index_color in range(256):
    #    #speed_test[index_color].fill((index_color, 0, 0))
    #    current_screen = speed_test[index_color]
    #    current_screen.lock()
    #    for x in range(screen_size_x):
    #        for y in range(screen_size_y):
    #            current_screen.set_at((x, y), color_from_screen_cords(x, y, index_color))
    #    current_screen.unlock()
    #    if index_color % 10 == 0:
    #        print(index_color)

    array_pixel = numpy.zeros((screen_size_x, screen_size_y))

    for x in range(screen_size_x):
        for y in range(screen_size_y):
            array_pixel[x, y] = colorval_from_screen_cords(x, y, timer_tick)

    while going:

        clock.tick(600)

        # Handle Input Events
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                going = False
            elif event.type == pygame.locals.KEYDOWN and event.key == pygame.locals.K_ESCAPE:
                going = False

        timer_tick += 1

        #array_pixel = [ 256*65536 + 200*256 + timer_tick ] * (screen_size_x*screen_size_y)
        #array_pixel = numpy.array(array_pixel)

        #new_array_pixel = numpy.array([cycle_red(colorval) for colorval in array_pixel])
        #new_array_pixel = numpy.array([colorval+1 for colorval in array_pixel])
        new_array_pixel = v_cycle_red(array_pixel)
        array_pixel = new_array_pixel

        #for x in range(screen_size_x):
        ##for x in range(190, 220):
        #    for y in range(screen_size_y):
        #        #array_pixel[x, y] = 256*65536 + 200*256 + timer_tick
        #        array_pixel[x, y] = colorval_from_screen_cords(x, y, timer_tick)


        pygame.surfarray.blit_array(screen, array_pixel)

        #surf_array_background =  pygame.surfarray.pixels2d(background)
        #for x in range(screen_size_x):
        #    for y in range(screen_size_y):
        #        surf_array_background[x, y] = colorval_from_screen_cords(x, y, timer_tick)
        #del surf_array_background

        # Draw Everything
        #screen.blit(background, (0, 0))
        #screen.blit(speed_test[timer_tick & 255], (0, 0))
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()

