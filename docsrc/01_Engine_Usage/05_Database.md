In many games it is necessary to save the contents of variables or other data to disk when shutting down, and then load those values back into memory when starting up again. The file where this information is saved is usually referred to as a save file.

In Driftwood 2D, we present for saving data a simple [UBJSON](https://ubjson.org/) database, which can save the contents of most common Python objects. We can also open a different database while running, allowing for things like multiple save files. This is covered in the [API Reference](API_Reference).

[TOC]

## Choosing the Database

Choosing the database to use involves setting two configuration values -- the database root and the filename.

### Database Root

The database root is the directory in which the engine looks for database files. All database paths/filenames are relative to the database root. It can be set in the configuration file with the "root" setting in the "database" section. Alternatively it can be set from the command line with the "--dbroot" option.

### Database Filename

The database filename (and path) is relative to the database root. They usually have a ".db" file extension, but this is arbitrary. The filename can be set in the configuration file with the "name" setting in the "database" section. Alternatively it can be set from the command line with the "--dbroot" option.

## Using the Database

Values can be added to and removed from the database, as well as read out of it. Using the database during runtime from a script is covered in the [API Reference](API_Reference). The database can also be edited with the "dbedit.py" command line tool packaged with the engine source. The use of this tool is described in the later [Tools and Documentation](Tools_and_Documentation) chapter.
