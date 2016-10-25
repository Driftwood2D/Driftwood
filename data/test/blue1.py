def setup():
    a = Driftwood.light.insert("lightmap_vertical1.png", 2, 2, 80, 50, 160, "000000FF", blend=True)
    b = Driftwood.light.insert("lightmap_vertical1.png", 2, 158, 80, 50, 160, "000000FF", blend=True)
    if "got_blue_pearl" in Driftwood.database and "end_rumble" in Driftwood.vars and Driftwood.vars["end_rumble"]:
        Driftwood.script.call("libs/stdlib/viewport.py", "end_rumble")
        Driftwood.vars["end_rumble"] = "true"
        Driftwood.script.call("libs/stdlib/viewport.py", "rumble", 10, 3, None)