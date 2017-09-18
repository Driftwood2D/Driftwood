def enter():
    if "got_blue_pearl" in Driftwood.database:
        Driftwood.area.tilemap.layers[2].tile(5, 3).nowalk = None
        Driftwood.area.tilemap.layers[1].tile(5, 3).setgid(0)
    else:
        Driftwood.vars["blue_pearl_light"] = Driftwood.light.insert("lightmap_circle1.png", 1, 88, 56, 40, 40,
                                                                    "FFFFFF44", blend=False)
