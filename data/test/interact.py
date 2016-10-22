def play_blip():
    Driftwood.audio.play_sfx("Blip_Select.oga")
    w = Driftwood.widget.container("dialogbox.png", None, 10, 80, 100, 40)
    Driftwood.widget.text("This is a test widget.", "pf_arma_five.ttf", 8, w, 6, 4)
    Driftwood.widget.text("5pt seems to be the", "pf_arma_five.ttf", 8, w, 6, 10)
    Driftwood.widget.text("smallest legible.", "pf_arma_five.ttf", 8, w, 6, 16)
