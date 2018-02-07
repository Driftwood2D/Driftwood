def setup(ent):
    print("New entity \"player\" with EID {0} at {1},{2},{3} ".format(str(ent.eid),
                                                                      str(ent.x),
                                                                      str(ent.y),
                                                                      str(ent.layer)))

    # Make this entity the player and set default walk keybinds.
    _["player"] = Driftwood.script["Folkdance/player.py"].PlayerManager(ent)
    _["player"].setup_default_keybinds(diagonal=False)
