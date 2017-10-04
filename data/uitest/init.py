# Driftwood 2D UI Testing Meta-World


def init():
    """Called on engine start.
    """
    # Set the logical resolution of the window.
    Driftwood.window.resize(160, 160)

    # Load the area.
    Driftwood.area.focus("grid.json")

    # Run a UI test.
    Driftwood.script["test01.py"].test()

