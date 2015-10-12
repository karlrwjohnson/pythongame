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

# Wiring

ui_view = UIView(size=ARGS.screen_size, caption=WINDOW_CAPTION)
ui_controller = UIController(view=ui_view, framerate=ARGS.framerate)

zone = Zone(dimensions=(20,15))
zone_view = ZoneView(model=zone, ui_view=ui_view)
zone_controller = ZoneController(model=zone, view=zone_view, ui_controller=ui_controller)

# Manually create level

# (done in ZoneController while I figure out how it's supposed to happen)

# Run

ui_controller.run()

# End

#TODO: Do a proper destructor
pygame.quit()
