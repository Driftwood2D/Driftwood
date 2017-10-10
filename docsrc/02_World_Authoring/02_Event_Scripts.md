Event Scripts are scripts written in Python 3 which utilize the Driftwood 2D scripting API to command the engine. Most of what you need to know about Event Scripts is written in the [Event Scripting](../Event_Scripting) chapter, but a summary is given here.

[TOC]

## Purpose

## Init Script

After the engine starts up and loads the World Packages in its data path, the first thing it does is look for "init.py", the Init Script. This is a special Event Script which performs setup for the game. Without the presence of this script in the data path, the engine will only produce a blank window. Normally, the Init Script is a good place to set window resolution, load a first area, and insert the player entity. It must be present in the top level directory of any World Package in the path.
