####################################
# Driftwood 2D Game Dev. Suite     #
# widgetmanager.py                 #
# Copyright 2014 PariahSoft LLC    #
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

from sdl2.ext import *
from sdl2.sdlttf import *

import widget


class WidgetManager:

    def __init__(self, driftwood):
        self.driftwood = driftwood

        self.widgets = {}
        self.selected = None

        self.__last_wid = -1

        self.__spritefactory = None
        self.__uifactory = None
        self.__uiprocessor = None

        self.__prepare()

    def __contains__(self, wid):
        if self.widget(wid):
            return True
        return False

    def __getitem__(self, wid):
        return self.widget(wid)

    def __delitem__(self, wid):
        return self.kill(wid)

    def __iter__(self):
        return self.widgets.items()

    def select(self, wid):
        """Select the specified widget.
        
        An example is selecting a button in a menu or selecting a text input box, out of the other widgets on screen.
        
        Args:
             wid: Widget ID of the widget to select.

        Returns:
            True if succeeded, False if failed.
        """
        if not wid in self.widgets:
            self.driftwood.log.msg("WARNING", "Widget", "Cannot select nonexistent widget", wid)
            return False
        if self.selected is not None:
            self.widgets[self.selected].selected = False
        self.widgets[wid].selected = True
        self.selected = wid
        return True

    def release(self):
        """Release the currently selected widget so that no widgets are selected.

        Returns:
            True if succeeded, False if failed.
        """
        if self.selected is None:
            self.driftwood.log.msg("WARNING", "Widget", "Cannot release if no widget selected")
            return False
        self.widgets[self.selected].selected = False
        self.selected = None
        return True

    def container(self, imagefile=None, container=None, x=0, y=0, width=0, height=0):
        self.__last_wid += 1
        self.widgets[self.__last_wid] = widget.Widget(self, "container")
        self.widgets[self.__last_wid].wid = self.__last_wid
        self.widgets[self.__last_wid].x = x
        self.widgets[self.__last_wid].y = y
        self.widgets[self.__last_wid].width = width
        self.widgets[self.__last_wid].height = height

        if container:
            self.widgets[self.__last_wid].container = container
            self.widgets[container].append(self.__last_wid)

        if imagefile:
            self.widgets[self.__last_wid].image = self.driftwood.resource.request_image(imagefile)

        return self.__last_wid

    def text(self):
        pass

    def activate(self, wid):
        if wid in self.widgets:
            self.widgets[wid].active = True
            return True
        return False

    def deactivate(self, wid):
        if wid in self.widgets:
            self.widgets[wid].active = False
            return True
        return False

    def kill(self, wid):
        pass

    def widget(self, wid):
        pass

    def reset(self):
        self.widgets = {}
        self.selected = None

    def __prepare(self):
        if TTF_Init() < 0:
            self.driftwood.log.msg("ERROR", "Widget", "SDL_TTF", TTF_GetError())
        self.__spritefactory = SpriteFactory(sprite_type=TEXTURE, renderer=self.driftwood.window.renderer)
        self.__uifactory = UIFactory(self.__spritefactory)
        self.__uiprocessor = UIProcessor()

    def __del__(self):
        TTF_Quit()