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

from ctypes import byref, c_int

from sdl2 import *
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

    def container(self, imagefile=None, container=None, x=0, y=0, width=0, height=0, active=True):
        """Create a new container widget.

        A container widget can have a background image, and other widgets can be contained by it. Widgets in a container
        are drawn together and the container's x and y positions are added to the widget's x and y positions.

        Args:
            imagefile: If set, ilename of the image file to use as a background.
            container: If set, the wid of the parent container.
            x: The x position of the container on the window.
            y: The y position of the container on the window.
            width: The width of the container.
            height: The height of the container.
            active: Whether to make the widget active right away.

        Returns:
            Widget ID of the new container widget if succeeded, None if failed.
        """
        self.__last_wid += 1

        new_widget = widget.Widget(self, "container")
        self.widgets[self.__last_wid] = new_widget

        # Set the variables.
        new_widget.wid = self.__last_wid
        new_widget.x = x
        new_widget.y = y
        new_widget.realx = x
        new_widget.realy = y
        new_widget.width = width
        new_widget.height = height

        # Center if not in a container.
        if container is None:
            window_logical_width = self.driftwood.window.logical_width
            window_logical_height = self.driftwood.window.logical_height
            window_zoom = self.driftwood.config["window"]["zoom"]
            if x == -1:
                new_widget.x = (window_logical_width // window_zoom - new_widget.width) // 2
                new_widget.realx = new_widget.x
            if y == -1:
                new_widget.y = (window_logical_height // window_zoom - new_widget.height) // 2
                new_widget.realy = new_widget.y

        else:
            if self.widgets[container].type == "container":  # It has a container.
                new_widget.container = container
                self.widgets[container].contains.append(new_widget.wid)
                if self.widgets[container].realx and self.widgets[container].realy:  # Set the adjusted x and y.
                    # Either center or place in a defined position.
                    if x == -1:
                        new_widget.realx = self.widgets[container].realx + \
                                           self.widgets[container].width // 2 - \
                                           new_widget.width // 2
                    else:
                        new_widget.realx += self.widgets[container].realx

                    if y == -1:
                        new_widget.realy = self.widgets[container].realy + \
                                           self.widgets[container].height // 2 - \
                                           new_widget.height // 2
                    else:
                        new_widget.realy += self.widgets[container].realy

            else:  # Fake container.
                self.driftwood.log.msg("ERROR", "Widget", "container", "not a container", container)
                return None

        if imagefile:  # It has a background.
            new_widget.image = self.driftwood.resource.request_image(imagefile)

        if active:  # Do we activate it to be drawn/used?
            self.activate(new_widget.wid)

        return new_widget.wid

    def text(self, contents, font, ptsize, container=None, x=0, y=0, width=-1, height=-1, color="000000FF",
             active=True):
        """Create a new text widget.

            A text widget puts text on the screen. It cannot have a background image, but can have a color.

            Args:
                contents: The contents of the text.
                font: The font to render the text with.
                ptsize: The point size of the text.
                container: If set, the wid of the parent container.
                x: The x position of the text on the window. Center if -1.
                y: The y position of the text on the window. Center if -1.
                width: The width of the text. If -1 don't alter it.
                height: The height of the container. If -1 don't alter it.
                color: The color and alpha to draw the text in.
                active: Whether to make the widget active right away.

            Returns:
                Widget ID of the new text widget.
        """
        self.__last_wid += 1

        new_widget = widget.Widget(self, "text")
        self.widgets[self.__last_wid] = new_widget

        # Set the variables.
        new_widget.wid = self.__last_wid
        new_widget.contents = contents
        new_widget.ptsize = ptsize
        new_widget.x = x
        new_widget.y = y
        new_widget.realx = x
        new_widget.realy = y
        new_widget.width = width
        new_widget.height = height

        new_widget.font = self.driftwood.resource.request_font(font, ptsize)
        if not new_widget.font:
            return None

        # Get text width and height.
        tw, th = c_int(), c_int()
        TTF_SizeText(new_widget.font.font, contents.encode(), byref(tw), byref(th))
        new_widget.textwidth, new_widget.textheight = tw.value, th.value

        # Set width and height if not overridden.
        if width == -1:
            new_widget.width = tw.value
        if height == -1:
            new_widget.height = th.value

        # Center if not in a container.
        if container is None:
            window_logical_width = self.driftwood.window.logical_width
            window_logical_height = self.driftwood.window.logical_height
            window_zoom = self.driftwood.config["window"]["zoom"]
            if x == -1:
                new_widget.x = (window_logical_width // window_zoom - new_widget.width) // 2
                new_widget.realx = new_widget.x
            if y == -1:
                new_widget.y = (window_logical_height // window_zoom - new_widget.height) // 2
                new_widget.realy = new_widget.y

        # Are we inside a container?
        elif self.widgets[container].type == "container":
            new_widget.container = container
            self.widgets[container].contains.append(new_widget.wid)
            if self.widgets[container].realx and self.widgets[container].realy:  # Set the adjusted x and y.
                # Either center or place in a defined position.
                if x == -1:
                    new_widget.realx = self.widgets[container].realx + \
                                       self.widgets[container].width // 2 - \
                                       new_widget.width // 2
                else:
                    new_widget.realx += self.widgets[container].realx

                if y == -1:
                    new_widget.realy = self.widgets[container].realy + \
                                       self.widgets[container].height // 2 - \
                                       new_widget.height // 2
                else:
                    new_widget.realy += self.widgets[container].realy

        # Render.
        color_temp = SDL_Color()
        color_temp.r, color_temp.g, color_temp.b, color_temp.a = int(color[0:2], 16), int(color[2:4], 16), \
                                                                 int(color[4:6], 16), int(color[6:8], 16)
        surface_temp = TTF_RenderUTF8_Solid(new_widget.font.font, contents.encode(), color_temp)

        # Convert to a texture we can use internally.
        if surface_temp:
            new_widget.texture = SDL_CreateTextureFromSurface(self.driftwood.window.renderer,
                                                              surface_temp)
            SDL_FreeSurface(surface_temp)
            if not new_widget.texture:
                self.driftwood.log.msg("ERROR", "Widget", "text", "SDL", SDL_GetError())
        else:
            self.driftwood.log.msg("ERROR", "Widget", "text", "TTF", TTF_GetError())

        if active:  # Do we activate it to be drawn/used?
            self.activate(new_widget.wid)

    def activate(self, wid):
        if wid in self.widgets:
            self.widgets[wid].active = True
            self.driftwood.area.changed = True
            return True
        self.driftwood.log.msg("ERROR", "Widget", "activate", "attempt to activate nonexistent widget", wid)
        return False

    def deactivate(self, wid):
        if wid in self.widgets:
            self.widgets[wid].active = False
            self.driftwood.area.changed = False
            return True
        self.driftwood.log.msg("ERROR", "Widget", "deactivate", "attempt to deactivate nonexistent widget", wid)
        return False

    def kill(self, wid):
        if wid in self.widgets:
            self.widgets[wid]._terminate()
            del self.widgets[wid]
            self.driftwood.area.changed = True
            return True
        self.driftwood.log.msg("ERROR", "Widget", "kill", "attempt to kill nonexistent widget", wid)
        return False

    def widget(self, wid):
        if wid in self.widgets:
            return self.widgets[wid]
        return None

    def reset(self):
        for widget in self.widgets:
            self.widgets[widget]._terminate()
        self.widgets = {}
        self.selected = None
        return True

    def _draw_widgets(self):
        """Copy the widgets into FrameManager. This is signaled by AreaManager once the area is drawn."""
        for widget in sorted(self.widgets.keys()):
            if self.widgets[widget].active and self.widgets[widget].srcrect():  # It's visible, draw it.
                # But ignore inactive containers.
                if (not self.widgets[widget].container) or self.widgets[self.widgets[widget].container].active:
                    srcrect = self.widgets[widget].srcrect()
                    dstrect = list(self.widgets[widget].dstrect())
                    if self.widgets[widget].type == "container" and self.widgets[widget].image:  # Draw a container.
                        r = self.driftwood.frame.overlay(self.widgets[widget].image.texture, srcrect, dstrect)
                        if type(r) is int and r < 0:
                            self.driftwood.log.msg("ERROR", "Widget", "_draw_widgets", "SDL", SDL_GetError())
                    elif self.widgets[widget].type == "text" and self.widgets[widget].texture:  # Draw some text.
                        r = self.driftwood.frame.overlay(self.widgets[widget].texture, srcrect, dstrect)
                        if type(r) is int and r < 0:
                            self.driftwood.log.msg("ERROR", "Widget", "_draw_widgets", "SDL", SDL_GetError())

    def __prepare(self):
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
