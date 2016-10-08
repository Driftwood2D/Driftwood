def set_player(ent):
    """Set the entity "ent" as the player character.
    """
    Driftwood.entity.player = ent
    return True

def set_default_walk_keybinds():
    """Setup the default walk keybinds.
    """
    if not Driftwood.entity.player:
        return False
    
    Driftwood.input.register("up", __default_keybind_move_up)
    Driftwood.input.register("down", __default_keybind_move_down)
    Driftwood.input.register("left", __default_keybind_move_left)
    Driftwood.input.register("right", __default_keybind_move_right)
    Driftwood.input.register("interact", __default_keybind_interact)
    
    return True

def __default_keybind_move_up(keyevent):
    player = Driftwood.entity.player
    if keyevent == Driftwood.input.ONDOWN:
        player._walk_stop()
        player.walk(0, -1, dont_stop=True, stance="walk_up", end_stance="face_up")
    elif keyevent == Driftwood.input.ONREPEAT:
        player.walk(0, -1, dont_stop=True, stance="walk_up", end_stance="face_up")
    elif keyevent == Driftwood.input.ONUP:
        player._walk_stop()

def __default_keybind_move_down(keyevent):
    player = Driftwood.entity.player
    if keyevent == Driftwood.input.ONDOWN:
        player._walk_stop()
        player.walk(0, 1, dont_stop=True, stance="walk_down", end_stance="face_down")
    elif keyevent == Driftwood.input.ONREPEAT:
        player.walk(0, 1, dont_stop=True, stance="walk_down", end_stance="face_down")
    elif keyevent == Driftwood.input.ONUP:
        player._walk_stop()

def __default_keybind_move_left(keyevent):
    player = Driftwood.entity.player
    if keyevent == Driftwood.input.ONDOWN:
        player._walk_stop()
        player.walk(-1, 0, dont_stop=True, stance="walk_left", end_stance="face_left")
    if keyevent == Driftwood.input.ONREPEAT:
        player.walk(-1, 0, dont_stop=True, stance="walk_left", end_stance="face_left")
    elif keyevent == Driftwood.input.ONUP:
        player._walk_stop()

def __default_keybind_move_right(keyevent):
    player = Driftwood.entity.player
    if keyevent == Driftwood.input.ONDOWN:
        player._walk_stop()
        player.walk(1, 0, dont_stop=True, stance="walk_right", end_stance="face_right")
    if keyevent == Driftwood.input.ONREPEAT:
        player.walk(1, 0, dont_stop=True, stance="walk_right", end_stance="face_right")
    elif keyevent == Driftwood.input.ONUP:
        player._walk_stop()

def __default_keybind_interact(keyevent):
    player = Driftwood.entity.player
    if keyevent == Driftwood.input.ONDOWN:
        if not player.interact():
            player.interact("under")

