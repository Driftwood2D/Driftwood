def init():
    """Called on engine start.
    """
    # Load the area.
    Driftwood.area.focus("blue1.json")

    Driftwood.audio.play_music("A_Travellers_Tale.oga", loop=-1)

    # Insert the player entity.
    player = Driftwood.entity.insert("player.json", layer=1, x=16*4, y=16*8)

    # Prepare earthquake.
    Driftwood.tick.register(rumble, delay=10.0)
    Driftwood.vars["init_rumble_tick_callback"] = rumble

def rumble():
    Driftwood.script.call("libs/stdlib/viewport.py", "rumble", 15, 3, 5)
