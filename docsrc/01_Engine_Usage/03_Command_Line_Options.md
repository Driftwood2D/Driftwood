Sometimes you may want to start the Driftwood 2D engine with some particular options temporarily, without having to edit the configuration file. Driftwood accepts a number of command line options which will modify its settings for one run only.

[TOC]

## Usage

Running the engine with the "--help" option shows us what options are available:

<pre>
[myself@Linux Driftwood]$ bin/driftwood --help
usage: driftwood [-h] [--path <name,...>] [--root <root>] [--db <database>]
                 [--dbroot <root>] [--size <WxH>] [--ttl <seconds>]
                 [--maxfps <fps>] [--mvol <0-128>] [--svol <0-128>]
                 [--window | --fullscreen] [--quiet | --verbose]
                 [--halt | --continue] [--version]
                 [config]

Driftwood 2D Alpha-0.0.6

positional arguments:
  config             config file to use

optional arguments:
  -h, --help         show this help message and exit
  --path <name,...>  set path
  --root <root>      set path root
  --db <database>    set database to use
  --dbroot <root>    set database root
  --size <WxH>       set window dimensions
  --ttl <seconds>    set cache time-to-live
  --maxfps <fps>     set max fps
  --mvol <0-128>     set music volume
  --svol <0-128>     set sfx volume
  --window           run in windowed mode
  --fullscreen       run in fullscreen mode
  --quiet            run in quiet logging mode
  --verbose          run in verbose logging mode
  --halt             halt execution on errors or warnings
  --continue         continue execution despite errors or warnings
  --version          print the version string
</pre>

All options are... optional. Let's go over each of these command line options and how to use them.

## Options

See the [Configuration File](Configuration_File) section earlier in this chapter for more information about the settings changed by these options.

### config

This is the only option that is not a switch. Its value is the relative path (from the current working directory) to an alternative configuration file to load settings out of. Any further command line options will override the settings in this configuration file.

### --help

The "--help" option (also "-h") causes the above usage info to be output to the console.

### --path

The "--path" option is followed by a comma-separated list of path names to append to the virtual filesystem, starting with the world package. The [Data Path and Patching](Data_Path_and_Patching) section later in this chapter will tell you more about path names and the virtual filesystem.

### --root

The "--root" option is followed by the relative path (from the current working directory) to the folder where world packages and patches are kept. Path entries are relative to the root path set here.

### --db

The "--db" option is followed by the relative path (from the database root) to the database to be loaded.

### --dbroot

The "--dbroot" option is followed by the relative path (from the current working directory) to the folder where databases are kept.

### --size

The "--size" option is followed by the dimensions (in format WxH) of the game window, or the maximum dimensions in fullscreen.

### --ttl

The "--ttl" option is followed by the time to live of items in the cache. This is the length of time that data will remain cached in memory after the last time it was requested. A value of 0 disables the cache.

### --zoom

The "--zoom" option is followed by the zoom multiplier; the view will be zoomed in this much, causing pixelation and a retro feel.

### --maxfps

The "--maxfps" option is followed by the maximum frames per second the engine will display at.

### --mvol

The "--mvol" option is followed by the music volume, which is a number from 0 to 128, with 128 being highest and 0 disabling music.

### --svol

The "--svol" option is followed by the sound effects volume, which is a number from 0 to 128, with 128 being highest and 0 disabling sound effects.

### --window

The "--window" option takes no arguments. It causes the engine to run in a window.

### --fullscreen

The "--fullscreen" option takes no arguments. It causes the engine to run in fullscreen.

### --quiet

The "--quiet" option takes no arguments. It causes the engine to only display warning and error messages to the console.

### --verbose

The "--verbose" option takes no arguments. It causes the engine to display informational messages to the console which are not warnings or errors.

### --halt

The "--halt" option takes no arguments. It causes the engine to shut down upon encountering warnings or errors.

### --continue

The "--continue" option takes no arguments. It causes the engine to continue running despite encountering warnings or errors.

### --version

The "--version" option takes no arguments. It causes the engine to output its version string to the console and then exit.
