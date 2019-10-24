import os
import math
import random
import numpy
import pygame
import pygame.locals
import pygame.surfarray
import pygame.mixer
from pygame.compat import geterror


main_dir = os.path.split(os.path.abspath(__file__))[0]
img_dir = os.path.join(main_dir, "img")

screen_size_x = 640
screen_size_y = 480

tunnel_diameter = 300
dist_focale = 100

time_show_white_circle = 2000

# Liste des sons. Sous-tuple de 3 éléments :
#  - nom du fichier .wav
#  - durée du son (en secondes)
#  - date (en tick de jeu) à laquelle il faut le jouer
#  - facteur de volume
ALL_SOUNDS = (
    ("partout_univers", 1.916, 5, 1),
    ("vous_elite", 2.435, 210, 10000),
    ("dechaine_les_enfers", 2.337, 360, 1),
    ("bar_ouvert", 1.488, 510, 0.5),
    ("pere200", 7.561, 590, 1),
    ("eni_ou_ipse", 2.363, 990, 1),
    ("tu_n_a_pas_eu_tes_bn", 2.224, 1150, 1),
    ("vous_nuls", 2.453, 1300, 1),
    ("pas_uv_pas_deutec", 4.058, 1430, 1),
    ("la_boheme", 4.789, 1640, 1),
    ("morceaux_utbm", 9.954, 1900, 1),
)


