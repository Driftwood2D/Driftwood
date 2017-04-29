Driftwood 2D provides a virtual filesystem for requesting resources, by reading items' locations from its path and combining them. The last location on the path has the highest precedence. If a file occurs later in the path with the name of a file that already exists in the virtual filesystem, the file from the earlier path is replaced. This allows patches to be overlaid onto a game world at any time by dropping them in the data folder and adding them to the end of the path.

Let's look over how paths are handled by the engine, and how to set them.

[TOC]

## Data Root and Pathnames
Driftwood 2D will look for packages in its path using the configured data root as its root directory. All pathnames (path locations) are relative to the data root, which is relative to the directory from which the engine is run.

The "root" setting in the "path" section of the configuration file determines the data root. Alternatively, the "--root" command line option may be used to define the data root.

Driftwood 2D itself is always the first (lowest priority) item in the path, and is not relative to the data root.

## Packages
A package is simply a directory or zip file that contains game data. These are placed in the data root directory so that they can be added to the path. Files in packages later in the path will replace files of the same name earlier in the path, inclusive of the paths' directory structures.

## Setting the Path

The path can be set in the configuration file or in the command line.

In the configuration file, the path is defined by the "path" setting in the "path" section. The setting is a comma separated list of strings containing package paths relative to the data root, enclosed in square brackets.

ex.
```
  "path": {
    "root": "data/",
    "path": [
      "first/",
      "second/",
      "third.zip",
      "extra/fourth/"
    ]
```

If set from the command line using the "--path" option, the path is a list of strings separated by commas and no spaces, with no square brackets.

ex.
<pre>
$ bin/driftwood --path first/,second/,third.zip,extra/fourth/
</pre>

The path can also be modified during runtime. This is covered later in the [API Reference](../API_Reference).
