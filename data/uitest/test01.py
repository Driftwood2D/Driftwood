def test():
    a = Driftwood.script["stdlib/widget.py"].load("widgets/textbox1.json", {
        "contents": "This is a textbox that has had its text wrapped a whole danged awful lot.",
        "wrap": 110
    })
    b = Driftwood.script["stdlib/widget.py"].load("widgets/textbox2.json", {
        "contents": "This text will be replaced by the vars property.",
        "line_height": "0.6"
    })

    print(a)
    print(b)
