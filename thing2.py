from __future__ import print_function

from pygame.locals import *

from gamelogic import *
from ui import *
from view import *
#

pygame.init()

# Wiring

pygameEventDispatcher = PygameEventDispatcher()

keyboardEventDispatcher = KeyboardEventDispatcher()
pygameEventDispatcher.addKeyDownHandler(keyboardEventDispatcher.keyDownCallback)
pygameEventDispatcher.addKeyUpHandler(keyboardEventDispatcher.keyUpCallback)

mouseEventDispatcher = MouseEventDispatcher()
pygameEventDispatcher.addMouseMotionHandler(mouseEventDispatcher.mouseMotionHandler)
pygameEventDispatcher.addMouseButtonDownHandler(mouseEventDispatcher.mouseButtonDownHandler)
pygameEventDispatcher.addMouseButtonUpHandler(mouseEventDispatcher.mouseButtonUpHandler)

timer = Timer()
gameTime = GameTime()
gameEventScheduler = GameEventScheduler()

# Level

grass = Tile('default', pygame.image.load('tile.png'))
gameMap = Map(dimensions=(20, 15), tileFunc=lambda x, y: grass)
guy = Mob((4, 2), pygame.image.load('stickfig.png'))
guyNavigator = MobNavigator(guy, gameEventScheduler)
gameMap.mobs.add(guy)

guard = Mob((5, 2), pygame.image.load('stickfig.png'))
guardNavigator = MobNavigator(guard, gameEventScheduler)
gameMap.mobs.add(guard)
guardNavigator.patrol([(5,5), (15,5), (10,10), (5,10)])


screenManager = ScreenManager()
mapView = MapView(map=gameMap,
                  screenManager=screenManager)

# Interactivity

keyboardEventDispatcher.addKeyDownHandler(K_w, lambda evt: guyNavigator.walk(( 0, -1)))
keyboardEventDispatcher.addKeyDownHandler(K_s, lambda evt: guyNavigator.walk(( 0,  1)))
keyboardEventDispatcher.addKeyDownHandler(K_a, lambda evt: guyNavigator.walk((-1,  0)))
keyboardEventDispatcher.addKeyDownHandler(K_d, lambda evt: guyNavigator.walk(( 1,  0)))

def shutdown(*args):
    global sys
    pygame.quit()
    sys.exit()

pygameEventDispatcher.addQuitHandler(shutdown)
keyboardEventDispatcher.addKeyDownHandler(K_q, shutdown)

keyboardEventDispatcher.addKeyDownHandler(K_SPACE, lambda evt: gameTime.toggle())

mouseEventDispatcher.addClickHandler(mapView.mouseClickCallback)
mouseEventDispatcher.addMoveHandler(mapView.mouseHoverCallback)

mapView.addTileClickHandler(lambda tileCoord: print("clicked on tile {}".format(tileCoord)))
mapView.addTileClickHandler(lambda tileCoord: guyNavigator.walkTo(tileCoord))

while True:
    pygameEventDispatcher.handleEvents(pygame.event.get())
    keyboardEventDispatcher.processTasks()

    # Physics
    dt = timer.elapsed()

    # Game logic
    gameEventScheduler.advanceBy(dt * gameTime.multiplier)

    # Render
    screenManager.clear()
    mapView.render()
    screenManager.flip()
