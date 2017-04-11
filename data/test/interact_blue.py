def open_door():
    # TODO: This needs to be in the stdlib.
    Driftwood.area.tilemap.layers[2].tiles[4].nowalk = None
    Driftwood.area.tilemap.layers[2].tiles[4].localgid = 27
    Driftwood.area.tilemap.layers[2].tiles[4].gid = 27
    Driftwood.area.tilemap.layers[2].tiles[4].members = [26]


def open_door2():
    Driftwood.area.tilemap.layers[2].tiles[2].nowalk = None
    Driftwood.area.tilemap.layers[2].tiles[2].localgid = 27
    Driftwood.area.tilemap.layers[2].tiles[2].gid = 27
    Driftwood.area.tilemap.layers[2].tiles[2].members = [26]


def get_pearl():
    if "got_blue_pearl" not in Driftwood.database:
        Driftwood.area.tilemap.layers[2].tiles[35].nowalk = None
        Driftwood.area.tilemap.layers[1].tiles[35].localgid = 0
        Driftwood.area.tilemap.layers[1].tiles[35].gid = 0
        Driftwood.area.tilemap.layers[1].tiles[35].members = []
        Driftwood.database.put("got_blue_pearl", "true")
        if "blue_pearl_light" in Driftwood.vars and Driftwood.vars["blue_pearl_light"]:
            Driftwood.light.kill(Driftwood.vars["blue_pearl_light"])
