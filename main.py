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
import serial
import io
import time
import os

class rPiDisplay(DisplayBase):

    def __init__(self, *args, **kwargs):
        super(rPiDisplay, self).__init__(*args, **kwargs)

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        pos = offscreen_canvas.width
        self.matrix.brightness = 100

        port = '/dev/ttyACM0'
        baudrate = 9600
        ser = serial.Serial(port, baudrate, timeout=0.001)

        # States:
        # 0 = Start screen
        # 1 = Moving
            # 1.3
            # 1.6
        # 2 = slowdown
            # 2.3
            # 2.6
        # 3 = done
        # 4 = show success

        state = -1

        shouldMove = False
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

        frameInterval = 0.05
        iteration = 0

        serial_response = ''
        while True:
            
            if state == 0:
                vels = [0, 0, 0]
                iteration = 0
                # Check for iO
                while state == 0:
                    serial_response += ser.read()
                    if "1" in serial_response:
                        serial_response = ''
                        ser.flushInput()
                        ser.flushOutput()
                        state = 1
                        break

            if state == 1:
                vels = [1, 3, 2]
                state = 1.3
                iteration = 0

            if state == 1.3 and 1.5 / frameInterval <= iteration:
                vels = [3, 4, 3]
                state = 1.6
                iteration = 0

            if state == 1.6 and 1 / frameInterval <= iteration:
                vels = [6, 5, 6]
                state = 2
                iteration = 0

            # After 5s start slowdown
            if state == 2 and 3 / frameInterval <= iteration:
                vels = [3, 4, 3]
                state = 2.3
                iteration = 0

            if state == 2.3 and 1.5 / frameInterval <= iteration:
                vels = [1, 3, 2]
                state = 2.6
                iteration = 0

            if state == 2.6 and 1 / frameInterval <= iteration:
                vels = [1, 1, 1]
                state = 3
                iteration = 0

            # Come to complete stop
            if state == 3 and 3 / frameInterval <= iteration:
                for column in range(3):
                    for item in cols[column]:
                        if item[2] == 12:
                            vels[column] = 0
                if vels == [0, 0, 0]:
                    state = 0

            if state == -1:
                state = 0

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
            self.matrix.SwapOnVSync(offscreen_canvas)
            time.sleep(frameInterval)

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

