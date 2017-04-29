map_util = Driftwood.script["Scripts/map_util.py"]


def setup(ent):
    print("New entity \"scimitar\" with EID {0} at {1},{2},{3} ".format(str(ent.eid),
                                                                        str(ent.x),
                                                                        str(ent.y),
                                                                        str(ent.layer)))
    ent.set_stance("init")


def insert_from_tiled():
    map = Driftwood.area.tilemap
    tilewidth, tileheight = map.tilewidth, map.tileheight

    for l, x, y in map_util.tiles_with_property(map, "scimitar"):
        Driftwood.entity.insert("Entities/scimitar.json", layer=l, x=tilewidth*x, y=tileheight*y)
