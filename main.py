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

class rPiDisplay(DisplayBase):

    

    def __init__(self, *args, **kwargs):
        super(rPiDisplay, self).__init__(*args, **kwargs)

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("/home/pi/2048-Pi-Display/fonts/4x6.bdf")
        textColor = graphics.Color(59, 59, 59)
        pos = offscreen_canvas.width

        self.matrix.brightness = 100
       
        iteration = 0
        currentWeather = '0F '
        wotd = 'Good Morning...'
        currentTrack = ''
        image = None
        is_playing = False
        weather_color = graphics.Color(59, 59, 59)
        spotify_color = graphics.Color(0, 99, 0)
        sent_ipaddress = False
        block_fill = False
        black_color = graphics.Color(255, 255, 255)

        new_image = None
        old_image = None
        currentStep = 0

        rain_coords = []
        pong_coord = [1, 1]
        pong_xDir = 1
        pong_yDir = -1
        for x in range(0, 10):
            rain_coords.append(randomOffset(32, 6))
        while True:

            if iteration % 5000 == 0:
                try: 
                    gw = os.popen("ip -4 route show default").read().split()
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.connect((gw[2], 0))
                    host_ip = s.getsockname()[0]
                    gateway = gw[2]
                    host_name = socket.gethostname()

                    value_str = "[rPi-Display] Host: %s IP: %s" % (host_name, host_ip)
                    try:
                        requests.post('http://prod.ft7mz3prg3.us-east-1.elasticbeanstalk.com/misc/text', json={'text': value_str})
                        sent_ipaddress = True
                        print("Sent IP Address")
                    except:
                        print('Couldn\'t POST data to remote. Throwing out text...')
                except: 
                    print("Unable to get Hostname and IP") 

            clock_resp = fetchTime()
            concocted_str = clock_resp[0]
            clock_color = clock_resp[1]
            day_color = clock_resp[2]
            day = clock_resp[3]

            offscreen_canvas.Clear()

            # Draw Time
            if block_fill:
                drawRect(offscreen_canvas, 0, 0, 32, 7, clock_color.red, clock_color.green, clock_color.blue)
                graphics.DrawText(offscreen_canvas, font, 0, 6, graphics.Color(255 - clock_color.red, 255 - clock_color.green, 255 - clock_color.blue), concocted_str)
            else:
                graphics.DrawText(offscreen_canvas, font, 0, 6, clock_color, concocted_str)

            graphics.DrawLine(offscreen_canvas, 0, 7, 31, 7, day_color)

            #Draw Day
            if block_fill:
                drawRect(offscreen_canvas, 0, 8, 32, 7, day_color.red, day_color.green, day_color.blue)
                graphics.DrawText(offscreen_canvas, font, 0, 14, graphics.Color(255 - day_color.red, 255 - day_color.green, 255 - day_color.blue), day)
            else:
                graphics.DrawText(offscreen_canvas, font, 0, 14, day_color, day)

            if iteration % 1 == 0:
                offscreen_canvas.SetPixel(pong_coord[0], pong_coord[1] + 8, 255, 255, 255)
                pong_result = pongPosition(pong_coord, pong_xDir, pong_yDir)
                pong_coord = pong_result[0]
                pong_xDir = pong_result[1]
                pong_yDir = pong_result[2]



            if iteration % 50 == 0:
                resp = fetchWeather()
                weather_color = resp[0]
                currentWeather = resp[1]

            if iteration % 100 == 0:
                t = Thread(target=downloadWeather)
                t.start()


            graphics.DrawLine(offscreen_canvas, 0, 15, 31, 15, weather_color)

            #Draw weather
            if block_fill:
                drawRect(offscreen_canvas, 0, 16, 32, 7, weather_color.red, weather_color.green, weather_color.blue)
                graphics.DrawText(offscreen_canvas, font, 0, 22, graphics.Color(255 - weather_color.red, 255 - weather_color.green, 255 - weather_color.blue), currentWeather)
            else:
                if 'RAIN' in currentWeather or 'SNOW' in currentWeather or 'DRIZ' in currentWeather or 'THDR' in currentWeather:
                    rain_color = graphics.Color(92, 200, 250)
                    if iteration % 2 == 0:
                        for index in range(0, len(rain_coords)):
                            if rain_coords[index][1] > 6:
                                rain_coords[index] = randomOffset(32, 6)
                            else:
                                rain_coords[index][1] += 1
                        if len(rain_coords) == 0:
                            for x in range(0, 10):
                                rain_coords.append(randomOffset(32, 6))                        
                    for coord in rain_coords:
                        offscreen_canvas.SetPixel(coord[0], coord[1] + 16, 92, 200, 250)

                graphics.DrawText(offscreen_canvas, font, 0, 22, weather_color, currentWeather)

            if iteration % 50 == 0:
                resp = fetchSpotify()
                is_playing = resp[0]
                if resp[2] is not None:
                    currentTrack = resp[2]
                if is_playing == False:
                    old_image = None
                    new_image = None
                if resp[1] is not None:
                    temp_image = resp[1].resize((32, 32), Image.ANTIALIAS)
                    if temp_image != old_image and temp_image != new_image:
                        if temp_image is not None:
                            image = temp_image.resize((9, 9), Image.ANTIALIAS)
                        if temp_image is not None:
                            if old_image is None:
                                old_image = temp_image
                            most_frequent = most_frequent_colour(image)
                            spotify_color = graphics.Color(most_frequent[0], most_frequent[1], most_frequent[2])
                        else:
                            spotify_color = graphics.Color(0, 99, 0)

                        if is_playing and new_image != old_image:
                            new_image = temp_image
                   
                    currentTrack = resp[2]

            if iteration % 100 == 0:
                t = Thread(target=downloadSpotify)
                t.start()

            if iteration % 1000 == 0:
                t = Thread(target=downloadUrbanWOTD)
                t.start()

            if iteration % 500 == 0:
                temp_wotd = fetchUrbanWOTD()
                if temp_wotd != "No internet??":
                    wotd = temp_wotd

            if is_playing:
                graphics.DrawLine(offscreen_canvas, 0, 23, 31, 23, spotify_color)
                leng = graphics.DrawText(offscreen_canvas, font, pos, 30, spotify_color, currentTrack)
                pos -= 1
                if (pos + leng < 10):
                    pos = offscreen_canvas.width
                if image is not None:
                    offscreen_canvas.SetImage(image, offset_y=23)
            else:
                # Draw Urban Dictionary WOTD
                graphics.DrawLine(offscreen_canvas, 0, 23, 31, 23, graphics.Color(59, 59, 59))
                leng = graphics.DrawText(offscreen_canvas, font, pos, 30, textColor, wotd)
                pos -= 1
                if (pos + leng < 0):
                    pos = offscreen_canvas.width

            
            
            iteration += 1

            today = datetime.datetime.today()
            timezone = pytz.timezone("America/New_York")
            d_aware = timezone.localize(today)

            hour = int(d_aware.strftime("%H"))

            if hour >= 1 and hour < 9:
                self.matrix.brightness = 10
                offscreen_canvas.Clear()

                # Draw Time
                graphics.DrawText(offscreen_canvas, font, 0, 6, graphics.Color(150, 0, 0), concocted_str)
                graphics.DrawText(offscreen_canvas, font, 0, 14, graphics.Color(150, 0, 0), currentWeather)

                offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
            else:
                if new_image is not None:
                    if new_image != old_image:
                        currentStep = animateAlbumArt(offscreen_canvas, old_image, new_image, currentStep)
                        if currentStep == 0:
                            old_image = new_image
                            new_image = None
                    else:
                        new_image = None

                offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
                self.matrix.brightness = 70

            time.sleep(0.1)

