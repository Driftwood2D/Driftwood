def lights():
    if "blue_pearl_active" not in Driftwood.database:
        a = Driftwood.light.insert("lightmap_circle1.png", 2, 80, 20, 48, 48, "4444FFEE")
        b = Driftwood.light.insert("lightmap_circle1.png", 2, 20, 60, 48, 48, "4444FFEE")
        c = Driftwood.light.insert("lightmap_circle1.png", 2, 140, 60, 48, 48, "4444FFEE")
        Driftwood.script.call("libs/stdlib/light.py", "flicker", a.lid, 0, 0, 64, 16)
        Driftwood.script.call("libs/stdlib/light.py", "flicker", b.lid, 0, 0, 64, 16)
        Driftwood.script.call("libs/stdlib/light.py", "flicker", c.lid, 0, 0, 64, 16)

    else:
        if "end_rumble" in Driftwood.vars and Driftwood.vars["end_rumble"]:
            Driftwood.script.call("libs/stdlib/viewport.py", "end_rumble")
        Driftwood.vars["end_rumble"] = "true"
        Driftwood.script.call("libs/stdlib/viewport.py", "rumble", 30, 2, None)
        Driftwood.light.reset()
        a = Driftwood.light.insert("lightmap_circle1.png", 2, 80, 56, 160, 160, "FFFFFFFF", blend=False)
        c = Driftwood.light.insert("lightmap_circle1.png", 3, 80, 56, 100, 100, "8888FFFF", blend=False)
        d = Driftwood.light.insert("lightmap_circle1.png", 3, 80, 56, 200, 200, "FF8888FF", blend=False)
        b = Driftwood.light.insert("lightmap_circle1.png", 3, 80, 56, 128, 100, "4444FFEE", blend=True)
        Driftwood.script.call("libs/stdlib/light.py", "flicker", b.lid, 0, 0, 40, 8)
        Driftwood.script.call("libs/stdlib/light.py", "flicker", a.lid, 0, 0, 120, 6)


def activate_pearl():
    if "got_blue_pearl" in Driftwood.database and "blue_pearl_active" not in Driftwood.database:
        Driftwood.database["blue_pearl_active"] = "true"
        lights()
