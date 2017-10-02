At this time, we are unaware of any completed, published projects using the Driftwood 2D engine. Therefore, we will assume that you have downloaded a release from GitHub, and that you are reading the manual for the release version you downloaded.

[TOC]


## Requirements

Before we start, you should make sure you have the following software installed. Otherwise, the engine will not work. If you have questions about any of these third-party software requirements, please consult their official documentation as their installation is outside the scope of this manual.

* [SDL2](https://www.libsdl.org/)
* [SDL2_image](https://www.libsdl.org/projects/SDL_image/)
* [SDL2_mixer](https://www.libsdl.org/projects/SDL_mixer/)
* [SDL2_ttf](https://www.libsdl.org/projects/SDL_ttf/)
* [Python >= 3.5.0](https://www.python.org/) (Any version 3.5.0 or greater will work.)
* [Python jsonschema](https://pypi.python.org/pypi/jsonschema)
* [Python PySDL2](https://pypi.python.org/pypi/PySDL2/)
* [Python ubjson](https://pypi.python.org/pypi/py-ubjson)
* [Python Jinja2](http://jinja.pocoo.org/)


## Directory Structure

Once you unpack your release, the top level Driftwood directory should contain the following files and subdirectories:

* data/
* docsrc/
* src/
* tools/
* CREDITS.md
* LICENSE
* Makefile
* README.md
* config.json
* driftwood.bat 

Let's take a brief look at each of these items.

### data/

By default, this is where Driftwood 2D looks for game data, in the form of world packages and patches. You will learn more about this in the [Data Path and Patching](Data_Path_and_Patching) section later in this chapter.

### docsrc/

This directory contains the source code for this documentation, which can be compiled using [Daux.io](https://daux.io/). This is covered in the later chapter [Tools and Documentation](../Tools_and_Documentation).

### src/

This directory contains the source code for the Driftwood 2D engine. You may compile the source code into a single convenient file or run it as is. This will be covered later in this section.

### tools/

This directory contains the source code for additional tools that may be useful in working with Driftwood 2D. These tools are covered in the later chapter [Tools and Documentation](../Tools_and_Documentation).

### CREDITS.md

These are the credits for Driftwood 2D, as well as all of the third party software and data the engine uses directly, written in Markdown. On Windows, you may safely read this file by changing its file extension to txt.

### LICENSE

This is the end user license agreement for the Driftwood 2D engine. The gist is that you can do whatever you want as long as you attribute us in your project as the license describes. On Windows, change the file extension to txt in order to open this file.

### Makefile

This is the GNU Makefile for Driftwood 2D. It can be used to automatically compile the engine and the documentation, and to clean up afterwards. This is covered later in this section, and is not applicable to Windows users.

### README.md

This is the README file which gives some basic information about Driftwood 2D, written in Markdown. Again, change the file extension to txt to view it on Windows.

### config.json

This is the Driftwood 2D configuration file, which contains default settings for running the engine. You will learn how to edit this file in the [Configuration File](Configuration_File) section later in this chapter.

### driftwood.bat

This is a Windows batch file, provided for your convenience. Opening this file on Windows should automatically start the Driftwood 2D engine.


## Compiling (optional)

This step is optional, and not currently applicable to Windows users. Compiling is unnecessary, because Python software can be run from the source code. However, compiling the engine will combine all of the source files into a single convenient file and may be desirable.

To compile, you should be on a Linux, Mac OSX, or Unix system, and make sure you have installed GNU Make and Zip. In the top level Driftwood directory, in the terminal, simply run the command "make". A directory called "bin/" will be created, and the compiled engine will be placed at "bin/driftwood".

In the process of "Making", each source file in the "src/" directory is compiled into a faster and more compact Python bytecode file, and then the directory structure is placed into a zip archive with a shebang at the beginning of the file to invoke Python3. Because Python can run code out of a zip archive, the "bin/driftwood" file can be invoked from the command line as an executable.

However, this file may only be safely used on the system it was compiled on. If you would like to compile a redistributable binary that you can package with your project, you should instead run "make release". This is the same as running "make", except that the source files will not be compiled into bytecode before being packaged, and the resulting file will be placed into a new "release/" subdirectory.


## Starting the Engine

If you compiled the engine, simply run "bin/driftwood" from the top level Driftwood directory to start it up. If you compiled a release version, run "release/driftwood" instead.

If you are using Windows, run the "driftwood.bat" batch file in the top level directory by double clicking it or executing it from the command line.

If you would like to run from source on a non-Windows platform, simply run "python3 src/" from the command line.

Note that the engine will not run if it cannot find a world package (game data). See the next subsection.

## Choosing a Game

If you need to tell Driftwood 2D to read game data from a particular world package and it is not already configured to do so, see the "path" settings in the [Configuration File](Configuration_File) section later in this chapter. You may also choose a game using [Command Line Options](Command_Line_Options). The [Data Path and Patching](Data_Path_and_Patching) section provides even more information on this topic. The testing world package bundled with the Driftwood 2D source is the "data/test/" directory. World packages can be directories or zip files.

