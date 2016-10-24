def lights():
    if not "got_blue_pearl" in Driftwood.database:
        a = Driftwood.light.insert("lightmap_circle1.png", 2, 80, 20, 48, 48, "4444FFEE")
        b = Driftwood.light.insert("lightmap_circle1.png", 2, 20, 60, 48, 48, "4444FFEE")
        c = Driftwood.light.insert("lightmap_circle1.png", 2, 140, 60, 48, 48, "4444FFEE")
        Driftwood.script.call("libs/stdlib/light.py", "flicker", a.lid, 0, 0, 64, 16)
        Driftwood.script.call("libs/stdlib/light.py", "flicker", b.lid, 0, 0, 64, 16)
        Driftwood.script.call("libs/stdlib/light.py", "flicker", c.lid, 0, 0, 64, 16)
    
    else:
        a = Driftwood.light.insert("lightmap_circle1.png", 2, 80, 56, 160, 160, "FFFFFFFF", blend=True)
        b = Driftwood.light.insert("lightmap_circle1.png", 3, 80, 56, 128, 100, "4444FFEE", blend=True)
        Driftwood.script.call("libs/stdlib/light.py", "flicker", b.lid, 0, 0, 40, 8)
