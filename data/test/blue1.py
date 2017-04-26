def setup():
    a = Driftwood.light.insert("lightmap_vertical1.png", 2, 2, 80, 50, 160, "000000FF", blend=True)
    b = Driftwood.light.insert("lightmap_vertical1.png", 2, 158, 80, 50, 160, "000000FF", blend=True)
    if "got_blue_pearl" in Driftwood.database:
        Driftwood.script.call("stdlib/viewport.py", "end_rumble")
        Driftwood.script.call("stdlib/viewport.py", "rumble", 10, 3, None)

    h = Driftwood.widget.container(x=-1, y=-1, width=80, height=80)
    Driftwood.widget.text("Test Text", "pf_arma_five.ttf", 16, parent=h,
                          x=-1, y=-1, width=-1, height=-1, color="0000FFFF", active=True)
