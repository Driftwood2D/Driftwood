####################################
# Driftwood 2D Game Dev. Suite     #
# light.py                         #
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


class Light:
    """This class represents a light.

    Attributes:
        Same as __init__ args.
    """

    def __init__(self, manager, lid, lightmap, layer, x, y, w, h, intensity, color, soft, entity):
        """Light class initializer.

        Args:
            manager: Link back to the parent LightManager instance.

            lid: The Light ID of this light.
            lightmap: ImageFile of the lightmap.
            layer: Layer to draw on.
            x: x-coordinate in pixels.
            y: y-coordinate in pixels.
            w: Width of the light.
            h: Height of the light.
            intensity: Brightness of the light, in percentage.
            color: Hexadeximal color value of the light.
            soft: Whether to soften on zoom. Otherwise pixelates.
            entity: If set, eid of entity to track the light to. Disabled if None.
        """
        self.manager = manager

        self.lid = lid
        self.lightmap = lightmap
        self.layer = layer
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.intensity = intensity
        self.color = color
        self.soft = soft
        self.entity = entity
