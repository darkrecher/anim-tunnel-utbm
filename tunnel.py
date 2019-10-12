import os
import math
import numpy
import pygame
import pygame.locals
import pygame.surfarray
import pygame.mixer
from pygame.compat import geterror


"""
À tester, quand on en sera à texturer le tunnel :

>>> data_flat
array([ 0,  1,  2, 10, 20, 30])
>>> data_flat[numpy.array([1, 3, 3, 5, 1])]
array([ 1, 10, 10, 30,  1])
>>>
>>>
>>> data
array([[ 0,  1,  2],
       [10, 20, 30]])
>>> data[numpy.array([[0, 0], [1, 1]])
... ]
array([[[ 0,  1,  2],
        [ 0,  1,  2]],

       [[10, 20, 30],
        [10, 20, 30]]])
>>> data[numpy.array([[0, 0], [1, 1]])]
array([[[ 0,  1,  2],
        [ 0,  1,  2]],

       [[10, 20, 30],
        [10, 20, 30]]])
>>> data[numpy.array([0, 1])]
array([[ 0,  1,  2],
       [10, 20, 30]])
>>> data[numpy.array([0, 1]), numpy.array([0, 1])]
array([ 0, 20])
>>> data[numpy.array([0, 1, 2]), numpy.array([0, 1, 1])]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
IndexError: index 2 is out of bounds for axis 0 with size 2
>>> data[numpy.array([0, 1, 1]), numpy.array([0, 1, 2])]
array([ 0, 20, 30])
>>>


"""


main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

screen_size_x = 640
screen_size_y = 480

tunnel_diameter = 300
dist_focale = 100


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


def cylinder_coords_from_screen_coords(pix_x, pix_y):
    a_x = pix_x - screen_size_x/2
    a_y = pix_y - screen_size_y/2
    if (a_x, a_y) == (0, 0):
        raise ValueError("La coordonnée du milieu de l'écran ne peut pas atteindre le cylindre")
    # https://stackoverflow.com/questions/15994194/how-to-convert-x-y-coordinates-to-an-angle
    angle = math.atan2(a_y, a_x)
    cylinder_z = dist_focale * tunnel_diameter / (math.sqrt(a_x**2 + a_y**2))
    return angle, cylinder_z


def colorval_from_screen_coords_old(pix_x, pix_y, offset_z_cylinder=0):
    try:
        angle, cylinder_z = cylinder_coords_from_screen_coords(pix_x, pix_y)
    except ValueError:
        return 0
    cylinder_z += offset_z_cylinder
    blue = ((angle+math.pi)*255)/(2*math.pi)
    blue = int(blue)
    red = int(cylinder_z) & 255
    green = 0
    return red<<16 | green<<8 | blue


def colorval_from_screen_coords(pix_x, pix_y, texture_width, texture_height, texture, offset_z_cylinder=0):
    try:
        angle, cylinder_z = cylinder_coords_from_screen_coords(pix_x, pix_y)
    except ValueError:
        return 0
    cylinder_z += offset_z_cylinder
    tex_x = int(cylinder_z % texture_width)
    tex_y = int(((angle+math.pi)*(texture_height-1))/(2*math.pi))
    tex_color = texture.get_at((tex_x, tex_y))
    return tex_color.r<<16 | tex_color.g<<8 | tex_color.b


