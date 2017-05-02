When starting up, one of the first things the Driftwood 2D engine does is read the configuration file. This file is written in JSON and contains the engine's default settings. In order to change these settings, you will have to edit this file. However, some settings may be changed temporarily at runtime using command line options. Command line options are discussed in the next section, [Command Line Options](Command_Line_Options).

[JSON](http://www.json.org/) is a simple language for describing sets of data. You won't need to know very much about it here, since the file is already mostly written for you.

[TOC]

## Structure of the Configuration File

The engine will not make assumptions about configuration; all options must be present or it will not run.

Here is the configuration file that comes with this version of the engine:

```
{
  "database": {
    "root": "db/",
    "name": "test.db"
  },
  "cache": {
    "ttl": 300
  },
  "input": {
    "keybindings": {
      "up": "SDLK_UP",
      "down": "SDLK_DOWN",
      "left": "SDLK_LEFT",
      "right": "SDLK_RIGHT",
      "interact": "SDLK_SPACE",
      "console": "SDLK_BACKQUOTE"
    },
    "debug": true
  },
  "audio": {
    "support": ["ogg"],
    "frequency": 22050,
    "chunksize": 4096,
    "music_volume": 128,
    "sfx_volume": 128
  },
  "log": {
    "verbose": true,
    "halt": true,
    "file": "driftwood.log",
    "suppress": [
      ["Tick"]
    ],
    "suppress_halt": [
      ["WARNING"]
    ]
  },
  "path": {
    "root": "data/",
    "path": [
      "test/"
    ]
  },
  "window": {
    "title": "Driftwood 2D",
    "width": 480,
    "height": 480,
    "fullscreen": false,
    "zoom": 4
  }
}
```

You can see that there are several sections. Let's take a look over each section and the settings it contains.

## database

The "database" section contains settings related to the database. The database is where variables are stored between engine runs; think of it as a save file. The database will be explained more in depth in the [Database](Database) section later in this chapter.

### root

The value of "root" is a string. It contains the relative (to the top level engine directory) path to the folder where the database is stored. Normally this is set to "db", but it doesn't really matter what you set it to as long as the folder exists.

### name

The value of "name" is a string. It contains the filename of the database that will be used when running the engine. The file is looked for in the directory set in the "root" setting. Each database is like a save file, so you would change this if you wanted to start over or play a different game, or load a "save" from earlier.

## cache

The "cache" section contains settings related to resource caching. When a resource is requested by the engine, it will be kept in memory in case it is needed again for a specified amount of time.

### ttl

The value of "ttl" is a number of seconds. This is the "time to live" for the cache -- the amount of time that a resource is held in memory after the most recent time it was used before dropping out of the cache. Decreasing this number will lower RAM usage, but may also increase load times if your computer has very slow storage. 300 (or 5 minutes) is generally a sensible value.

## input

The "input" section contains input handling settings. Keybindings and debug mode are set in this section.

### keybindings

This subsection contains the names of several input actions, and each of them contains a string value which references an [SDL Keycode](https://wiki.libsdl.org/SDL_Keycode).

* "up": Move up.
* "down": Move down.
* "left": Move left.
* "right": Move right.
* "interact": Interact with an object.
* "console": Drop to debug console if enabled.

### debug

The value of debug is a boolean. If true, pressing tilde (or your configured key) will drop to a debug console which can be used to enter event scripting code while the engine is running. Otherwise the feature is disabled.

## audio

The "audio" section contains sound and music settings. Some of these are unlikely to need modification. Volumes are set in this section.

### support

The value of "support" is a comma-separated list of strings, denoting which kinds of audio files to support. Valid options are "ogg", "mp3", and/or "flac".

### frequency

The value of "frequency" is the sampling frequency at which the audio subsystem will run. It is unlikely you will ever need to change this unless you have a very weak sound card or are some kind of audiophile.

### chunksize

The value of "chunksize" is the chunk size of the audio subsystem. This should be a power of two. It's unlikely, but tweak this number if you encounter audio stuttering.

### music_volume

The value of "music_volume" is the numeric volume at which music is played by default. It is a number between 0 and 128, 128 being highest and 0 being off.

### sfx_volume

The value of "sfx_volume" is the numeric volume at which sound effects are played by default. It is a number between 0 and 128, 128 being highest and 0 being off.

## log

The "log" section contains settings for the engine log, which outputs to the console (if run in the console.) The settings here control what sorts of information to output, and can also silence specified messages and errors. The engine log is expanded upon in the [Engine Log](Engine_Log) section later in this chapter.

### verbose

The value of "verbose" is a boolean (true or false.) If this is set to false, the log will not output messages that are not warnings or errors. If true, all messages will be output.

### halt

The value of "halt" is a boolean (true or false.) If this is set to false, the engine will not stop when encountering warnings or errors. Otherwise it will.

### file
The value of "file" is a string. It contains the relative (to the working directory) path to a file to which log messages should be written, in addition to being written to the console.

### suppress

The value of suppress is a comma separated list of lists of strings. Each item in the outer list is a suppression rule, and those rules are lists where each item in the list is a successive item in the log chain to be matched. Items in a log chain are matched to the rules chain until the end of the rules chain. If all items match, the message is not outputted. You can see that \["Tick"\] is suppressed by default; if this were not the case, the log would be flooded with callbacks, which is sometimes desirable for debugging purposes. Log chains and suppression rules are discussed in the [Engine Log](Engine_Log) section later in this chapter.

### suppress_halt

The "suppress_halt" option is just like "suppress", except that instead of preventing output, it prevents halting. If a suppress_halt rule matches a message, that message will not cause the engine to stop running even if the "halt" setting is true. You can see that \["WARNING"\] is suppressed by default; this prevents the engine from stopping on warnings. Again, these rules are discussed in the [Engine Log](Engine_Log) section later in this chapter.

## path

The "path" section contains settings for the virtual filesystem. Settings here tell the engine where to look for data. The virtual filesystem is discussed in-depth in the [Data Path and Patching](Data_Path_and_Patching) section later in this chapter.

### root

The value of "root" is a string. It contains the relative path (from the top directory) to the root of the virtual filesystem. This is the directory where the engine will look for world packages and patches -- game data. The [Data Path and Patching](Data_Path_and_Patching) section later in this chapter discusses the virtual filesystem.

### path

The value of "path" (the subsection, not the section) is a comma-separated list of paths to packages, relative to the "root" directory. These packages are directories or zip files, and they are loaded on top of each other into the virtual filesystem in the order they are listed, replacing conflicting files from the ones preceding. This allows hotpatching. The "path" list must contain, at the very least, the relative path to the world package you are trying to load. See the [Data Path and Patching](Data_Path_and_Patching) section later in this chapter for more information.

## window

The "window" section contains settings relating to the game window and graphics. You might also call these the video settings.

### title

The value of "title" is a string. It contains the title that will show on the game window at first when the engine starts.

### width

The value of "width" is the width in pixels of the game window, and also the maximum width of the view in in-game pixels. The actual width may be stretched in fullscreen mode.

### height

The value of "height" is the height in pixels of the game window, and also the maximum height of the view in in-game pixels. The actual height may be stretched in fullscreen mode.

### fullscreen

The value of "fullscreen" is a boolean (true or false.) If this setting is true, the engine is run in fullscreen. Otherwise it is run in a window.

### zoom

The value of "zoom" is the number of times to multiply the width of a pixel in-game. This can give a retro look. The view will actually zoom in without changing the width or height in real pixels, so if you zoom too far there won't be much on screen at a time.

### maxfps

The value of "maxfps" is the maximum frames per second the engine will display at. It also determines how many ticks the engine can perform per second. Each tick is a cycle of the engine in which things can happen. A value of 0 means this value will be determined automatically based on your hardware.
