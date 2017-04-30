map_util = Driftwood.script["Scripts/map_util.py"]


entity_types = [
    "player",
    "scimitar",
]


def insert_entities_from_tiled():
    for entity_type in entity_types:
        insert_from_tiled(entity_type)


def insert_from_tiled(entity_type):
    descriptor = "Entities/{}.json".format(entity_type)
    prop_name = entity_type

    tilemap = Driftwood.area.tilemap
    tilewidth, tileheight = tilemap.tilewidth, tilemap.tileheight

    for l, x, y in map_util.tiles_with_property(tilemap, prop_name):
        Driftwood.entity.insert(descriptor, layer=l, x=tilewidth*x, y=tileheight*y)
