import random


def setup(ent):
    print("New entity \"wizard\" with EID {0} at {1},{2},{3} ".format(str(ent.eid),
                                                                      str(ent.x),
                                                                      str(ent.y),
                                                                      str(ent.layer)))
    
    Driftwood.tick.register(move, delay=2.0, message=ent)

    Driftwood.light.insert("lightmap_circle1.png", 0, 0, 0, 64, 64, "FFFFFFAA", entity=ent.eid, layermod=-1)


def kill(ent):
    Driftwood.tick.unregister(move)


def move(seconds_past, ent):
    rand = random.randint(1, 8)
    if rand == 1:
        ent.walk(0, -1, dont_stop=False, stance="walk_up", end_stance="face_up")
    elif rand == 2:
        ent.walk(0, 1, dont_stop=False, stance="walk_down", end_stance="face_down")
    elif rand == 3:
        ent.walk(-1, 0, dont_stop=False, stance="walk_left", end_stance="face_left")
    elif rand == 4:
        ent.walk(1, 0, dont_stop=False, stance="walk_right", end_stance="face_right")
