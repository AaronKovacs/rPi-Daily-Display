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
import socket
import os
from config import weather_zipcode, openweathermap_appid
from threading import Thread
import json 
import copy 
from random import randrange
import random


class rPiDisplay(DisplayBase):

    def __init__(self, *args, **kwargs):
        super(rPiDisplay, self).__init__(*args, **kwargs)

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        pos = offscreen_canvas.width
        self.matrix.brightness = 100

        # image, x, y
        cols = [[], [], []]

        # slowest to fastest: 60, 
        vels = [1, 3, 2]

        for column in range(3):
            for i in range(10):
                x = 0
                if column == 1:
                    x = 12
                if column == 2:
                    x = 24
                cols[column].append([randomIcon(), x, i * 10])

        iteration = 0
        while True:
            offscreen_canvas.Clear()
            for col in cols:
                for row in col:
                    # Offscreen remove
                    if row[2] >= 32:
                        col.remove(row)
                        continue
                    # Insert new icon

                    if col[0][2] >= 0:
                        col.insert(0, [randomIcon(), row[1], -10])

                    # Move
                    row[2] = row[2] + (1 * vels[cols.index(col)])

                    offscreen_canvas.SetImage(row[0], row[1], row[2])


            iteration += 1
            if iteration == 60:
                iteration = 0

            self.matrix.SwapOnVSync(offscreen_canvas)
            time.sleep(0.1)

images = ['money', 'heart-icon', 'happy', 'fire', 'bird', 'ghost', 'xmark']
def randomIcon():
    return icon(random.choice(images))
   
def icon(name):
    return Image.open("/home/pi/2048-Pi-Display/images/%s.png" % (name)).convert('RGB').resize((8, 8), resample=0)

          
def drawRect(canvas, x, y, width, height, red, green, blue):
        for x_mod in range(0, width):
            for y_mod in range(0, height):
                canvas.SetPixel(x + x_mod, y + y_mod, red, green, blue)

# Main function
if __name__ == "__main__":
    run_text = rPiDisplay()
    if (not run_text.process()):
        run_text.print_help()

