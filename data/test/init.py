def init():
	"""Called on engine start.
	"""
	# Load the logo.
	image = Driftwood.resource.request_image("basedata/pariahsoft_logo.png")

	# Display the logo.
	Driftwood.window.frame(image)

	# Wait 2 seconds and then load the area.
	Driftwood.tick.register(init_area, delay=2.0, once=True)


def init_area(millis):
	# Load the area.
	Driftwood.area.focus("testmap.json")

	# Insert the player entity.
	player = Driftwood.entity.insert("player.json", layer=0, x=16*1, y=16*2)

