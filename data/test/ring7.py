def kill_door():
    Driftwood.script["rumble.py"].end_rumble()
    Driftwood.tick.register(kill_door_callback1, once=True, delay=1.0)
    Driftwood.tick.register(kill_door_callback2, once=True, delay=2.0)
    Driftwood.tick.register(kill_door_callback3, once=True, delay=3.0)


def kill_door_callback1(seconds_past):
    Driftwood.area.tilemap.layers[1].tiles[51].setgid(18)
    Driftwood.area.changed = True


def kill_door_callback2(seconds_past):
    Driftwood.area.tilemap.layers[1].tiles[51].setgid(19)
    Driftwood.area.changed = True


def kill_door_callback3(seconds_past):
    Driftwood.area.tilemap.layers[1].tiles[51].setgid(20)
    Driftwood.area.changed = True