def tex_coord_from_screen_coords(pix_x, pix_y, texture_width, texture_height):
    try:
        angle, cylinder_z = cylinder_coords_from_screen_coords(pix_x, pix_y)
    except ValueError:
        return (0, 0)
    tex_x = int(cylinder_z % texture_width)
    tex_y = int(((angle+math.pi)*(texture_height-1))/(2*math.pi))
    # on décale tout de un cinquième, pour que le raccord moche entre le haut et le bas de l'image ne soit pas pil poil sur la partie gauche du tunnel.
    tex_y = (tex_y + texture_height//5) % texture_height
    return (tex_x, tex_y)



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
    pygame.mixer.init()
    screen = pygame.display.set_mode((screen_size_x, screen_size_y))
    pygame.display.set_caption('Tunnel 3D')
    pygame.mouse.set_visible(0)

    snd_pere_200_1 = pygame.mixer.Sound(os.path.join('audio', 'pere200_1.wav'))

    texture, texture_rect = load_image("texture.png")
    print(texture_rect)
    texture_width = texture_rect.w
    texture_height = texture_rect.h

    array_texture_origin = pygame.surfarray.array2d(texture)
    print(type(array_texture_origin))
    print(array_texture_origin.dtype)
    print(array_texture_origin[0,0])
    array_texture = array_texture_origin.copy()

    # Create The Backgound
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))
    timer_tick = 0

    #surf_array_background =  pygame.surfarray.pixels2d(background)
    #print(surf_array_background)
    #pygame.quit()

    #background.lock()
    #for x in range(screen_size_x):
    #    for y in range(screen_size_y):
    #        #background.set_at((x, y), (timer_color & 255, 0, 0))
    #        background.set_at((x, y), color_from_screen_coords(x, y, timer_tick))
    #background.unlock()

    #for x in range(screen_size_x):
    #    for y in range(screen_size_y):
    #        surf_array_background[x, y] = colorval_from_screen_coords(x, y, texture_width, texture_height, texture, timer_tick)

    #del surf_array_background

    # Display The Background
    #screen.blit(background, (0, 0))

    # Si la taille (width ou height) de l'image de texture ne tient pas
    # dans un int 32 bits, ça va péter. Mais franchement osef.
    screen_from_tunnel_x = numpy.zeros((screen_size_x, screen_size_y), dtype="u4")
    screen_from_tunnel_y = numpy.zeros((screen_size_x, screen_size_y), dtype="u4")

    for x in range(screen_size_x):
        for y in range(screen_size_y):
            tex_coords = tex_coord_from_screen_coords(x, y, texture_width, texture_height)
            screen_from_tunnel_x[x, y] = tex_coords[0]
            screen_from_tunnel_y[x, y] = tex_coords[1]

    #pygame.surfarray.blit_array(screen, screen_from_tunnel_y)
    pygame.surfarray.blit_array(screen, array_texture[(screen_from_tunnel_x+10) % texture_width, screen_from_tunnel_y])
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
    #            current_screen.set_at((x, y), color_from_screen_coords(x, y, index_color))
    #    current_screen.unlock()
    #    if index_color % 10 == 0:
    #        print(index_color)

    #array_pixel = numpy.zeros((screen_size_x, screen_size_y))

    #for x in range(screen_size_x):
    #    for y in range(screen_size_y):
    #        array_pixel[x, y] = colorval_from_screen_coords(x, y, timer_tick)

    pause = False

    while going:

        clock.tick(50)

        # Handle Input Events
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                going = False
            elif event.type == pygame.locals.KEYDOWN:
                if event.key == pygame.locals.K_ESCAPE:
                    going = False
                if event.key == pygame.locals.K_SPACE:
                    pause = not pause

        if not pause:
            timer_tick += 10

        #array_pixel = [ 256*65536 + 200*256 + timer_tick ] * (screen_size_x*screen_size_y)
        #array_pixel = numpy.array(array_pixel)

        #new_array_pixel = numpy.array([cycle_red(colorval) for colorval in array_pixel])
        #new_array_pixel = numpy.array([colorval+1 for colorval in array_pixel])

        #new_array_pixel = v_cycle_red(array_pixel)
        #array_pixel = new_array_pixel

        #for x in range(screen_size_x):
        ##for x in range(190, 220):
        #    for y in range(screen_size_y):
        #        #array_pixel[x, y] = 256*65536 + 200*256 + timer_tick
        #        array_pixel[x, y] = colorval_from_screen_coords(x, y, timer_tick)


        #pygame.surfarray.blit_array(screen, array_pixel)

        #surf_array_background =  pygame.surfarray.pixels2d(background)
        #for x in range(screen_size_x):
        #    for y in range(screen_size_y):
        #        surf_array_background[x, y] = colorval_from_screen_coords(x, y, timer_tick)
        #del surf_array_background

        # Draw Everything
        #screen.blit(background, (0, 0))
        #screen.blit(speed_test[timer_tick & 255], (0, 0))

        pygame.surfarray.blit_array(screen, array_texture[(screen_from_tunnel_x+(timer_tick//2)) % texture_width, screen_from_tunnel_y])
        pygame.display.flip()

        if (timer_tick+4000) % 5000 == 0:
            snd_pere_200_1.play()

    pygame.quit()


if __name__ == '__main__':
    main()

