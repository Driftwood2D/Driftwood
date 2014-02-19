# Load our logo and put it on the screen.
# Then wait two seconds and load the testing map.
# All Driftwood scripts are aware of the "Driftwood" instance.


def init():
	image = Driftwood.resource.request_image("basedata/pariahsoft_logo.png")

	Driftwood.window.frame(image)

	Driftwood.tick.register(init_area, 2000, True)


def init_area():
	Driftwood.area.focus("testmap.json")
	Driftwood.entity.insert("player.json", 0, 16, 32)

