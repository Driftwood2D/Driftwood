def rumble(rate, intensity, duration):
    __end_regular_rumble()
    Driftwood.script.call("stdlib/viewport.py", "rumble", rate, intensity, duration)


def regular_rumble(rate, intensity, duration, interval):
    __end_regular_rumble()
    def rumble():
        Driftwood.script.call("stdlib/viewport.py", "rumble", rate, intensity, duration)
    Driftwood.vars["regular_rumble"] = rumble
    Driftwood.tick.register(rumble, delay=interval)


def __end_regular_rumble():
    if "regular_rumble" in Driftwood.vars:
        Driftwood.tick.unregister(Driftwood.vars["regular_rumble"])
        del Driftwood.vars["regular_rumble"]


def constant_rumble(rate, intensity):
    __end_regular_rumble()
    Driftwood.script.call("stdlib/viewport.py", "rumble", rate, intensity, None)


def end_rumble():
    __end_regular_rumble()
    Driftwood.script.call("stdlib/viewport.py", "end_rumble")
