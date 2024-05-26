#!/usr/bin/env python
import os
import sys
import time
import traceback

from PIL.Image import Transpose
from PIL import Image
from PIL import ImageDraw, ImageOps, ImageEnhance
from waveshare_epd import epd7in3f

palette = [
    0,
    0,
    0,  # Color 1: black
    255,
    0,
    0,  # Color 2: red
    0,
    255,
    0,  # Color 3: green
    0,
    0,
    255,  # Color 4: blue
    255,
    255,
    0,  # Color 5: yellow
    255,
    128,
    0,  # Color 6: orange
    255,
    255,
    255,  # Color 7: white
]

image = Image.open(sys.argv[1])
image = ImageOps.fit(image, (800, 480))

brightness = float(sys.argv[2])
if brightness > 1:
    image = ImageEnhance.Contrast(image).enhance(1 / brightness)
    image = ImageEnhance.Brightness(image).enhance(brightness)

# Create a new image using the palette
palette_image = Image.new("P", (1, 1))
palette_image.putpalette(
    palette * int(256 / len(palette)) + palette[: 3 * (256 % len(palette))]
)

im = image.quantize(palette=palette_image, dither=Image.Dither.FLOYDSTEINBERG)
im = im.transpose(Transpose.ROTATE_180)

try:
    epd = epd7in3f.EPD()
    epd.init()
    epd.Clear()

    epd.display(epd.getbuffer(im))
    time.sleep(3)

    epd.sleep()
except IOError as e:
    print(e)
except KeyboardInterrupt:
    epd7in3f.epdconfig.module_exit(cleanup=True)
    exit()
