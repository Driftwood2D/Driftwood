def init():
    """Called on engine start.
    """
    # Set the logical resolution of the window.
    Driftwood.window.resize(160, 160)

    # Initialize special effects.
    viewport = Driftwood.script["Stageshow/viewport.py"].ViewportFX()
    lighting = Driftwood.script["Stageshow/lighting.py"].LightingFX()
    _["viewport"] = viewport
    _["lighting"] = lighting

    # Load the area.
    Driftwood.area.focus("area1.json")

    # Insert the player entity.
    player = Driftwood.entity.insert("player.json", layer=1, x=4, y=8)
