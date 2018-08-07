# import dependencies

import colorsys
import signal
import time
from sys import exit

import requests
import unicornhathd
import datetime as dt
import time


def next_bus(stop_point):
    """
    Fruitful function that draws data from the TFL Unified API relating to a London bus route
    and returns a list of soon-to-arrive buses with destinations and time to arrival in rounded minutes.
    input: the bus stop point ID (obtainable from the TFL Unified API), as a string
    output: list of strings relating to bus destinations and time to arrive in rounded minutes
    """
    stop = str(stop_point)
    r = requests.get('https://api-radon.tfl.gov.uk/StopPoint/' + stop_point + '/Arrivals')
    print(r)
    json_result = r.json()
    all_stops = json_result
    my_buses = []
    for i in all_stops:
        i = '{}, {}-min'.format(str(i['destinationName']),str(round(i['timeToStation']/60)))
        my_buses.append(i)
    return my_buses

while True:
    """
    Until told to stop, this script continues to draw down data from the TFL API
    every fifteen seconds. In this case, we make two calls to our next_bus function
    one for the southbound buses and one for the northbound buses.
    """
    try:
        southbound = next_bus('490008258S')
        southbound = str.join(', ', southbound)
        northbound = next_bus('490008258W')
        northbound = str.join(', ', northbound)
    except:
        southbound = 'TFail'
        northbound = 'TFail'

    time.sleep(15)


"""
Code from this point forward is based on example code provided by Pimoroni
for the UnicornHat HD led unit for the Raspberry Pi, and acknowledgements and intellectual
property is theirs via MIT Licence.  I have amended it sufficiently for the purposes
of this project.

Full code available here: https://github.com/pimoroni/unicorn-hat-hd

Those using a different display device will wish to excise this code
and pass the results of the above functions to alternative code via a forked script
"""

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    exit("This script requires the pillow module\nInstall with: sudo pip install pillow")

lines = [southbound, northbound]

colours = [tuple([int(n * 255) for n in colorsys.hsv_to_rgb(x/float(len(lines)), 1.0, 1.0)]) for x in range(len(lines))]

FONT = ("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", 12)

# Set rotation and brightness

unicornhathd.rotation(0)
unicornhathd.brightness(1.0)

width, height = unicornhathd.get_shape()

text_x = width
text_y = 2

font_file, font_size = FONT

font = ImageFont.truetype(font_file, font_size)

text_width, text_height = width, 0

for line in lines:
    w, h = font.getsize(line)
    text_width += w + width
    text_height = max(text_height,h)

text_width += width + text_x + 1

image = Image.new("RGB", (text_width,max(16, text_height)), (0,0,0))
draw = ImageDraw.Draw(image)

offset_left = 0

for index, line in enumerate(lines):
    draw.text((text_x + offset_left, text_y), line, colours[index], font=font)

    offset_left += font.getsize(line)[0] + width

for scroll in range(text_width - width):
    for x in range(width):
        for y in range(height):
            pixel = image.getpixel((x+scroll, y))
            r, g, b = [int(n) for n in pixel]
            unicornhathd.set_pixel(width-1-x, y, r, g, b)

    unicornhathd.show()
    time.sleep(0.01)

unicornhathd.off()
