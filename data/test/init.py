# Load an image file and put it on the screen.
# Then wait two seconds and load the testing map.
# All Driftwood scripts are aware of the "Driftwood" instance.


def init():
	imagedata = Driftwood.resource.request("basedata/pariahsoft_logo.png", True)
	image = Driftwood.filetype.ImageFile(imagedata)

	Driftwood.window.frame(image)

	Driftwood.tick.register(init_area, 2000, True)


def init_area():
	Driftwood.area.focus("testmap.json")