# Direction +1 (Up, Right) or -1 (Down, Left)
def pongPosition(lastCoord, xDir, yDir):
    newCoord = [0, 0]
    newCoord[0] = lastCoord[0]
    newCoord[1] = lastCoord[1]

    if yDir > 0:
        #Move Up
        newCoord[1] += 1
    else:
        #Move Down
        newCoord[1] -= 1

    if xDir > 0:
        #Move Right
        newCoord[0] += 1
    else:
        #Move Left
        newCoord[0] -= 1

    new_yDir = yDir
    new_xDir = xDir

    # Outside vertical bounds?
    if newCoord[1] < 0 or newCoord[1] > 6:
        new_yDir = -new_yDir

    # Outside horizontal bounds
    if newCoord[0] < 1 or newCoord[0] > 31:
        new_xDir = -new_xDir

    if new_xDir != xDir or new_yDir != yDir:
        return pongPosition(lastCoord, new_xDir, new_yDir)

    return (newCoord, new_xDir, new_yDir)


def randomOffset(width, height):
    return [randrange(width), randrange(height)]


def animateAlbumArt(canvas, old_image, new_image, currentStep):
    speed = 1
    finished = False

    if currentStep <= 23:
        adjustedStep = currentStep - 0
        canvas.SetImage(old_image.resize((9 + adjustedStep, 9 + adjustedStep), Image.ANTIALIAS), offset_y=23 - adjustedStep)
    elif currentStep <= 32 + 23:
        adjustedStep = currentStep - 23
        canvas.SetImage(old_image.resize((32, 32), Image.ANTIALIAS), offset_x=-adjustedStep, offset_y=0)
        canvas.SetImage(new_image.resize((32, 32), Image.ANTIALIAS), offset_x=32 - adjustedStep, offset_y=0)
    elif currentStep <= 3 + 32 + 23:
        canvas.SetImage(new_image.resize((32, 32), Image.ANTIALIAS), offset_x=0, offset_y=0)
    elif currentStep <= 23 + 3 + 32 + 23:
        adjustedStep = currentStep - 23 - 32 - 3
        canvas.SetImage(new_image.resize((32 - adjustedStep, 32 - adjustedStep), Image.ANTIALIAS), offset_x=0, offset_y=adjustedStep)
    elif currentStep > 23 + 3 + 32 + 23:
        old_image = new_image
        new_image = None
        finished = True

    currentStep += 1 * speed

    if finished:
        currentStep = 0

    return currentStep

