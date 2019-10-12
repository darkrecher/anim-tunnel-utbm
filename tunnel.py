# coding: utf-8

import os, pygame
from pygame.locals import *
from pygame.compat import geterror

if not pygame.font: print('Warning, fonts disabled')
if not pygame.mixer: print('Warning, sound disabled')

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

screen_size_x = 400
screen_size_y = 300

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

    timer_color = 240

    # Display The Background
    screen.blit(background, (0, 0))
    pygame.display.flip()

    clock = pygame.time.Clock()
    going = True

    speed_test = [ pygame.Surface(screen.get_size()) for _ in range(256) ]
    for index_color in range(256):
        speed_test[index_color].fill((index_color, 0, 0))


    while going:

        clock.tick(60)

        # Handle Input Events
        for event in pygame.event.get():
            if event.type == QUIT:
                going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                going = False

        #background.lock()
        #for x in range(screen_size_x):
        #    for y in range(screen_size_y):
        #        background.set_at((x, y), (timer_color & 255, 0, 0))
        #background.unlock()
        timer_color += 1

        # Draw Everything
        #screen.blit(background, (0, 0))
        screen.blit(speed_test[timer_color & 255], (0, 0))
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
