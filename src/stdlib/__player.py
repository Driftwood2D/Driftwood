####################################
# Driftwood 2D Game Dev. Suite     #
# stdlib/__player.py               #
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

# Driftwood STDLib Player private functions and variables.


def four_way_keybind_move_up(keyevent):
    player = Driftwood.entity.player
    if keyevent == Driftwood.input.ONDOWN:
        player._walk_stop()
        player.walk(0, -1, dont_stop=True, stance="walk_up", end_stance="face_up")
    elif keyevent == Driftwood.input.ONREPEAT:
        player.walk(0, -1, dont_stop=True, stance="walk_up", end_stance="face_up")
    elif keyevent == Driftwood.input.ONUP:
        player._walk_stop()


def four_way_keybind_move_down(keyevent):
    player = Driftwood.entity.player
    if keyevent == Driftwood.input.ONDOWN:
        player._walk_stop()
        player.walk(0, 1, dont_stop=True, stance="walk_down", end_stance="face_down")
    elif keyevent == Driftwood.input.ONREPEAT:
        player.walk(0, 1, dont_stop=True, stance="walk_down", end_stance="face_down")
    elif keyevent == Driftwood.input.ONUP:
        player._walk_stop()


def four_way_keybind_move_left(keyevent):
    player = Driftwood.entity.player
    if keyevent == Driftwood.input.ONDOWN:
        player._walk_stop()
        player.walk(-1, 0, dont_stop=True, stance="walk_left", end_stance="face_left")
    if keyevent == Driftwood.input.ONREPEAT:
        player.walk(-1, 0, dont_stop=True, stance="walk_left", end_stance="face_left")
    elif keyevent == Driftwood.input.ONUP:
        player._walk_stop()


def four_way_keybind_move_right(keyevent):
    player = Driftwood.entity.player
    if keyevent == Driftwood.input.ONDOWN:
        player._walk_stop()
        player.walk(1, 0, dont_stop=True, stance="walk_right", end_stance="face_right")
    if keyevent == Driftwood.input.ONREPEAT:
        player.walk(1, 0, dont_stop=True, stance="walk_right", end_stance="face_right")
    elif keyevent == Driftwood.input.ONUP:
        player._walk_stop()


def default_keybind_interact(keyevent):
    player = Driftwood.entity.player
    if keyevent == Driftwood.input.ONDOWN:
        if not player.interact():
            player.interact("under")


def default_keybind_face(keyevent):
    player = Driftwood.entity.player
    if keyevent == Driftwood.input.ONDOWN:
        player._face_key_active = True
    elif keyevent == Driftwood.input.ONUP:
        player._face_key_active = False


def eight_way_keybind_move_up(keyevent):
    player = Driftwood.entity.player
    if keyevent == Driftwood.input.ONDOWN:
        player._move_keys_active[0] = 1
    elif keyevent == Driftwood.input.ONUP:
        player._move_keys_active[0] = 0
    eight_way_update()


def eight_way_keybind_move_down(keyevent):
    player = Driftwood.entity.player
    if keyevent == Driftwood.input.ONDOWN:
        player._move_keys_active[1] = 1
    elif keyevent == Driftwood.input.ONUP:
        player._move_keys_active[1] = 0
    eight_way_update()


def eight_way_keybind_move_left(keyevent):
    player = Driftwood.entity.player
    if keyevent == Driftwood.input.ONDOWN:
        player._move_keys_active[2] = 1
    elif keyevent == Driftwood.input.ONUP:
        player._move_keys_active[2] = 0
    eight_way_update()


def eight_way_keybind_move_right(keyevent):
    player = Driftwood.entity.player
    if keyevent == Driftwood.input.ONDOWN:
        player._move_keys_active[3] = 1
    elif keyevent == Driftwood.input.ONUP:
        player._move_keys_active[3] = 0
    eight_way_update()


eight_way_stance = [
    ["up_left", "up", "up_right"],
    ["left", "none", "right"],
    ["down_left", "down", "down_right"],
]


def eight_way_update():
    player = Driftwood.entity.player
    up, down, left, right = player._move_keys_active

    y = down - up
    x = right - left

    base = eight_way_stance[y+1][x+1]
    stance = "walk_" + base
    end_stance = "face_" + base

    if x == 0 and y == 0:
        player._walk_stop()
    else:
        player.walk(x, y, dont_stop=True, facing=None, stance=stance, end_stance=end_stance)
