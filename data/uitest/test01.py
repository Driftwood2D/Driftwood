def test():
    a = Driftwood.script["stdlib/widget.py"].load("widgets/textbox1.json",
                        {"contents": "This is a textbox that has had its text wrapped a whole danged awful lot."})
    b = Driftwood.script["stdlib/widget.py"].load("widgets/textbox2.json")

    print(a)
    print(b)