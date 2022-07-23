import os, sys
import nibabel as nib
import pygame as pg
import numpy as np

from driver import *

path = '/Users/pscovel/Documents/data/placenta-segmentation/test_inference/MAP-C517-L2'

volumes = ImageSet(os.path.join(path, 'volume'))
segmentations = ImageSet(os.path.join(path, 'predicted_segmentation'))

pg.init()
pg.display.set_caption('Placenta Segmentation')
font = pg.font.SysFont('Times New Roman', 20)
clock = pg.time.Clock()

SCREEN_WIDTH, SCREEN_HEIGHT = (1200, 700)
dimension = volumes.data[0].shape
pos = [i // 2 for i in dimension]
vminmax = volumes.minmax()
sminmax = segmentations.minmax()
stoggle = True
sopacity = 0.3
frame = 0
scale = 3
scolor = (0, 128, 128)

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
xview = pg.Surface((dimension[1], dimension[2]))
yview = pg.Surface((dimension[0], dimension[2]))
zview = pg.Surface((dimension[0], dimension[1]))

xbox = [[0, 0]]
ybox = [[0, 300]]
zbox = [[500, 0]]

xbox.append([xbox[0][0] + dimension[1] * scale, xbox[0][1] + dimension[2] * scale])
ybox.append([ybox[0][0] + dimension[0] * scale, ybox[0][1] + dimension[2] * scale])
zbox.append([zbox[0][0] + dimension[0] * scale, zbox[0][1] + dimension[1] * scale])

print(xbox)
print(ybox)
print(zbox)

clicked = False
scroll = 0
framerate = 5
playing = False
mouseX, mouseY = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.MOUSEBUTTONDOWN:
            mouseX, mouseY = event.pos
            if event.button == 1:
                clicked = True
            if event.button == 4:
                scroll = 1
            if event.button == 5:
                scroll = -1
        if event.type == pg.MOUSEMOTION and event.buttons[0]:
            mouseX, mouseY = event.pos
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                playing = not playing
            if event.key == pg.K_w:
                stoggle = not stoggle
            if event.key == pg.K_q and stoggle:
                if sopacity >= 0.05:
                    sopacity = round(sopacity - 0.05, 2)
            if event.key == pg.K_e and stoggle:
                if sopacity <= 0.95:
                    sopacity = round(sopacity + 0.05, 2)

    keys = pg.key.get_pressed()
    if keys[pg.K_UP]:
        if framerate >= 60:
            framerate = 60
        else:
            framerate += 1
    if keys[pg.K_DOWN]:
        if framerate <= 1:
            framerate = 1
        else:
            framerate -= 1

    if scroll:
        if xbox[0][0] < mouseX < xbox[1][0]:
            if xbox[0][1] < mouseY < xbox[1][1]:
                if scroll  > 0 and pos[0] < dimension[0]:
                    pos[0] += scroll
                if scroll < 0 and pos[0] > 0:
                    pos[0] += scroll
        if ybox[0][0] < mouseX < ybox[1][0]:
            if ybox[0][1] < mouseY < ybox[1][1]:
                if scroll > 0 and pos[1] < dimension[1]:
                    pos[1] += scroll
                if scroll < 0 and pos[1] > 0:
                    pos[1] += scroll
        if zbox[0][0] < mouseX < zbox[1][0]:
            if zbox[0][1] < mouseY < zbox[1][1]:
                if scroll > 0 and pos[2] < dimension[2]:
                    pos[2] += scroll
                if scroll < 0 and pos[2] > 0:
                    pos[2] += scroll

    if playing:
        frame = (frame + 1) % len(volumes.data)

    vdataX, sdataX = volumes.slice(frame, pos[0], axis=0), segmentations.slice(frame, pos[0], axis=0)
    vdataY, sdataY = volumes.slice(frame, pos[1], axis=1), segmentations.slice(frame, pos[1], axis=1)
    vdataZ, sdataZ = volumes.slice(frame, pos[2], axis=2), segmentations.slice(frame, pos[2], axis=2)

    dataX = gray(vdataX) * (1 - sopacity) + color(sdataX, scolor) * sopacity * int(stoggle)
    dataY = gray(vdataY) * (1 - sopacity) + color(sdataY, scolor) * sopacity * int(stoggle)
    dataZ = gray(vdataZ) * (1 - sopacity) + color(sdataZ, scolor) * sopacity * int(stoggle)

    xview = pg.transform.scale(pg.surfarray.make_surface(dataX), (dimension[1] * scale, dimension[2] * scale))
    yview = pg.transform.scale(pg.surfarray.make_surface(dataY), (dimension[0] * scale, dimension[2] * scale))
    zview = pg.transform.scale(pg.surfarray.make_surface(dataZ), (dimension[0] * scale, dimension[1] * scale))
    
    screen.fill((0, 0, 0))

    xlabel = font.render(f'X - {pos[0]} / {dimension[0]}', True, (255, 255, 255))
    ylabel = font.render(f'Y - {pos[1]} / {dimension[1]}', True, (255, 255, 255))
    zlabel = font.render(f'Z - {pos[2]} / {dimension[2]}', True, (255, 255, 255))
    
    flabel = font.render(f'Frame - {frame} / {len(volumes.data) - 1}', True, (255, 255, 255))
    rlabel = font.render(f'Framerate - {framerate}', True, (255, 255, 255))
    plabel = font.render(f'Playing - {playing}', True, (255, 255, 255))
    olabel = font.render(f'Opacity - {sopacity if stoggle else 0}', True, scolor, tuple(255 - i for i in scolor))

    screen.blit(xview, xbox[0])
    screen.blit(yview, ybox[0])
    screen.blit(zview, zbox[0])

    screen.blit(xlabel, (xbox[0][0] + 10, xbox[1][1] + 10))
    screen.blit(ylabel, (ybox[0][0] + 10, ybox[1][1] + 10))
    screen.blit(zlabel, (zbox[0][0] + 10, zbox[1][1] + 10))

    screen.blit(flabel, (SCREEN_WIDTH - 150, 10))
    screen.blit(rlabel, (10, SCREEN_HEIGHT - 30))
    screen.blit(plabel, (10, SCREEN_HEIGHT - 50))
    screen.blit(olabel, (SCREEN_WIDTH - 150, 30))

    clicked = False
    scroll = 0
    
    clock.tick(framerate if playing else 10)
    pg.display.flip()
pg.quit()
