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

color_map = [
[255, 0, 0],
[255, 30, 0],
[255, 60, 0],
[255, 90, 0],
[255, 112, 0],
[255, 150, 0],
[255, 190, 0],
[255, 220, 0],
[255, 241, 0],
[200, 243, 0],
[120, 246, 0],
[50, 250, 0],
[0, 255, 0],
[0, 255, 50],
[0, 255, 150],
[0, 255, 200],
[0, 255, 255],
[0, 200, 255],
[0, 120, 255],
[0, 50, 255],
[0, 0, 255],
[50, 0, 255],
[120, 0, 255],
[200, 0, 255],
[255, 0, 255],
[220, 20, 160],
[200, 40, 80],
[170, 60, 40],
[147, 81, 0],
[83, 47, 25],
[121, 121, 121],
[66, 66, 66],
]

# [ x, y, horizontal or vertical, current-step ]
pong_beam_coords = []
move_coords = []

class rPiDisplay(DisplayBase):

    def __init__(self, *args, **kwargs):
        super(rPiDisplay, self).__init__(*args, **kwargs)

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("/home/pi/2048-Pi-Display/fonts/4x6.bdf")
        textColor = graphics.Color(59, 59, 59)
        pos = offscreen_canvas.width

        weather_pos = 0
        feels_pos = 40

        self.matrix.brightness = 100

        iteration = 0
        currentWeather = '0F '
        feelsWeather = '0f '
        wotd = 'Good Morning...'
        currentTrack = ''
        image = None
        is_playing = False
        weather_color = graphics.Color(59, 59, 59)
        spotify_color = graphics.Color(0, 99, 0)
        sent_ipaddress = False
        block_fill = False
        black_color = graphics.Color(255, 255, 255)

        current_song_ms = 0
        duration_song_ms = 0

        new_image = None
        old_image = None
        currentStep = 0

        rain_coords = []
        pong_coord = [1, 1]
        pong_coords = [[1, 1]]
        pong_xDir = 1
        pong_yDir = -1

        joke_file = open('/home/pi/2048-Pi-Display/jokes.txt', "r")
        jokes = joke_file.read().splitlines()
        joke_file.close()        
        joke = ''
        jokePunchline = ''
        def setJoke():
            jokes.shuffle()
            parts = jokes[0].split('<>')
            joke = parts[0]
            jokePunchline = parts[1]
        setJoke()
        
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
                for index in range(0, len(pong_coords)):
                    if is_playing:

                        def clamp(minvalue, value, maxvalue):
                            return max(minvalue, min(value, maxvalue))

                        use_color = color_map[index]
                        play_progress = int(round(32 * (float(current_song_ms) / float(duration_song_ms))) - 1)
     
                        if index > play_progress:
                            use_color = [255, 255, 255]
                        else:
                            offscreen_canvas.SetPixel(pong_coords[index][0], pong_coords[index][1] + 8, use_color[0], use_color[1], use_color[2])

                    else:
                        offscreen_canvas.SetPixel(pong_coords[index][0], pong_coords[index][1] + 8, color_map[index][0], color_map[index][1], color_map[index][2])

                pong_result = pongPosition(pong_coords[0], pong_xDir, pong_yDir, is_playing)
                
                pong_coords.insert(0, pong_coord)
                pong_coords = pong_coords[:32]
                
                pong_coord = pong_result[0]
                pong_xDir = pong_result[1]
                pong_yDir = pong_result[2]


            if iteration % 50 == 0:
                resp = fetchWeather()
                weather_color = resp[0]
                currentWeather = resp[1]
                feelsWeather = resp[2]

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

                graphics.DrawText(offscreen_canvas, font, weather_pos, 22, weather_color, currentWeather)
                #graphics.DrawText(offscreen_canvas, font, feels_pos, 22, graphics.Color(92, 31, 199), feelsWeather)
                #weather_pos -= 1
                #feels_pos -= 1
                #if weather_pos <= -40:
                #    weather_pos = 40
                #if feels_pos <= -40:
                #    feels_pos = 40



                

            if iteration % 50 == 0:
                resp = fetchSpotify()
                is_playing = resp[0]
                if resp[3] is not None:
                    current_song_ms = int(resp[3])
                if resp[4] is not None:
                    duration_song_ms = int(resp[4])
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
                leng = graphics.DrawText(offscreen_canvas, font, pos, 30, textColor, joke)
                punchlineLeng = graphics.DrawText(offscreen_canvas, font, pos + leng + 1, 30, graphics.Color(255, 119, 255), jokePunchline)
                pos -= 1
                if (pos + leng + punchlineLeng + 1 < 0):
                    pos = offscreen_canvas.width
                    # New Joke
                    setJoke()

            if iteration % 1 == 0:
                for index in range(0, len(pong_coords)):
                    if is_playing:

                        def clamp(minvalue, value, maxvalue):
                            return max(minvalue, min(value, maxvalue))

                        use_color = color_map[index]
                        play_progress = int(round(32 * (float(current_song_ms) / float(duration_song_ms))) - 1)
     
                        if index > play_progress:
                            use_color = [255, 255, 255]

                        offscreen_canvas.SetPixel(pong_coords[index][0], pong_coords[index][1] + 8, use_color[0], use_color[1], use_color[2])
                    else:
                        offscreen_canvas.SetPixel(pong_coords[index][0], pong_coords[index][1] + 8, color_map[index][0], color_map[index][1], color_map[index][2])

                pong_result = pongPosition(pong_coords[0], pong_xDir, pong_yDir, is_playing)
                
                pong_coords.insert(0, pong_coord)
                pong_coords = pong_coords[:32]
                
                pong_coord = pong_result[0]
                pong_xDir = pong_result[1]
                pong_yDir = pong_result[2]


                # Draw the beams
                for bindex in range(0, len(pong_beam_coords)):
                    if bindex >= len(pong_beam_coords):
                        continue


                    if pong_beam_coords[bindex][3] > 32:
                        coords = [pong_beam_coords[bindex][0], pong_beam_coords[bindex][1] - 8]
                        del pong_beam_coords[bindex]
                        del move_coords[move_coords.index(coords)]
                        continue
                    # [ x, y, horizontal or vertical, current-step, color ]
                    topxpos = pong_beam_coords[bindex][0]
                    topypos = pong_beam_coords[bindex][1]

                    bottomxpos = pong_beam_coords[bindex][0]
                    bottomypos = pong_beam_coords[bindex][1]

                    if pong_beam_coords[bindex][2] > 0:
                        topxpos += pong_beam_coords[bindex][3]
                        bottomxpos -= pong_beam_coords[bindex][3]
                    else:
                        topypos += pong_beam_coords[bindex][3]
                        bottomypos -= pong_beam_coords[bindex][3]

                    color_index = pong_beam_coords[bindex][3]

                    def safe_color(colori, index):
                        useic = colori
                        if colori >= len(color_map) - 1:
                            useic -= len(color_map) - 1
                            if useic < 0:
                                useic = 0
                        return color_map[useic][index]

                    for i in range(0, 3):
                        if pong_beam_coords[bindex][2] > 0:
                            # Horizontal

                            offscreen_canvas.SetPixel(topxpos - i, topypos, safe_color(color_index + i, 0), safe_color(color_index + i, 1), safe_color(color_index + i, 2))
                            offscreen_canvas.SetPixel(bottomxpos + i, bottomypos, safe_color(color_index + i, 0), safe_color(color_index + i, 1), safe_color(color_index + i, 2))
                        else:
                            # Vertical
                            if topypos + i < 23:
                                offscreen_canvas.SetPixel(topxpos, topypos + i, safe_color(color_index + i, 0), safe_color(color_index + i, 1), safe_color(color_index + i, 2))
                            
                            offscreen_canvas.SetPixel(bottomxpos, bottomypos - i, safe_color(color_index + i, 0), safe_color(color_index + i, 1), safe_color(color_index + i, 2))
            
                    # Interate step
                    pong_beam_coords[bindex][3] += 1

            
            iteration += 1

            today = datetime.datetime.today()
            timezone = pytz.timezone("America/New_York")
            d_aware = timezone.localize(today)

            hour = int(d_aware.strftime("%H"))

            # Ryan Priscilla Valentines Day
            #if True:
            '''
            offscreen_canvas.Clear()
            heart_image = Image.open("/home/pi/2048-Pi-Display/images/heart.png").convert('RGB')
            heart_image.thumbnail((32, 32), Image.ANTIALIAS)
            offscreen_canvas.SetImage(heart_image)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
            self.matrix.brightness = 70
            time.sleep(0.5)
            '''
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
            current_song_ms += 100


            
            #print(current_song_ms)
            #print(duration_song_ms)
            #print(current_song_ms / duration_song_ms)

