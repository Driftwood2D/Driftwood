def test():
    #w = Driftwood.widget.insert_container(imagefile="textbox.png", x=None, y=None, width=144, height=48)
    #Driftwood.widget.insert_text("This is a text box.", "pf_arma_five.ttf", 8, parent=w, x=6, y=4,
    #                             width=None, height=None, color="000000FF", active=True)

    Driftwood.script["stdlib/widget.py"].load("widgets/textbox1.json",
                                              {"contents": ["This is a textbox", "with three", "lines."]})
