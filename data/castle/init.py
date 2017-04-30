entities = Driftwood.script["Entities/__init__.py"]

Driftwood.script.register("on_focus", entities.insert_entities_from_tiled)
Driftwood.script.register("on_focus", entities.insert_entities_from_tiled)
Driftwood.script.unregister("on_focus", entities.insert_entities_from_tiled)


def init():
    """Called on engine start.
    """
    # Set the logical resolution of the window.
    Driftwood.window.resolution(80, 80)

    # Play placeholder music.
    Driftwood.audio.play_music("Music/42_Rise_of_the_Ancients.oga", loop=-1)

    # Load the area.
    Driftwood.area.focus("Areas/mainroom.json")