def drawRect(canvas, x, y, width, height, red, green, blue):
        for x_mod in range(0, width):
            for y_mod in range(0, height):
                canvas.SetPixel(x + x_mod, y + y_mod, red, green, blue)


def most_frequent_colour(image):

    w, h = image.size
    pixels = image.getcolors(w * h)

    most_frequent_pixel = pixels[0]

    for count, colour in pixels:
        if count > most_frequent_pixel[0]:
            most_frequent_pixel = (count, colour)

    return most_frequent_pixel[1]


def fetchTime():
    today = datetime.datetime.today()
    timezone = pytz.timezone("America/New_York")
    d_aware = timezone.localize(today)

    hour = int(d_aware.strftime("%H"))
    clock_color = graphics.Color(107, 0, 0)
    if hour > 12:
        hour -= 12
        clock_color = graphics.Color(0, 0, 107)

    t_string = d_aware.strftime("%M:%S")

    if hour == 0:
        hour = 12
    concocted_str = "%s:%s" % (hour, t_string)

    day_color = graphics.Color(59, 59, 59)
    day = d_aware.strftime("%A").upper()

    day_trunc = ''
    if day == 'MONDAY':
        day_color = graphics.Color(248, 205, 70)
        day_trunc = 'MO'
    if day == 'TUESDAY':
        day_color = graphics.Color(235, 76, 198)
        day_trunc = 'TU'
    if day == 'WEDNESDAY':
        day_color = graphics.Color(92, 199, 59)
        day_trunc = 'WD'
    if day == 'THURSDAY':
        day_color = graphics.Color(241, 150, 57)
        day_trunc = 'TR'
    if day == 'FRIDAY':
        day_color = graphics.Color(36, 104, 246)
        day_trunc = 'FR'
    if day == 'SATURDAY':
        day_color = graphics.Color(92, 31, 199)
        day_trunc = 'SA'
    if day == 'SUNDAY':
        day_color = graphics.Color(234, 50, 35)
        day_trunc = 'SU'

    final_str = '%s %s/%s' % (day_trunc, d_aware.strftime("%-m"), d_aware.strftime("%-d"))

    return (concocted_str, clock_color, day_color, final_str)

