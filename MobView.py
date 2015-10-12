import numpy

class MobView (object):
    def __init__(self):
        pass

    def render(self, zone_view, mob):
        if mob.walk_animation is None:
            position = mob.position
        else:
            progress = mob.walk_animation.progress
            source_coord = numpy.array(mob.walk_animation.source_coord)
            dest_coord = numpy.array(mob.walk_animation.dest_coord)
            position = source_coord * (1.0 - progress) + dest_coord * progress

        zone_view.blit_world_sprite(mob.sprite, position)
