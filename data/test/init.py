def init():
	"""Called on engine start.
	"""
	# Load the logo.
	image = Driftwood.resource.request_image("basedata/pariahsoft_logo.png")

	# Display the logo.
	Driftwood.window.frame(image)

	# Wait 2 seconds and then load the area.
	Driftwood.tick.register(init_area, 2000, True)


def init_area():
	# Load the area.
	Driftwood.area.focus("testmap.json")
	
	# Insert an entity and make it the player.
	Driftwood.entity.insert("player.json", 0, 16, 32)
	Driftwood.entity.player = Driftwood.entity.entities[-1]
	
	# Register key bindings.
	Driftwood.input.register(Driftwood.keycode.SDLK_UP, move_up)
	Driftwood.input.register(Driftwood.keycode.SDLK_DOWN, move_down)
	Driftwood.input.register(Driftwood.keycode.SDLK_LEFT, move_left)
	Driftwood.input.register(Driftwood.keycode.SDLK_RIGHT, move_right)

def move_up():
	Driftwood.entity.player.move(0, -1)

def move_down():
	Driftwood.entity.player.move(0, 1)

def move_left():
	Driftwood.entity.player.move(-1, 0)

def move_right():
	Driftwood.entity.player.move(1, 0)
