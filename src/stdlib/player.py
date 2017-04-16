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


def set_player(ent):
    """Set the entity "ent" as the player character.
    """
    Driftwood.entity.player = ent
    return True


def set_default_walk_keybinds():
    """Setup the default walk keybinds.
    """
    if not Driftwood.entity.player:
        return False
    
    Driftwood.input.register("up", __default_keybind_move_up)
    Driftwood.input.register("down", __default_keybind_move_down)
    Driftwood.input.register("left", __default_keybind_move_left)
    Driftwood.input.register("right", __default_keybind_move_right)
    Driftwood.input.register("interact", __default_keybind_interact)
    Driftwood.input.register("face", __default_keybind_face)
    
    return True


def __default_keybind_move_up(keyevent):
    player = Driftwood.entity.player
    if keyevent == Driftwood.input.ONDOWN:
        player._walk_stop()
        player.walk(0, -1, dont_stop=True, stance="walk_up", end_stance="face_up")
    elif keyevent == Driftwood.input.ONREPEAT:
        player.walk(0, -1, dont_stop=True, stance="walk_up", end_stance="face_up")
    elif keyevent == Driftwood.input.ONUP:
        player._walk_stop()


def __default_keybind_move_down(keyevent):
    player = Driftwood.entity.player
    if keyevent == Driftwood.input.ONDOWN:
        player._walk_stop()
        player.walk(0, 1, dont_stop=True, stance="walk_down", end_stance="face_down")
    elif keyevent == Driftwood.input.ONREPEAT:
        player.walk(0, 1, dont_stop=True, stance="walk_down", end_stance="face_down")
    elif keyevent == Driftwood.input.ONUP:
        player._walk_stop()


def __default_keybind_move_left(keyevent):
    player = Driftwood.entity.player
    if keyevent == Driftwood.input.ONDOWN:
        player._walk_stop()
        player.walk(-1, 0, dont_stop=True, stance="walk_left", end_stance="face_left")
    if keyevent == Driftwood.input.ONREPEAT:
        player.walk(-1, 0, dont_stop=True, stance="walk_left", end_stance="face_left")
    elif keyevent == Driftwood.input.ONUP:
        player._walk_stop()


def __default_keybind_move_right(keyevent):
    player = Driftwood.entity.player
    if keyevent == Driftwood.input.ONDOWN:
        player._walk_stop()
        player.walk(1, 0, dont_stop=True, stance="walk_right", end_stance="face_right")
    if keyevent == Driftwood.input.ONREPEAT:
        player.walk(1, 0, dont_stop=True, stance="walk_right", end_stance="face_right")
    elif keyevent == Driftwood.input.ONUP:
        player._walk_stop()


def __default_keybind_interact(keyevent):
    player = Driftwood.entity.player
    if keyevent == Driftwood.input.ONDOWN:
        if not player.interact():
            player.interact("under")


def __default_keybind_face(keyevent):
    player = Driftwood.entity.player
    if keyevent == Driftwood.input.ONDOWN:
        player._face_key_active = True
    elif keyevent == Driftwood.input.ONUP:
        player._face_key_active = False
