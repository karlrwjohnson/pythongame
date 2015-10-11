class MobView (object):
    def __init__(self):
        pass

    def render(self, zone_view, mob):
        if mob.walk_animation is None:
            position = mob.position

        else:
            pass

        zone_view.blit_world_sprite(mob.sprite, position)
