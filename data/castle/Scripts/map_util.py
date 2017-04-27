def tiles_with_property(map, prop_name):
    """Search the specified Tilemap for all tile object with a property called prop_name.
    """
    width, height = map.width, map.height

    for l, layer in enumerate(map.layers):
        for y in range(height):
            for x in range(width):
                if prop_name in layer.tile(x, y).properties:
                    yield l, x, y
