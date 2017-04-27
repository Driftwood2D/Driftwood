def setup(ent):
    print("New entity \"player\" with EID {0} at {1},{2},{3} ".format(str(ent.eid),
                                                                      str(ent.x),
                                                                      str(ent.y),
                                                                      str(ent.layer)))

    # Make this entity the player and set default walk keybinds.
    Driftwood.script.call("stdlib/player.py", "set_player", ent)
    Driftwood.script.call("stdlib/player.py", "set_eight_way_walk_keybinds")


def insert_from_tiled():
    """Search the loaded Area for a tile object with a "player_start" property that was placed within Tiled. Insert a
    player entity there.
    """
    map = Driftwood.area.tilemap
    tilewidth, tileheight = map.tilewidth, map.tileheight

    l, x, y = scan_for_player_start(map)

    if l is not None:
        Driftwood.entity.insert("Entities/player.json", layer=l, x=tilewidth*x, y=tileheight*y)


def scan_for_player_start(map):
    width, height = map.width, map.height

    for l, layer in enumerate(map.layers):
        for y in range(height):
            for x in range(width):
                if "player_start" in layer.tile(x, y).properties:
                    return l, x, y

    return None, None, None
