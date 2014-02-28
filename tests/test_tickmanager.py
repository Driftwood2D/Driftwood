###################################
## Driftwood 2D Game Dev. Suite  ##
## test_tickmanager.py           ##
## Copyright 2014 PariahSoft LLC ##
###################################

## **********
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to
## deal in the Software without restriction, including without limitation the
## rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
## sell copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in
## all copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
## FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
## IN THE SOFTWARE.
## **********

import unittest
import unittest.mock as mock

import tickmanager

def driftwood():
    """Create a mock, shared Driftwood object"""
    d = mock.Mock()
    d.config = {
        'tick': {
            'tps': 1001,    # 1000 // 1001 == 0
        }
    }
    d.log.msg.side_effect = Exception('log.msg called')
    return d

class TestTickManager(unittest.TestCase):
    """Test that the TickManager handles ticks properly.
    """

    def test_pause_doesnt_call_ticks(self):
        """The TickManager should not call registered callbacks when paused"""
        callback = mock.Mock()
        callback.__qualname__ = "<blank>" # TickManager requires callbacks have
                                          # __qualname__

        ticker = tickmanager.TickManager(driftwood())
        ticker.toggle_pause()
        ticker.register(callback)
        ticker.tick()

        assert not callback.called

    def test_pause_does_call_input_and_window(self):
        """Even when paused, the TickManager should call input.tick(None) and
           window.tick(None)"""
        d = driftwood()
        ticker = tickmanager.TickManager(d)
        ticker.toggle_pause()
        ticker.tick()

        d.input.tick.assert_called_with(None)
        d.window.tick.assert_called_with(None)
