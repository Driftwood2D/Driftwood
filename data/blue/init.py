def init():
    """Called on engine start.
    """
    # Set the logical resolution of the window.
    Driftwood.window.resize(120, 120)

    # Load the area.
    Driftwood.area.focus("blue1.json")

    # Play placeholder music.
    Driftwood.audio.play_music("A_Travellers_Tale.oga", loop=None)

    # Insert the player entity.
    player = Driftwood.entity.insert("player.json", layer=1, x=16*4, y=16*8)
