#!/usr/bin/env python
from displaybase import DisplayBase

# Drawing

'''

class SimpleSquare(DisplayBase):
    def __init__(self, *args, **kwargs):
        super(SimpleSquare, self).__init__(*args, **kwargs)

    def run(self):
        offset_canvas = self.matrix.CreateFrameCanvas()
        while True:
            for x in range(0, self.matrix.width):
                offset_canvas.SetPixel(x, x, 255, 255, 255)
                offset_canvas.SetPixel(offset_canvas.height - 1 - x, x, 255, 0, 255)

            for x in range(0, offset_canvas.width):
                offset_canvas.SetPixel(x, 0, 255, 0, 0)
                offset_canvas.SetPixel(x, offset_canvas.height - 1, 255, 255, 0)

            for y in range(0, offset_canvas.height):
                offset_canvas.SetPixel(0, y, 0, 0, 255)
                offset_canvas.SetPixel(offset_canvas.width - 1, y, 0, 255, 0)
            offset_canvas = self.matrix.SwapOnVSync(offset_canvas)


# Main function
if __name__ == "__main__":
    simple_square = SimpleSquare()
    if (not simple_square.process()):
        simple_square.print_help()
'''
'''
import math


class RotatingBlockGenerator(DisplayBase):
    def __init__(self, *args, **kwargs):
        super(RotatingBlockGenerator, self).__init__(*args, **kwargs)

    def rotate(self, x, y, angle):
        return {
            "new_x": x * math.cos(angle) - y * math.sin(angle),
            "new_y": x * math.sin(angle) + y * math.cos(angle)
        }

    def scale_col(self, val, lo, hi):
        if val < lo:
            return 0
        if val > hi:
            return 255
        return 255 * (val - lo) / (hi - lo)

    def run(self):
        cent_x = self.matrix.width / 2
        cent_y = self.matrix.height / 2

        rotate_square = min(self.matrix.width, self.matrix.height) * 1.41
        min_rotate = cent_x - rotate_square / 2
        max_rotate = cent_x + rotate_square / 2

        display_square = min(self.matrix.width, self.matrix.height) * 0.7
        min_display = cent_x - display_square / 2
        max_display = cent_x + display_square / 2

        deg_to_rad = 2 * 3.14159265 / 360
        rotation = 0
        offset_canvas = self.matrix.CreateFrameCanvas()

        while True:
            rotation += 1
            rotation %= 360

            for x in range(int(min_rotate), int(max_rotate)):
                for y in range(int(min_rotate), int(max_rotate)):
                    ret = self.rotate(x - cent_x, y - cent_x, deg_to_rad * rotation)
                    rot_x = ret["new_x"]
                    rot_y = ret["new_y"]

                    if x >= min_display and x < max_display and y >= min_display and y < max_display:
                        offset_canvas.SetPixel(rot_x + cent_x, rot_y + cent_y, self.scale_col(x, min_display, max_display), 255 - self.scale_col(y, min_display, max_display), self.scale_col(y, min_display, max_display))
                    else:
                        offset_canvas.SetPixel(rot_x + cent_x, rot_y + cent_y, 0, 0, 0)

            offset_canvas = self.matrix.SwapOnVSync(offset_canvas)

# Main function
if __name__ == "__main__":
    rotating_block_generator = RotatingBlockGenerator()
    if (not rotating_block_generator.process()):
        rotating_block_generator.print_help()
'''
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

class RunText(DisplayBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("/home/pi/2048-Pi-Display/fonts/4x6.bdf")
        textColor = graphics.Color(59, 59, 59)
        pos = offscreen_canvas.width


        #image = Image.open("/home/pi/2048-Pi-Display/img.jpg")
        self.matrix.brightness = 40

       
        while True:

            t_string = datetime.datetime.today().strftime("%H:%M:%S")

            offscreen_canvas.Clear()
            len = graphics.DrawText(offscreen_canvas, font, 0, 6, textColor, t_string)
            graphics.DrawLine(offscreen_canvas, 0, 7, 0, 31, graphics.Color(255, 255, 255))

            time.sleep(0.1)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
        


# Main function
if __name__ == "__main__":
    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()


'''
currentTrack = ''
while True:
    token = util.prompt_for_user_token("jc8a1vumj4nofex2isggs9uur","user-read-currently-playing",client_id='a362ed228f6f42dda29df88594deacf9',client_secret='55924005c1a04aaca88d5a8e3dd39653',redirect_uri='https://callback/')

    sp = Spotify(auth=token)
    result = sp.current_user_playing_track()

    if currentTrack == result["item"]["name"]:
        time.sleep(5)
        continue

    currentTrack = result["item"]["name"]
    resp = requests.get(result["item"]["album"]["images"][0]["url"])
    image_file = io.BytesIO(resp.content)
    image = Image.open(image_file)
    image.thumbnail((self.matrix.width, self.matrix.height), Image.ANTIALIAS)
    self.matrix.SetImage(image.convert('RGB'))
    time.sleep(5)

'''