def downloadSpotify():
    with open('/home/pi/2048-Pi-Display/spotify.json', 'w') as outfile:
        ak_token = util.prompt_for_user_token("jc8a1vumj4nofex2isggs9uur","user-read-currently-playing", client_id='a362ed228f6f42dda29df88594deacf9',client_secret='55924005c1a04aaca88d5a8e3dd39653',redirect_uri='https://callback/')
        lo_token = util.prompt_for_user_token("loganjohnson_","user-read-currently-playing", client_id='40905780d3124d0c8454937552023133',client_secret='6402502d32834e568339004b885ad0a1',redirect_uri='https://callback/')

        # Check logan
        sp = Spotify(auth=lo_token)
        result = sp.current_user_playing_track()

        try_aaron = False

        if result is None:
            try_aaron = True
        elif result["is_playing"] == False:
            try_aaron = True

        if try_aaron:
            sp = Spotify(auth=ak_token)
            result = sp.current_user_playing_track()

        if result is not None:
            if result["item"]["name"] != '':
                try:
                    resp = requests.get(result["item"]["album"]["images"][0]["url"])
                    image_file = io.BytesIO(resp.content)
                    with open('/home/pi/2048-Pi-Display/spotify_image.jpeg', 'w') as imagefile:
                        imagefile.write(resp.content)
                        imagefile.close()
                except:
                    print("Couldn't fetch image")
            json.dump(result, outfile, indent=4)
            outfile.close()
            

def fetchSpotify():
    is_playing = False
    image = None
    currentTrack = ''

    with open('/home/pi/2048-Pi-Display/spotify.json', 'r') as json_file:
        try:
            result = json.load(json_file)
            json_file.close()
            if result is not None and "is_playing" in result:
                is_playing = result["is_playing"]
                if currentTrack != result["item"]["name"] and result["item"]["name"] != '':
                    currentTrack = result["item"]["name"]
            image = Image.open('/home/pi/2048-Pi-Display/spotify_image.jpeg').convert('RGB')
            #image.thumbnail((32, 32), Image.ANTIALIAS)
        except:
            print("Couldn't open image file")

    return (is_playing, image, currentTrack)
        

def downloadUrbanWOTD():
    with open('/home/pi/2048-Pi-Display/urbanwotd.json', 'w') as outfile:
        try:
            resp = requests.get("http://urban-word-of-the-day.herokuapp.com/today")
            data = resp.json()
            json.dump(data, outfile, indent=4)
            outfile.close()
        except:
           print("No internet??")

def fetchUrbanWOTD():
    try:
        with open('/home/pi/2048-Pi-Display/urbanwotd.json', 'r') as json_file:
            data = json.load(json_file)
            json_file.close()
            if data is not None:
               return data["word"]
            else:
                return 'error'
    except:
       return "No internet??"

def downloadWeather():
    with open('/home/pi/2048-Pi-Display/weather.json', 'w') as outfile:
        try:
            resp = requests.get("https://api.openweathermap.org/data/2.5/weather?zip=%s,us&units=imperial&appid=%s" % (weather_zipcode, openweathermap_appid))
            data = resp.json()
            json.dump(data, outfile, indent=4)
            outfile.close()
        except:
           print("No internet??")

def fetchWeather():
    weather_color = graphics.Color(59, 59, 59)
    currentWeather = "???F ????"
    try:
        with open('/home/pi/2048-Pi-Display/weather.json', 'r') as json_file:
            data = json.load(json_file)
            json_file.close()
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

    except:
        currentWeather = "???F ????"

    return (weather_color, currentWeather)


# Main function
if __name__ == "__main__":
    run_text = rPiDisplay()
    if (not run_text.process()):
        run_text.print_help()

