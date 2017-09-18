def open_door():
    Driftwood.area.tilemap.layers[1].tiles[5].nowalk = None
    Driftwood.area.tilemap.layers[1].tiles[5].localgid = 66
    Driftwood.area.tilemap.layers[1].tiles[5].gid = 66
    Driftwood.area.tilemap.layers[1].tiles[5].members = [65]


def focus():
    a = Driftwood.light.insert("lightmap_circle1.png", 2, 7, 115, 32, 32, "FFCC4466")
    b = Driftwood.light.insert("lightmap_circle1.png", 2, 153, 115, 32, 32, "FFCC4466")
    c = Driftwood.light.insert("lightmap_circle1.png", 2, 40, 7, 32, 32, "FFCC4466")
    Driftwood.script["stdlib/light.py"].flicker(a.lid, 0, 0, 10, 8)
    Driftwood.script["stdlib/light.py"].flicker(b.lid, 0, 0, 10, 8)
    Driftwood.script["stdlib/light.py"].flicker(c.lid, 0, 0, 10, 8)
