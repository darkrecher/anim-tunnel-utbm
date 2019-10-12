
# Exemple pourri.
# https://stackoverflow.com/questions/4532008/putpixel-with-pyglet
# Le vrai bon code qui sert à quelque chose.
# https://gamedev.stackexchange.com/questions/55945/how-to-draw-image-in-memory-manually-in-pyglet

import pyglet
window = pyglet.window.Window(300, 300)
#background = pyglet.resource.image('my600x600blackbackground.bmp')
background = pyglet.image.SolidColorImagePattern((0,0,255,255)).create_image(300, 300)
#background = pyglet.AbstractImage(300, 300)
#background = pyglet.image.load('black300.bmp')
#pix = pyglet.resource.image('singlewhitepixel.bmp').get_image_data()
#pix = pyglet.resource.image('singlewhitepixel.bmp')
#pix = pyglet.image.SolidColorImagePattern((255,255,255,255)).create_image(1, 1)
pix = pyglet.image.load('singlewhitepixel.bmp')

print(background)
print(pix)

def update(dt, crap):
    x = 10
    y = 10
    #background.blit_into(pix, x, y, 0) #specify x and y however you want
    background.blit_into(pix, x, y, 0) #specify x and y however you want

#update("", "")

#background.blit_into(pix, 0, 0, 0)

label = pyglet.text.Label(
    'Hello World', font_name='Times New Roman', font_size=36,
    x=150, y=150,
    anchor_x='center', anchor_y='center',
)

print(label)

pixels = [ 255, 0, 0, 0, 0, 0, 255, 255, 0, ] * 9
raw_data = (pyglet.gl.GLubyte * len(pixels))(*pixels)
image_data = pyglet.image.ImageData(3, 3, 'RGB', raw_data)

@window.event
def on_draw():
    window.clear()
    #label.draw()
    background.blit(0,0)
    #pix.blit(10, 10)
    image_data.blit(10, 10)
    print("J'ai drawed")

#pyglet.clock.schedule(update, 1.0/3) #3 frames per second
pyglet.app.run()
