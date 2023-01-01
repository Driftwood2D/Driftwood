################################
# Driftwood 2D Game Dev. Suite #
# __schema__.py                #
# Copyright 2014-2017          #
# Sei Satzparad & Paul Merrill #
################################

# **********
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# **********

# JSON Schemas
# These are the schema files for validating various categories of json-based engine data files.
# They are stuck here in variables because jsonschema's path-finding doesn't play nice with PyInstaller on Windows.

import json

# Schema for the engine config file.
_S_CONFIG = """
{
  "type": "object",
  "properties": {
    "database": {
      "type": "object",
      "properties": {
        "root": {
          "type": "string"
        },
        "name": {
          "type": "string"
        }
      },
      "required": [
        "root",
        "name"
      ]
    },
    "cache": {
      "type": "object",
      "properties": {
        "ttl": {
          "type": "number",
          "minimum": 1
        }
      },
      "required": [
        "ttl"
      ]
    },
    "input": {
      "type": "object",
      "properties": {
        "keybinds": {
          "type": "object",
          "additionalProperties": {
            "type": "string"
          }
        },
        "debug": {
          "type": "boolean"
        }
      },
      "required": [
        "keybinds",
        "debug"
      ]
    },
    "audio": {
      "type": "object",
      "properties": {
        "frequency": {
          "type": "integer",
          "minimum": 1
        },
        "music_volume": {
          "type": "integer",
          "minimum": 0,
          "maximum": 128
        },
        "sfx_volume": {
          "type": "integer",
          "minimum": 0,
          "maximum": 128
        }
      },
      "required": [
        "frequency",
        "music_volume",
        "sfx_volume"
      ]
    },
    "log": {
      "type": "object",
      "properties": {
        "verbose": {
          "type": "boolean"
        },
        "halt": {
          "type": "boolean"
        },
        "file": {
          "type": "string"
        },
        "suppress": {
          "type": "array",
          "items": {
            "type": "array",
            "items": {
              "type": "string"
            }
          }
        },
        "suppress_halt": {
          "type": "array",
          "items": {
            "type": "array",
            "items": {
              "type": "string"
            }
          }
        }
      },
      "required": [
        "verbose",
        "halt",
        "file",
        "suppress",
        "suppress_halt"
      ]
    },
    "path": {
      "type": "object",
      "properties": {
        "root": {
          "type": "string"
        },
        "path": {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      },
      "required": [
        "root",
        "path"
      ]
    },
    "window": {
      "type": "object",
      "properties": {
        "title": {
          "type": "string"
        },
        "width": {
          "type": "integer",
          "minimum": 1
        },
        "height": {
          "type": "integer",
          "minimum": 1
        },
        "fullscreen": {
          "type": "boolean"
        },
        "zoom": {
          "type": "integer",
          "minimum": 1
        },
    "maxfps": {
          "type": "integer",
          "minimum": 0
    }
      },
      "required": [
        "title",
        "width",
        "height",
        "fullscreen",
        "zoom",
    "maxfps"
      ]
    }
  },
  "required": [
    "database",
    "cache",
    "input",
    "audio",
    "log",
    "path",
    "window"
  ]
}
"""

# Schema for entity descriptors.
_S_ENTITY = """
{
  "type": "object",
  "properties": {
    "init": {
      "type": "object",
      "properties": {
        "mode": {
          "type": "string",
          "enum": [
            "tile",
            "pixel",
            "rogue"
          ]
        },
        "collision": {
          "type": "array",
          "items": {
            "type": "string",
            "enum": [
              "all",
              "entity",
              "tile",
              "next",
              "prev",
              "here"
            ]
          }
        },
        "travel": {
          "type": "boolean"
        },
        "speed": {
          "type": "integer",
          "minimum": 0
        },
        "image": {
          "type": "string"
        },
        "width": {
          "type": "integer",
          "minimum": 1
        },
        "height": {
          "type": "integer",
          "minimum": 1
        },
        "members": {
          "type": "array",
          "items": {
            "type": ["integer", "array"],
            "minimum": 0
          }
        },
        "afps": {
          "type": "integer",
          "minimum": 0
        },
        "properties": {
          "type": "object"
        },
        "on_insert": {
          "type": "string",
          "pattern": "^(|.+,.+)$"
        },
        "on_kill": {
          "type": "string",
          "pattern": "^(|.+,.+)$"
        },
        "resting_stance": {
          "type": "string"
        }
      },
      "required": [
        "mode",
        "collision",
        "travel",
        "speed",
        "image",
        "width",
        "height",
        "members",
        "afps",
        "properties",
        "on_insert",
        "on_kill",
        "resting_stance"
      ]
    }
  },
  "required": [
    "init"
  ],
  "additionalProperties": {
    "type": "object",
    "properties": {
      "collision": {
        "type": "array",
        "items": {
          "type": "string",
          "enum": [
            "entity",
            "tile",
            "next",
            "prev",
            "here"
          ]
        }
      },
      "image": {
        "type": "string"
      },
      "speed": {
        "type": "integer",
        "minimum": 0
      },
      "members": {
        "type": "array",
        "items": {
          "type": "integer",
          "minimum": 0
        }
      },
      "afps": {
        "type": "integer",
        "minimum": 0
      },
      "properties": {
        "type": "object"
      }
    }
  }
}
"""

# Dictionary storing all schema files by name.
_SCHEMA = {"config": json.loads(_S_CONFIG), "entity": json.loads(_S_ENTITY)}
