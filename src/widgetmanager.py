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


class WidgetManager:

    def __init__(self, driftwood):
        self.driftwood = driftwood

        self.widgets = {}
        self.focus = None

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

    def focus(self, wid):
        if not wid in self.widgets:
            self.driftwood.log.msg("Error", "Widget", "Cannot focus nonexistent widget", wid)
            return False
        if self.focus is not None:
            self.widgets[self.focus].focus = False
        self.widgets[wid].focus = True
        self.focus = wid
        return True

    def release(self):
        if self.focus is None:
            self.driftwood.log.msg("Error", "Widget", "Cannot release if no widget focused")
            return False
        self.widgets[self.focus].focus = False
        self.focus = None
        return True

    def container(self):
        pass

    def text(self):
        pass

    def activate(self, wid):
        pass

    def deactivate(self, wid):
        pass

    def kill(self, wid):
        pass

    def widget(self, wid):
        pass

    def __prepare(self):
        if TTF_Init() < 0:
            self.driftwood.log.msg("Error", "Widget", "SDL_TTF", TTF_GetError())
        self.__spritefactory = SpriteFactory(sprite_type=TEXTURE)
        self.__uifactory = UIFactory(self.__spritefactory)
        self.__uiprocessor = UIProcessor()

    def __del__(self):
        TTF_Quit()