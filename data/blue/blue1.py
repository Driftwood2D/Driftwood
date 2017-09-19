def setup():
    a = Driftwood.light.insert("lightmap_vertical1.png", 2, 2, 80, 50, 160, "000000FF", blend=True)
    b = Driftwood.light.insert("lightmap_vertical1.png", 2, 158, 80, 50, 160, "000000FF", blend=True)

    # Prepare earthquake.
    if "got_blue_pearl" not in Driftwood.database:
        Driftwood.script["rumble.py"].regular_rumble(15, 3, 5, 10)
    else:
        Driftwood.script["rumble.py"].constant_rumble(10, 3)

