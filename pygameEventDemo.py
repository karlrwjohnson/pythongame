import pygame

SIZE = (640, 480)
TITLE = 'Pygame Event Demo'

pygame.init()
pygame.display.set_mode(SIZE)
pygame.display.set_caption(TITLE)

while True:
    for event in pygame.event.get():
        print repr(event)