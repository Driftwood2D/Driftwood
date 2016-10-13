def setup():
    # Insert the wizard entity on each focus.
    Driftwood.entity.insert("wizard.json", layer=0, x=16*5, y=16*3)

    Driftwood.audio.play_sfx("Blip_Select.oga")
    Driftwood.audio.play_music("A_Travellers_Tale.oga", loop=-1)
