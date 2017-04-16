####################################
# Driftwood 2D Game Dev. Suite     #
# widgetmanager.py                 #
# Copyright 2014 PariahSoft LLC    #
# Copyright 2017 Michael D. Reiley #
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

from sdl2 import *
from sdl2.ext import *
from sdl2.sdlttf import *

import widget


class WidgetManager:
    """The Widget Manager
    
    This class keeps track of widgets. These are things like text dialogs and UI elements.
    
    Attributes:
        driftwood: Base class instance.
        widgets: The dictionary of widgets, sorted by widget id.
        selected: Whether or not this widget is the selected widget. ex. a selected button in a UI menu.
    """

    def __init__(self, driftwood):
        self.driftwood = driftwood

        self.widgets = {}
        self.selected = None

        self.__last_wid = -1

        self.__spritefactory = None  # The sdlext sprite factory.
        self.__uifactory = None  # The sdlext ui factory.
        self.__uiprocessor = None  # The sdlext ui processor.

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
        if wid not in self.widgets:
            self.driftwood.log.msg("ERROR", "Widget", "select", "Cannot select nonexistent widget", wid)
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
            self.driftwood.log.msg("ERROR", "Widget", "release", "Cannot release if no widget selected")
            return False
        self.widgets[self.selected].selected = False
        self.selected = None
        return True

    def container(self, imagefile=None, parent=None, x=0, y=0, width=0, height=0, active=True):
        """Create a new container widget.

        A container widget can have a background image, and other widgets can be contained by it. Widgets in a container
        are drawn together and the container's x and y positions are added to the widget's x and y positions.

        Args:
            imagefile: If set, filename of the image file to use as a background.
            parent: If set, the wid of the parent container.
            x: The x position of the container on the window.
            y: The y position of the container on the window.
            width: The width of the container.
            height: The height of the container.
            active: Whether to make the widget active right away.

        Returns:
            Widget ID of the new container widget if succeeded, None if failed.
        """
        self.__last_wid += 1

        if imagefile:  # It has a background.
            image = self.driftwood.resource.request_image(imagefile)
            if not image:
                self.driftwood.log.msg("ERROR", "Widget", "container", "no such image", imagefile)
                return None
        else:
            image = None


        new_widget = widget.ContainerWidget(self, self.__last_wid, parent, image, x, y, width, height)
        self.widgets[self.__last_wid] = new_widget

        ret = new_widget._prepare()
        if ret is None:
            self.driftwood.log.msg("ERROR", "Widget", "container", "could not create container widget")
            return None

        if active:  # Do we activate it to be drawn/used?
            self.activate(new_widget.wid)

        return new_widget.wid

    def text(self, contents, fontfile, ptsize, parent=None, x=0, y=0, width=-1, height=-1, color="000000FF",
             active=True):
        """Create a new text widget.

            A text widget puts text on the screen. It cannot have a background image, but can have a color.

            Args:
                contents: The contents of the text.
                fontfile: Filename of the font to render the text with.
                ptsize: The point size of the text.
                parent: If set, the wid of the parent container.
                x: The x position of the text on the window. Center if -1.
                y: The y position of the text on the window. Center if -1.
                width: The width of the text. If -1 don't alter it.
                height: The height of the container. If -1 don't alter it.
                color: The color and alpha to draw the text in.
                active: Whether to make the widget active right away.

            Returns:
                Widget ID of the new text widget if succeeded, None if failed.
        """
        self.__last_wid += 1

        font = self.driftwood.resource.request_font(fontfile, ptsize)
        if not font:
            self.driftwood.log.msg("ERROR", "Widget", "container", "no such font", fontfile)
            return None

        new_widget = widget.TextWidget(self, self.__last_wid, parent, contents, font, ptsize, x, y, width, height,
                                       color)
        self.widgets[self.__last_wid] = new_widget

        ret = new_widget._prepare()
        if ret is None:
            self.driftwood.log.msg("ERROR", "Widget", "text", "could not create text widget")
            return None

        if active:  # Do we activate it to be drawn/used?
            self.activate(new_widget.wid)

        return new_widget.wid

    def activate(self, wid):
        """Activate a widget. This widget becomes visible.
        
        Args:
            wid: Widget id of widget to activate.
        """
        if wid in self.widgets:
            self.widgets[wid].active = True
            self.driftwood.area.changed = True
            return True
        self.driftwood.log.msg("ERROR", "Widget", "activate", "attempt to activate nonexistent widget", wid)
        return False

    def deactivate(self, wid):
        """Deactivate a widget. This widget becomes invisible.

        Args:
            wid: Widget id of widget to deactivate.
        """
        if wid in self.widgets:
            self.widgets[wid].active = False
            self.driftwood.area.changed = False
            return True
        self.driftwood.log.msg("ERROR", "Widget", "deactivate", "attempt to deactivate nonexistent widget", wid)
        return False

    def kill(self, wid):
        """Kill a widget.
        
        Args:
            wid: Widget id of widget to kill.
        """
        if wid in self.widgets:
            self.widgets[wid]._terminate()
            del self.widgets[wid]
            self.driftwood.area.changed = True
            return True
        self.driftwood.log.msg("ERROR", "Widget", "kill", "attempt to kill nonexistent widget", wid)
        return False

    def widget(self, wid):
        """Get a widget by widget id.
        
        Args:
            wid: The widget id of the widget to return.
        """
        if wid in self.widgets:
            return self.widgets[wid]
        return None

    def reset(self):
        """Destroy all widgets.
        """
        for widget in self.widgets:
            self.widgets[widget]._terminate()
        self.widgets = {}
        self.selected = None
        return True

    def _draw_widgets(self):
        """Copy the widgets into FrameManager. This is signaled by AreaManager once the area is drawn."""
        for wid in sorted(self.widgets.keys()):
            if self.widgets[wid].active and self.widgets[wid].srcrect():  # It's visible, draw it.
                # But ignore inactive containers.
                if (not self.widgets[wid].parent) or self.widgets[self.widgets[wid].parent].active:
                    srcrect = self.widgets[wid].srcrect()
                    dstrect = list(self.widgets[wid].dstrect())
                    if type(self.widgets[wid]) is widget.ContainerWidget and self.widgets[wid].image:
                        # Draw a container.
                        r = self.driftwood.frame.overlay(self.widgets[wid].image.texture, srcrect, dstrect)
                        if type(r) is int and r < 0:
                            self.driftwood.log.msg("ERROR", "Widget", "_draw_widgets", "SDL", SDL_GetError())
                    elif type(self.widgets[wid]) is widget.TextWidget and self.widgets[wid].texture:
                        # Draw some text.
                        r = self.driftwood.frame.overlay(self.widgets[wid].texture, srcrect, dstrect)
                        if type(r) is int and r < 0:
                            self.driftwood.log.msg("ERROR", "Widget", "_draw_widgets", "SDL", SDL_GetError())

    def __prepare(self):
        """Initialize some things we need to get started.
        """
        if TTF_Init() < 0:
            self.driftwood.log.msg("ERROR", "Widget", "__prepare", "SDL_TTF", TTF_GetError())
        self.__spritefactory = SpriteFactory(sprite_type=TEXTURE, renderer=self.driftwood.window.renderer)
        self.__uifactory = UIFactory(self.__spritefactory)
        self.__uiprocessor = UIProcessor()

    def _terminate(self):
        """Cleanup before deletion.
        """
        for widget in self.widgets:
            self.widgets[widget]._terminate()
        self.widgets = {}
        TTF_Quit()
