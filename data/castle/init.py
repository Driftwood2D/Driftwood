player = Driftwood.script.module("Entities/player.py")

def init():
    """Called on engine start.
    """
    # Set the logical resolution of the window.
    Driftwood.window.resolution(80, 80)

    # Play placeholder music.
    Driftwood.audio.play_music("Music/42_Rise_of_the_Ancients.oga", loop=-1)

    # Load the area.
    Driftwood.area.focus("Areas/mainroom.json")

    player.insert_from_tiled()
