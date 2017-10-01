####################################
# Driftwood 2D Game Dev. Suite     #
# stdlib/player.py                 #
# Copyright 2016 Michael D. Reiley #
# & Paul Merrill                   #
####################################

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

# Driftwood STDLib Player functions.

__ = Driftwood.script["stdlib/__player.py"]


def set_player(ent):
    """Set the entity "ent" as the player character.
    """
    Driftwood.entity.player = ent
    return True


def set_four_way_walk_keybinds():
    """Setup the four-way (movement along major axes) walk keybinds.
    """
    if not Driftwood.entity.player:
        return False
    
    Driftwood.input.register("up", __.four_way_keybind_move_up)
    Driftwood.input.register("down", __.four_way_keybind_move_down)
    Driftwood.input.register("left", __.four_way_keybind_move_left)
    Driftwood.input.register("right", __.four_way_keybind_move_right)

    Driftwood.input.register("interact", __.default_keybind_interact)
    Driftwood.input.register("face", __.default_keybind_face)
    
    return True


def set_eight_way_walk_keybinds():
    """Setup the eight-way (axes + diagonals) walk keybinds.
    """
    player = Driftwood.entity.player

    if not player:
        return False

    player._move_keys_active = [0, 0, 0, 0]

    Driftwood.input.register("up", __.eight_way_keybind_move_up)
    Driftwood.input.register("down", __.eight_way_keybind_move_down)
    Driftwood.input.register("left", __.eight_way_keybind_move_left)
    Driftwood.input.register("right", __.eight_way_keybind_move_right)

    Driftwood.input.register("interact", __.default_keybind_interact)
    Driftwood.input.register("face", __.default_keybind_face)

    return True
