# Load an image file and put it on the screen.
# All Driftwood scripts are aware of the "Driftwood" instance.

imagedata = Driftwood.resource.request("basedata/driftwood.jpg")
image = Driftwood.filetype.ImageFile(imagedata)

Driftwood.window.frame(image.texture)

