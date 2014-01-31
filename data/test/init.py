# Load an image file and put it on the screen.
# All Driftwood scripts are aware of the "Driftwood" instance.

def init():
	imagedata = Driftwood.resource["basedata/pariahsoft_logo.png"]
	image = Driftwood.filetype.ImageFile(imagedata)

	Driftwood.window.frame(image)

