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
        self.matrix.brightness = 70

       
        iteration = 0
        currentWeather = '0F '
        wotd = ''
        currentTrack = ''
        image = None
        while True:

            t_string = datetime.datetime.today().strftime("%H:%M:%S")

            offscreen_canvas.Clear()
            graphics.DrawText(offscreen_canvas, font, 0, 6, graphics.Color(89, 89, 89), t_string)
            graphics.DrawLine(offscreen_canvas, 0, 7, 31, 7, graphics.Color(59, 59, 59))

            day_color = graphics.Color(59, 59, 59)
            day = datetime.datetime.today().strftime("%A").upper()
            if day == 'MONDAY':
                day_color = graphics.Color(248, 205, 70)
            if day == 'TUESDAY':
                day_color = graphics.Color(235, 76, 198)
            if day == 'WEDNESDAY':
                day_color = graphics.Color(92, 199, 59)
            if day == 'THURSDAY':
                day_color = graphics.Color(241, 150, 57)
            if day == 'FRIDAY':
                day_color = graphics.Color(36, 104, 246)
            if day == 'SATURDAY':
                day_color = graphics.Color(92, 31, 199)
            if day == 'SUNDAY':
                day_color = graphics.Color(234, 50, 35)

            graphics.DrawText(offscreen_canvas, font, 0, 14, day_color, day)
            graphics.DrawLine(offscreen_canvas, 0, 15, 31, 15, graphics.Color(59, 59, 59))

            if iteration % 100 == 0:
                resp = requests.get("https://api.openweathermap.org/data/2.5/weather?zip=15009,us&units=imperial&appid=e7694bebbbb89a1e84450d04255dfb59")
                data = resp.json()
                currentTemp = int(data["main"]["temp"])
                weather_color = graphics.Color(59, 59, 59)
                main_code = data["weather"][0]["main"].upper()

                if main_code == "CLOUDS":
                    main_code = "CLDS"
                    weather_color = graphics.Color(115, 253, 255)

                if main_code == "RAIN":
                    main_code = "RAIN"
                    weather_color = graphics.Color(4, 50, 255)

                if main_code == "THUNDERSTORM":
                    main_code = "THDR"
                    weather_color = graphics.Color(59, 59, 59)

                if main_code == "DRIZZLE":
                    main_code = "DRIZ"
                    weather_color = graphics.Color(148, 55, 255)

                if main_code == "SNOW":
                    main_code = "SNOW"
                    weather_color = graphics.Color(255, 47, 146)

                if main_code == "ATMOSPHERE":
                    main_code = "ATMO"
                    weather_color = graphics.Color(0, 250, 146)

                if main_code == "CLEAR":
                    main_code = "CLER"
                    weather_color = graphics.Color(255, 147, 0)

                currentWeather  = '%sF %s' % (currentTemp, main_code)


            graphics.DrawText(offscreen_canvas, font, 0, 22, weather_color, currentWeather)
            graphics.DrawLine(offscreen_canvas, 0, 23, 31, 23, graphics.Color(59, 59, 59))


            if iteration % 1000 == 0:
                token = util.prompt_for_user_token("jc8a1vumj4nofex2isggs9uur","user-read-currently-playing",client_id='a362ed228f6f42dda29df88594deacf9',client_secret='55924005c1a04aaca88d5a8e3dd39653',redirect_uri='https://callback/')
                sp = Spotify(auth=token)
                result = sp.current_user_playing_track()

                if currentTrack != result["item"]["name"] and result["item"]["name"] != '':
                    currentTrack = result["item"]["name"]
                    resp = requests.get(result["item"]["album"]["images"][0]["url"])
                    image_file = io.BytesIO(resp.content)
                    image = Image.open(image_file)
                    image.thumbnail((9, 9), Image.ANTIALIAS)
                else:
                    currentTrack = result["item"]["name"]
                    image = None

            if iteration % 1000 == 0:
                resp = requests.get("http://urban-word-of-the-day.herokuapp.com/today")
                data = resp.json()
                wotd = data["word"]

            if currentTrack != '' and image is not None:
                offscreen_canvas.SetImage(image, offset_y=23)
            else:
                len = graphics.DrawText(offscreen_canvas, font, pos, 30, textColor, wotd)
                pos -= 1
                if (pos + len < 0):
                    pos = offscreen_canvas.width

            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

            iteration += 1
            time.sleep(0.1)
        


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