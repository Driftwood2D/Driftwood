# Driftwood 2D

* Copyright (c) 2014-2017 Sei Satzparad and Paul Merrill
* Released under the MIT license.

![Driftwood 2D with Tiled and Console](https://i.imgur.com/XdbQO1P.png)

The Driftwood 2D Tiling Game Engine and Development Suite is a game engine and related set of tools designed for the purpose of allowing a novice to develop a fully featured tile-based 2D game. Driftwood 2D is currently undergoing heavy alpha-stage development and should not be considered stable. API changes will occur frequently at this stage. However, it is currently suitable for making very simple exploration-style games.

The engine loads a world package made of images, sounds, maps, descriptive files, and scripts, and then passes itself to the scripts as an interface to its internal API. From there, the scripts in the world package interact with and control the engine to perform its functions, resulting in a playable game. All public functions in the engine are accessible through the scripts. Maps are designed in Tiled and saved in JSON format, and the engine config file and entity descriptor files are also written in JSON.

Current features include:
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
* Python >= 3.6.0
* Python jsonschema <https://pypi.python.org/pypi/jsonschema>
* Python PySDL2 <https://pypi.python.org/pypi/PySDL2/>
* Python ubjson <https://pypi.python.org/pypi/py-ubjson>
* Python Jinja2 <https://jinja.palletsprojects.com/>
* Python PyGame <https://www.pygame.org/>


## Running

On Linux releases prior to Alpha-0.0.11, the source release contains everything necessary. Simply run ```make``` in the top directory, and if all of your prerequisites are installed and the make completes sucessfully, you can run ```bin/driftwood``` from the top directory to start the engine.

On Linux releases Alpha-0.0.11 and afterwards, the project has been split into subdirectories, which are not included in the source release zip. Instead, you can download the Linux binary release, and just run ```./driftwood``` in the top directory. For the source release, you must run ```git submodule init``` and ```git submodule update``` in the top directory, and then you can run ```make``` and ```bin/driftwood``` like before.

On Windows, simply download the Windows binary release and run ```Driftwood.exe``` in the top directory, either through the command line or by double clicking. The Windows binary release ships with all of its prerequisites, so it should just work. Alternatively you can download the source release and run the ```Driftwood.bat``` batch file, assuming you have installed all of the prerequisites manually.

On all releases, running the driftwood executable with the ```--help``` option will present a list of command line options. You can select a game from the data directory by running with ```--path game-directory-name```.

A Linux binary release is made from source by running ```make release```, and is placed in the newly created ```release/``` directory. Making Windows binaries is not currently documented, but we make them using using [pyinstaller](http://www.pyinstaller.org/).

For development testing, you can run ```python3 src``` from the top directory to run the engine from source without compiling.
