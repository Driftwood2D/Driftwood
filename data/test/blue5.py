def enter():
    if "got_blue_pearl" in Driftwood.database:
        Driftwood.area.tilemap.layers[2].tiles[35].nowalk = None
        Driftwood.area.tilemap.layers[1].tiles[35].localgid = 0
        Driftwood.area.tilemap.layers[1].tiles[35].gid = 0
        Driftwood.area.tilemap.layers[1].tiles[35].members = []
