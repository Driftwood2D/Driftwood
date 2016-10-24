def check_for_rumble():
    if "got_blue_pearl" in Driftwood.database and "end_rumble" in Driftwood.vars and Driftwood.vars["end_rumble"]:
        Driftwood.vars["end_rumble"]()
        Driftwood.vars["end_rumble"] = Driftwood.script.call("libs/stdlib/viewport.py", "rumble", 12, 3, None)
