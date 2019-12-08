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

class rPiDisplay(DisplayBase):

    def __init__(self, *args, **kwargs):
        super(rPiDisplay, self).__init__(*args, **kwargs)

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("/home/pi/2048-Pi-Display/fonts/4x6.bdf")
        textColor = graphics.Color(59, 59, 59)
        pos = offscreen_canvas.width

        self.matrix.brightness = 70
       
        iteration = 0
        currentWeather = '0F '
        wotd = ''
        currentTrack = ''
        image = None
        is_playing = False
        weather_color = graphics.Color(59, 59, 59)

        sent_ipaddress = False
        while True:

            if sent_ipaddress == False and iteration % 100 == 0:
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
            graphics.DrawText(offscreen_canvas, font, 0, 6, clock_color, concocted_str)
            graphics.DrawLine(offscreen_canvas, 0, 7, 31, 7, graphics.Color(59, 59, 59))

            #Draw Day
            graphics.DrawText(offscreen_canvas, font, 0, 14, day_color, day)
            graphics.DrawLine(offscreen_canvas, 0, 15, 31, 15, graphics.Color(59, 59, 59))

            if iteration % 100 == 0:
                resp = fetchWeather()
                weather_color = resp[0]
                currentWeather = resp[1]

            #Draw weather
            graphics.DrawText(offscreen_canvas, font, 0, 22, weather_color, currentWeather)

            if iteration % 100 == 0:
                pos = 10
                resp = fetchSpotify()
                is_playing = resp[0]
                image = resp[1]
                currentTrack = resp[2]

            if iteration % 1000 == 0:
                wotd = fetchUrbanWOTD()


            if is_playing:
                graphics.DrawLine(offscreen_canvas, 0, 23, 31, 23, graphics.Color(0, 99, 0))
                len = graphics.DrawText(offscreen_canvas, font, pos, 30, graphics.Color(0, 99, 0), currentTrack)
                pos -= 1
                if (pos + len < 10):
                    pos = offscreen_canvas.width
                if image is not None:
                    offscreen_canvas.SetImage(image, offset_y=23)
            else:
                # Draw Urban Dictionary WOTD
                graphics.DrawLine(offscreen_canvas, 0, 23, 31, 23, graphics.Color(59, 59, 59))
                len = graphics.DrawText(offscreen_canvas, font, pos, 30, textColor, wotd)
                pos -= 1
                if (pos + len < 0):
                    pos = offscreen_canvas.width

            
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
            iteration += 1
            time.sleep(0.1)

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
    concocted_str = "%s:%s" % (hour, t_string)

    day_color = graphics.Color(59, 59, 59)
    day = d_aware.strftime("%A").upper()
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

    return (concocted_str, clock_color, day_color, day)

def downloadSpotify():
    with open('/home/pi/2048-Pi-Display/spotify.json', 'w') as outfile:
        token = util.prompt_for_user_token("jc8a1vumj4nofex2isggs9uur","user-read-currently-playing", client_id='a362ed228f6f42dda29df88594deacf9',client_secret='55924005c1a04aaca88d5a8e3dd39653',redirect_uri='https://callback/')
        sp = Spotify(auth=token)
        result = sp.current_user_playing_track()
        if result is not None:
            if result["item"]["name"] != '':
                try:
                    resp = requests.get(result["item"]["album"]["images"][0]["url"])
                    image_file = io.BytesIO(resp.content)
                    with open('/home/pi/2048-Pi-Display/spotify_image.jpeg', 'w') as imagefile:
                        imagefile.write(resp.content)
                except:
                    print("Couldn't fetch image")
            json.dump(result, outfile, indent=4)
            

def fetchSpotify():
    is_playing = False
    image = None
    currentTrack = ''

    t = Thread(target=downloadSpotify)
    t.start()

    with open('/home/pi/2048-Pi-Display/spotify.json', 'r') as json_file:
        print(json_file)
        result = json.load(json_file)
        if result is not None and "is_playing" in result:
            is_playing = result["is_playing"]
            if currentTrack != result["item"]["name"] and result["item"]["name"] != '':
                currentTrack = result["item"]["name"]
        image = Image.open('/home/pi/2048-Pi-Display/spotify_image.jpeg').convert('RGB')
        image.thumbnail((9, 9), Image.ANTIALIAS)

    return (is_playing, image, currentTrack)
        
def fetchUrbanWOTD():
    try:
        resp = requests.get("http://urban-word-of-the-day.herokuapp.com/today")
        data = resp.json()
        if data is not None:
           return data["word"]
        else:
            return 'error'
    except:
       return "No internet??"

def fetchWeather():
    weather_color = graphics.Color(59, 59, 59)
    currentWeather = "???F ????"
    try:
        resp = requests.get("https://api.openweathermap.org/data/2.5/weather?zip=%s,us&units=imperial&appid=%s" % (weather_zipcode, openweathermap_appid))
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
    except:
        currentWeather = "???F ????"

    return (weather_color, currentWeather)


# Main function
if __name__ == "__main__":
    run_text = rPiDisplay()
    if (not run_text.process()):
        run_text.print_help()

