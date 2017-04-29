map_util = Driftwood.script["Scripts/map_util.py"]


def setup(ent):
    print("New entity \"player\" with EID {0} at {1},{2},{3} ".format(str(ent.eid),
                                                                      str(ent.x),
                                                                      str(ent.y),
                                                                      str(ent.layer)))

    # Make this entity the player and set default walk keybinds.
    Driftwood.script.call("stdlib/player.py", "set_player", ent)
    Driftwood.script.call("stdlib/player.py", "set_eight_way_walk_keybinds")


def insert_from_tiled():
    map = Driftwood.area.tilemap
    tilewidth, tileheight = map.tilewidth, map.tileheight

    for l, x, y in map_util.tiles_with_property(map, "player_start"):
        Driftwood.entity.insert("Entities/player.json", layer=l, x=tilewidth*x, y=tileheight*y)
        break  # Only take the first one found.
