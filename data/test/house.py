def open_door():
    Driftwood.area.tilemap.layers[1].tiles[5].nowalk = None
    Driftwood.area.tilemap.layers[1].tiles[5].localgid = 66
    Driftwood.area.tilemap.layers[1].tiles[5].gid = 66
    Driftwood.area.tilemap.layers[1].tiles[5].members = [65]


def focus():
    if Driftwood.tick.registered(Driftwood.vars["init_rumble_tick_callback"]):
        Driftwood.tick.unregister(Driftwood.vars["init_rumble_tick_callback"])
    a = Driftwood.light.insert("lightmap_circle1.png", 2, 7, 115, 32, 32, "FFCC4466")
    b = Driftwood.light.insert("lightmap_circle1.png", 2, 153, 115, 32, 32, "FFCC4466")
    c = Driftwood.light.insert("lightmap_circle1.png", 2, 40, 7, 32, 32, "FFCC4466")
    Driftwood.script.call("libs/stdlib/light.py", "flicker", a.lid, 0, 0, 10, 8)
    Driftwood.script.call("libs/stdlib/light.py", "flicker", b.lid, 0, 0, 10, 8)
    Driftwood.script.call("libs/stdlib/light.py", "flicker", c.lid, 0, 0, 10, 8)
