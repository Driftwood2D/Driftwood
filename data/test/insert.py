def setup(ent):
    print("New entity with EID {0} at {1},{2},{3} ".format(str(ent.eid),
                                                                str(ent.x),
                                                                str(ent.y),
                                                                str(ent.layer)))

    Driftwood.script.call("libs/stdlib/player.py", "set_player", args=ent)
    Driftwood.script.call("libs/stdlib/player.py", "set_default_walk_keybinds")

