#!/usr/bin/env python
from displaybase import DisplayBase

from rgbmatrix import graphics
import time
import datetime
from PIL import Image
from client import Spotify
import util
from PIL import Image
import urllib2 as urllib
import io
import requests
import pytz


class RunText(DisplayBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("/home/pi/2048-Pi-Display/fonts/4x6.bdf")
        pos = offscreen_canvas.width
        self.matrix.brightness = 10
        while True:
            offscreen_canvas.Clear()
            graphics.DrawText(offscreen_canvas, font, 0, 6, graphics.Color(255, 0, 0), "Net Err")
            len = graphics.DrawText(offscreen_canvas, font, pos, 14, graphics.Color(59, 59, 59), "Trying...")
            
            pos -= 1
            if (pos + len < 0):
                pos = offscreen_canvas.width
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

            time.sleep(0.1)
        


# Main function
if __name__ == "__main__":
    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()