# Direction +1 (Up, Right) or -1 (Down, Left)
def pongPosition(lastCoord, xDir, yDir, is_playing):
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
    if newCoord[1] < -8 or newCoord[1] > 14:
        new_yDir = -new_yDir
        if lastCoord not in move_coords:
            pong_beam_coords.append([lastCoord[0], lastCoord[1] + 8, 1, 1])
            move_coords.append(lastCoord)

    # Outside horizontal bounds 31
    if newCoord[0] < 0 or newCoord[0] > 31:
        new_xDir = -new_xDir

        if lastCoord not in move_coords:
            pong_beam_coords.append([lastCoord[0], lastCoord[1] + 8, -1, 1])
            move_coords.append(lastCoord)



    #if is_playing:
        # 0 - 7 h 17 - 23
        #def inAlbumArt(coord):
        #    return coord[0] >= 0 and coord[0] <= 8 and coord[1] >= 15 and coord[1] <= 23

        #if inAlbumArt(newCoord):
        #    if newCoord[1] == 15:
        #        new_yDir = -new_yDir
        #    else:
        #        new_xDir = -new_xDir

    # Top Left Corner
    #if lastCoord == [1,-7]:
    #    return (randomOffset(31, 6), xDir, yDir)
    # Top Right Corner
    #if lastCoord == [31,-7]:
    #    return (randomOffset(31, 6), xDir, yDir)
    # Bottom Left Corner
    #if lastCoord == [1,6]:
    #    return (randomOffset(31, 6), xDir, yDir)
    # Bottom Right Corner
    #if lastCoord == [31,6]:
    #    return (randomOffset(31, 6), xDir, yDir)

    if new_xDir != xDir or new_yDir != yDir:
        return pongPosition(lastCoord, new_xDir, new_yDir, is_playing)

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
            #print('Nope!')
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
    current_dur = 0
    whole_dur = 0

    with open('/home/pi/2048-Pi-Display/spotify.json', 'r') as json_file:
        try:
            result = json.load(json_file)
            json_file.close()
            if result is not None and "is_playing" in result:
                is_playing = result["is_playing"]
                if currentTrack != result["item"]["name"] and result["item"]["name"] != '':
                    currentTrack = result["item"]["name"]

                current_dur = result["progress_ms"]
                whole_dur = result["item"]["duration_ms"]
                #print(current_dur)
                #print(whole_dur)
            image = Image.open('/home/pi/2048-Pi-Display/spotify_image.jpeg').convert('RGB')
            
            #image.thumbnail((32, 32), Image.ANTIALIAS)
        except:
            print("Couldn't open image file")

    return (is_playing, image, currentTrack, current_dur, whole_dur)
        

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
    feelsWeather = "???F ????"
    try:
        with open('/home/pi/2048-Pi-Display/weather.json', 'r') as json_file:
            data = json.load(json_file)
            json_file.close()

            currentTemp = int(data["main"]["temp"])
            
            feelsTemp = int(data["main"]["feels_like"])
            feelsWeather = "FEELS %sF"  % (feelsTemp)

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
        feelsWeather = "???F ????"

    return (weather_color, currentWeather, feelsWeather)


# Main function
if __name__ == "__main__":
    run_text = rPiDisplay()
    if (not run_text.process()):
        run_text.print_help()

