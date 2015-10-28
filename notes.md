Notes
=====

Lifecycle of maps
-----------------

- Everything can be serialized. Including event callbacks, so long as I stick
  to instance methods, thanks to my patch.
- In lieu of a map editor, maps could be edited in a spreadsheet, exported in
  a simple format, and parsed out with Python.
    * Maybe I could even use LibreOffice to export it??!?
        - I could use that experience to build a LibreOffice-based tab editor
- Extra info could be specified in a Python script along side the spreadsheet
- Makefile??
- Anyway, the spreadsheet + extra data gets "compiled" -- read in and pickled --
  into a map file.

- Maps contain tile data, a TimedEventDispatcher, mobs, actions already in
  motion, event zones, and spawn points.

- Maps get loaded by unpickling them. To save map state, we could re-pickle them
  and write them back out after de-spawning the PC. Maybe maps should have some
  sort of cleanup logic function.

To Do
-----

- Implement ui chrome
- UIView should be able to tell what's UI chrome and what isn't
- Player mob might need to be attached to the model, not the controller
- Map needs spawn points
- Combat
- Diagonal movement
- Real pathfinding
- Obstacles
- Line-of-sight
- Fog of war ("seen" flag on tiles?)
- Pausable time
- Mechanism to auto-pause time when PC is done doing something?
- Fix bug where arrow keys send mob one tile past where they intend
- Either use the backported enums, or make your own
- Sprite library and figure out how to keep them from being serialized. (string key?)