def load_image(name, colorkey=None, use_alpha=False):

    if colorkey and use_alpha:
        raise Exception("Soit colorkey, soit use_alpha, mais pas les deux.")
    fullname = os.path.join(img_dir, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print("Cannot load image:", fullname)
        raise SystemExit(str(geterror()))

    if use_alpha:
        image = image.convert_alpha()
    else:
        image = image.convert()

    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        # TODO : ça va planter, ça. On n'a pas de RLEACCEL.
        image.set_colorkey(colorkey, RLEACCEL)

    return image, image.get_rect()


def cylinder_coords_from_screen_coords(pix_x, pix_y):
    a_x = pix_x - screen_size_x / 2
    a_y = pix_y - screen_size_y / 2
    if (a_x, a_y) == (0, 0):
        raise ValueError(
            "La coordonnée du milieu de l'écran ne peut pas atteindre le cylindre"
        )
    # https://stackoverflow.com/questions/15994194/how-to-convert-x-y-coordinates-to-an-angle
    angle = math.atan2(a_y, a_x)
    cylinder_z = dist_focale * tunnel_diameter / (math.sqrt(a_x ** 2 + a_y ** 2))
    return angle, cylinder_z


def tex_coord_from_screen_coords(pix_x, pix_y, texture_width, texture_height):
    try:
        angle, cylinder_z = cylinder_coords_from_screen_coords(pix_x, pix_y)
    except ValueError:
        return (0, 0)
    tex_x = min(int(cylinder_z), texture_width)
    tex_y = int(((angle + math.pi) * (texture_height - 1)) / (2 * math.pi))
    # on décale tout de un cinquième, pour que le raccord moche entre
    # le haut et le bas de l'image ne soit pas pil poil sur la partie gauche du tunnel.
    tex_y = (tex_y + texture_height // 5) % texture_height
    return (tex_x, tex_y)


def load_sounds():
    all_sounds = []
    for sound_name, duration, date_play, volume_factor in ALL_SOUNDS:
        sound = pygame.mixer.Sound(os.path.join("audio", sound_name + ".ogg"))
        if volume_factor != 1:
            sound.set_volume(volume_factor)
        all_sounds.append((date_play, sound))
    all_sounds.sort(key=lambda x:x[0])
    return all_sounds


class Boulette():

    DEG_TO_RAD_FACTOR = (2*math.pi) / 360

    def __init__(self, boulette_imgs):
        self.boulette_imgs = boulette_imgs
        self.len_boulette_imgs = len(self.boulette_imgs)
        self.angle = 20.0
        self.dist = 0.0
        self.delta_angle = 0.0
        self.delta_angle_lim = 1.0
        self.delta_dist = 0.0
        self.delta_dist_lim = 0.5
        self.dist_min = 50
        self.dist_max = 100

    def change_polar_coords(self):
        # TODO : constantes, plize.
        accel_angle = random.randint(-50, 50) / 2000
        self.delta_angle += accel_angle
        if self.delta_angle < -self.delta_angle_lim:
            self.delta_angle -= accel_angle * 50
            #print("lim down", accel_angle, self.delta_angle, self.angle)
        if self.delta_angle > self.delta_angle_lim:
            self.delta_angle -= accel_angle * 50
            #print("lim up", accel_angle, self.delta_angle, self.angle)
        self.angle += self.delta_angle
        if self.angle < 0:
            self.angle += 360
        if self.angle > 360:
            self.angle -= 360

        accel_dist = random.randint(-50, 50) / 1000
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

    def get_cartez_coords(self):
        return (
            int(screen_size_x//2 + math.cos(self.angle*Boulette.DEG_TO_RAD_FACTOR)*self.dist),
            int(screen_size_y//2 + math.sin(self.angle*Boulette.DEG_TO_RAD_FACTOR)*self.dist)
        )

    def get_img_and_coords(self):
        # TODO : décalage de la moitié.
        index_boulette_rotation = int(((self.angle+7.5) / 360) * self.len_boulette_imgs) % self.len_boulette_imgs
        index_boulette_rotation = self.len_boulette_imgs - index_boulette_rotation - 1
        index_boulette_rotation += self.len_boulette_imgs//4
        if index_boulette_rotation >= self.len_boulette_imgs:
            index_boulette_rotation -= self.len_boulette_imgs

        # TODO : re constantes, plize.
        scale_factor = 0.1 + self.dist / 400
        boulette_rotated, rect_rotated, coord_hotpoint = self.boulette_imgs[
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


def main():

    # Initialize Everything
    random.seed("Des morceaux de l'uuuutééééébéééééhèèèèèème !")
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((screen_size_x, screen_size_y), pygame.NOFRAME)
    pygame.display.set_caption("Tunnel 3D")
    pygame.mouse.set_visible(0)

    all_sounds = load_sounds()

    texture, texture_rect = load_image("texture.png")
    texture_width = texture_rect.w
    texture_height = texture_rect.h

    array_texture_origin = pygame.surfarray.array2d(texture)
    # TODO : euh... y'a vraiment besoin de copier ?
    array_texture = array_texture_origin.copy()

    timer_tick = 0

    black_circle, black_circle_rect = load_image("fond_noir.png", use_alpha=True)
    coord_black_circle = (
        (screen_size_x - black_circle_rect.w) // 2,
        (screen_size_y - black_circle_rect.h) // 2,
    )

    img_boulette, boul_rect = load_image("boulette_01.png", use_alpha=True)
    boul_rect = pygame.Rect(0, 0, int(boul_rect.w*0.25), int(boul_rect.h*0.25))
    boulette_scaled = pygame.transform.scale(
        img_boulette,
        (boul_rect.w, boul_rect.h),
    )


    print("precalc tunnel mapping")
    # Si la taille (width ou height) de l'image de texture ne tient pas
    # dans un int 32 bits, ça va péter. Mais franchement osef.
    screen_from_tunnel_x = numpy.zeros((screen_size_x, screen_size_y), dtype="u4")
    screen_from_tunnel_y = numpy.zeros((screen_size_x, screen_size_y), dtype="u4")
    screen_from_tunnel_x_lim = numpy.zeros((screen_size_x, screen_size_y), dtype="u4")

    for x in range(screen_size_x):
        for y in range(screen_size_y):
            tex_coords = tex_coord_from_screen_coords(
                x, y, texture_width, texture_height
            )
            screen_from_tunnel_x[x, y] = tex_coords[0]
            screen_from_tunnel_y[x, y] = tex_coords[1]
            screen_from_tunnel_x_lim[x, y] = texture_width - 1

    print("precalc circle alpha source")
    white_circle = pygame.Surface((screen_size_x, screen_size_y), flags=pygame.SRCALPHA)
    white_circle.fill((255, 255, 255))
    # Matrice contenant la distance (en pixels) par rapport au centre de l'écran.
    white_circle_alpha_source = numpy.zeros((screen_size_x, screen_size_y), dtype="u4")
    for x in range(screen_size_x):
        for y in range(screen_size_y):
            val = ((x-screen_size_x//2)**2 + (y-screen_size_y//2)**2)**0.5
            white_circle_alpha_source[x, y] = val

    # Précalcul de la transparence du cercle blanc qui apparaît à la fin
    print("precalc white_circle_alphas")
    white_circle_alphas = []
    white_circle_temp = numpy.zeros((screen_size_x, screen_size_y), dtype="u4")
    min_circles = [0] * 50 + [ int(r**1.2) for r in range(150) ]
    max_circles = [ 1+int(r**1.2) for r in range(200) ]

    for min_dist, max_dist in zip(min_circles, max_circles):
        #white_circle_temp[:] = 255-((white_circle_alpha_source-50)*255)//150
        #white_circle_temp[white_circle_alpha_source < 50] = 255
        #white_circle_temp[white_circle_alpha_source >= 200] = 0
        #min_dist = circle_index*2
        #max_dist = min_dist+100
        white_circle_temp[:] = 255-((white_circle_alpha_source-min_dist)*255)//(max_dist-min_dist)
        white_circle_temp[white_circle_alpha_source < min_dist] = 255
        white_circle_temp[white_circle_alpha_source >= max_dist] = 0
        white_circle_next = numpy.zeros((screen_size_x, screen_size_y), dtype="u1")
        white_circle_next[:] = white_circle_temp
        white_circle_alphas.append(white_circle_next)

    print("precalc boulette rotations")
    # TODO : constantes pour le nombre d'image de boulette, et le step de rotation.
    # TODO : (quand ce sera fait)
    # tuples imbriqués.
    # Chaque elem du tuple le plus haut représente l'une des 6 images possibles de la boulette de papier.
    # C'est un sous-tuple. Chaque elem de ce sous-tuple représente une image rotatée de la boulette.
    # Rotatée à 15 degrés, puis 30, 45, etc. Ce sont des sous-sous-tuple.
    # Le premier elem du sous-sous-tuple est l'image elle-même.
    # Le deuxième est la taille de l'image.
    # Le troisième est le vecteur (x, y) de décalage.
    boulette_imgs = []
    for angle in range(0, 360, 15):
        vect_center_to_middle_down = pygame.math.Vector2(0, boul_rect.h//2)
        # Je sais pas pourquoi faut mettre "-angle" et pas "angle".
        # Sûrement un truc compliqué de matheux.
        vect_center_to_middle_down = vect_center_to_middle_down.rotate(-angle)
        boulette_rotated = pygame.transform.rotate(boulette_scaled, angle)
        rect_rotated = boulette_rotated.get_rect()
        coord_hotpoint = (
            -rect_rotated.w//2 - vect_center_to_middle_down.x,
            -rect_rotated.h//2 - vect_center_to_middle_down.y
        )
        boulette_imgs.append((boulette_rotated, rect_rotated, coord_hotpoint))

    # TODO : duplicate code avec la main loop. De plus, j'affiche pas le fond noir.
    # Bref, beurk, à homogénéiser.
    pygame.surfarray.blit_array(
        screen,
        array_texture[
            (screen_from_tunnel_x + 10) % texture_width, screen_from_tunnel_y
        ],
    )
    pygame.display.flip()

    clock = pygame.time.Clock()
    going = True
    pause = False
    boulette = Boulette(boulette_imgs)

    # Déclenchement de la musique de fond.
    pygame.mixer.music.load("audio\\Synthesia_La_Soupe_Aux_Choux_theme.ogg")
    pygame.mixer.music.set_volume(0.95)

    print("start loop")

    while going:

        clock.tick(50)

        # Gestion des événements d'input (les touches, et la fermeture de la fenêtre)
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                going = False
            elif event.type == pygame.locals.KEYDOWN:
                if event.key == pygame.locals.K_ESCAPE:
                    going = False
                if event.key == pygame.locals.K_SPACE:
                    pause = not pause

        # TODO : c'est un peu à l'arrache tout ça. Faudrait des constantes
        # pour configurer plus clairement la vitesse d'avancée du tunnel
        # et les dates de jeu des sons.
        if not pause:
            timer_tick += 1

        pygame.surfarray.blit_array(
            screen,
            array_texture[
                numpy.minimum(screen_from_tunnel_x + (timer_tick * 4), screen_from_tunnel_x_lim),
                screen_from_tunnel_y,
            ],
        )

        # Gestion de la boulette de papier.
        boulette.change_polar_coords()
        boulette_scaled, coord_img_left_up = boulette.get_img_and_coords()
        screen.blit(boulette_scaled, (coord_img_left_up[0], coord_img_left_up[1]))

        screen.blit(black_circle, coord_black_circle)

        # Affichage de la lumière finale.
        if timer_tick > time_show_white_circle:
            circle_index = timer_tick - time_show_white_circle
            if circle_index < len(white_circle_alphas):
                white_circle_alpha = pygame.surfarray.pixels_alpha(white_circle)
                white_circle_alpha[:] = white_circle_alphas[circle_index]
                del white_circle_alpha
            screen.blit(white_circle, (0, 0))

        pygame.display.flip()

        while all_sounds and all_sounds[0][0] < timer_tick:
            date_play, current_sound = all_sounds.pop(0)
            current_sound.play()

        # TODO : ajouter une constante pour ces nombres, please.
        if timer_tick == 100:
            pygame.mixer.music.play()

        if timer_tick == 1870:
            pygame.mixer.music.fadeout(500)

        # TODO : test de rapidité. plutôt OK. Du coup, l'anim est moche, mais osef c'est provisoire.
        #white_circle_temp[:] = 255-((white_circle_alpha_source-50)*255)//150
        #white_circle_temp[white_circle_alpha_source < 50] = 255
        #white_circle_temp[white_circle_alpha_source >= 200] = 0

        #white_circle_temp[white_circle_alpha_source > timer_tick*1.5] = 0
        #white_circle_temp[white_circle_alpha_source <= timer_tick*1.1] = 255
        ##white_circle_temp[(white_circle_alpha_source > timer_tick*1.1) and (white_circle_alpha_source < timer_tick*1.5)] -= timer_tick*1.1
        #white_circle_temp[numpy.all([
        #    white_circle_alpha_source > timer_tick*1.1,
        #    white_circle_alpha_source < timer_tick*1.5])
        #] = (white_circle_alpha_source - timer_tick*1.1)*255 / (timer_tick*1.5 - timer_tick*1.1)


    pygame.quit()


if __name__ == "__main__":
    main()
