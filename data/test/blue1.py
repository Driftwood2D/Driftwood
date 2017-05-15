def setup():
    a = Driftwood.light.insert("lightmap_vertical1.png", 2, 2, 80, 50, 160, "000000FF", blend=True)
    b = Driftwood.light.insert("lightmap_vertical1.png", 2, 158, 80, 50, 160, "000000FF", blend=True)

    # Prepare earthquake.
    if "got_blue_pearl" not in Driftwood.database:
        Driftwood.script["rumble.py"].regular_rumble(15, 3, 5, 10)
    else:
        Driftwood.script["rumble.py"].constant_rumble(10, 3)

    h = Driftwood.widget.insert_container(x=None, y=None, width=80, height=80)
    Driftwood.widget.insert_text("Test Text", "pf_arma_five.ttf", 16, parent=h,
                          x=None, y=None, width=None, height=None, color="0000FFFF", active=True)
