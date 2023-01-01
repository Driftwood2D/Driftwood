################################
# Driftwood 2D Game Dev. Suite #
# light.py                     #
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

from typing import Tuple

import entity
import filetype
import lightmanager


class Light:
    """This class represents a light.

    Attributes:
        Same as __init__ args.
    """

    def __init__(
        self,
        manager: "lightmanager.LightManager",
        lid: int,
        lightmap: filetype.ImageFile,
        layer: int,
        x: int,
        y: int,
        w: int,
        h: int,
        alpha: int,
        blendmode: int,
        colormod: Tuple[int, int, int],
        entity: entity.Entity,
        layermod: int,
    ):
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
            alpha: Alpha value of the light.
            blendmode: Whether to blend light instead of adding it. Useful for dark lights.
            colormod: RGB-triple of color value of the light.
            entity: If set, eid of entity to track the light to. Disabled if None.
            layermod: Integer to add to the layer the light is drawn on when tracking an entity.
        """
        self.manager = manager

        self.lid = lid
        self.lightmap = lightmap
        self.layer = layer
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.alpha = alpha
        self.blendmode = blendmode
        self.colormod = colormod
        self.entity = entity

        if entity is not None:
            self.manager.driftwood.tick.register(self._track_entity, message=(entity, layermod))

    def _track_entity(self, seconds_past: float, msg: Tuple[entity.Entity, int]) -> None:
        """Follow an entity's position."""
        try:  # Avoid strange timing anomaly.
            self.x = (
                self.manager.driftwood.entity.entity(msg[0]).x + self.manager.driftwood.entity.entity(msg[0]).width // 2
            )
            self.y = (
                self.manager.driftwood.entity.entity(msg[0]).y
                + self.manager.driftwood.entity.entity(msg[0]).height // 2
            )
            self.layer = self.manager.driftwood.entity.entity(msg[0]).layer + msg[1]
        except AttributeError:
            self.manager.driftwood.tick.unregister(self._track_entity)

        self.manager.driftwood.area.changed = True
