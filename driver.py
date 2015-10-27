"""
Architecture paradigms:
- Model-View-Controller
   * Views only know how to render stuff and depend on their model and their master-view
   * Controllers dispatch UI events
- Event-based: Most components are Observable and broadcast updates
- Listeners are auto-wiring: components register themselves as event listeners on assignment
- Components may be injected directly in the constructor, eliminating the need for manual wiring
"""

from __future__ import print_function

import argparse
import pygame

import Observable

from Mob import Mob
from UIController import UIController
from UIView import UIView
from util import resolution_pair
from Zone import Zone
from ZoneController import ZoneController
from ZoneView import ZoneView

PARSER = argparse.ArgumentParser()
PARSER.add_argument('-s', '--screen_size', type=resolution_pair, default='640x480',
                    help='Window dimensions')
PARSER.add_argument('-f', '--framerate', type=int, default=60,
                    help='Limit rendering passes per second')
PARSER.add_argument('-d', '--debug', type=bool, default=False,
                    help='Log message broadcasts for debugging')
ARGS = PARSER.parse_args()

# Settings

WINDOW_CAPTION = 'Game Title Here'
Observable.debug_events = ARGS.debug

# Model
zone = Zone(dimensions=(20,15))

grass_sprite = pygame.image.load('img/tile.png')
for tile in zone.tiles:
    tile.sprite = grass_sprite

stick_fig_sprite = pygame.image.load('img/stickfig.png')
pc = Mob(tile=zone.tiles[(4, 2)], sprite=stick_fig_sprite)

guard = Mob(tile=zone.tiles[(5, 2)], sprite=stick_fig_sprite)
guard.patrol([
    zone.tiles[coord]
    for coord in [(5,5), (15,5), (10,10), (5,10)]
])

# View
ui_view = UIView(size=ARGS.screen_size, caption=WINDOW_CAPTION)
zone_view = ZoneView(zone=zone, ui_view=ui_view)

# Controller
ui_controller = UIController(view=ui_view, framerate=ARGS.framerate)
zone_controller = ZoneController(zone=zone, view=zone_view, ui_controller=ui_controller, pc=pc)

# Run
ui_controller.run()

# End

#TODO: Do a proper destructor
pygame.quit()
