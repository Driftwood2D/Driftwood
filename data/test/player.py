def setup(ent):
    print("New entity \"player\" with EID {0} at {1},{2},{3} ".format(str(ent.eid),
                                                                      str(ent.x),
                                                                      str(ent.y),
                                                                      str(ent.layer)))

    # Make this entity the player and set default walk keybinds.
    Driftwood.script.call("libs/stdlib/player.py", "set_player", ent)
    Driftwood.script.call("libs/stdlib/player.py", "set_default_walk_keybinds")
