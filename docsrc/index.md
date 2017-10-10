# Driftwood 2D - Alpha-0.0.10

* Copyright (c) 2014-2017 Michael D. Reiley and Paul Merrill
* Released under the MIT license.

The Driftwood 2D Tiling Game Engine and Development Suite is a game engine and related set of tools designed for the purpose of allowing a novice to develop a fully featured tile-based 2D game. Driftwood 2D is currently undergoing heavy alpha-stage development and should not be considered stable. API changes will occur frequently at this stage. However, it is currently suitable for making very simple exploration-style games.

Driftwood 2D is a spiritual successor to [Tsunagari](https://github.com/pariahsoft/Tsunagari), an engine in C++ with similar goals, which ran into irreconcilable design flaws and spaghettified to death. Tsunagari was abandoned soon after the creation of this engine.

The engine loads a world package made of images, sounds, maps, descriptive files, and scripts, and then passes itself to the scripts as an interface to its internal API. From there, the scripts in the world package interact with and control the engine to perform its functions, resulting in a playable game. All public functions in the engine are accessible through the scripts. Maps are designed in Tiled and saved in JSON format, and the engine config file and entity descriptor files are also written in JSON.

## Features

* Infinite graphical and walkable layers
* Resource caching
* Virtual filesystem for game data and patches, supporting zip files
* Tile and sprite animations
* Sound effects and music
* Configurable input handling
* Timed callbacks
* Lightmaps
* Graphical occlusion
* Lazy map loading
* Rudimentary database for saving data between plays
* Simple widgets with TTF font support
* Powerful entity and widget description in JSON with Jinja2
* Fully scriptable in Python 3
* Developer console accessible during runtime

...and more on the way!

## Requirements

* SDL2
* SDL2_image
* SDL2_mixer
* SDL2_ttf
* Python >= 3.5.0
* Python jsonschema (https://pypi.python.org/pypi/jsonschema)
* Python PySDL2 (https://pypi.python.org/pypi/PySDL2/)
* Python ubjson (https://pypi.python.org/pypi/py-ubjson)
* Python Jinja2 (http://jinja.pocoo.org/)

