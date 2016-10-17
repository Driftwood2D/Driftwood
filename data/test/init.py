def init():
    """Called on engine start.
    """
    # Load the logo.
    image = Driftwood.resource.request_image("basedata/pariahsoft_logo.png")

    # Display the logo.
    Driftwood.window.frame(image)

    # Wait 2 seconds and then load the area.
    Driftwood.tick.register(init_area, delay=2.0, once=True)


def init_area(millis):
    # Load the area.
    Driftwood.area.focus("testmap.json")

    Driftwood.audio.play_sfx("Blip_Select.oga")
    Driftwood.audio.play_music("A_Travellers_Tale.oga", loop=-1)

    # Insert the player entity.
    player = Driftwood.entity.insert("player.json", layer=1, x=16*1, y=16*2)

    # Prepare earthquake.
    Driftwood.tick.register(rumble, delay=10.0, once=True)

def rumble():
    Driftwood.script.call("libs/stdlib/viewport.py", "rumble", 15, 3, 5)
