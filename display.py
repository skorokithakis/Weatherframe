#!/usr/bin/env python
import argparse
import os
import sys
import time
import traceback

from PIL.Image import Transpose
from PIL import Image
from PIL import ImageDraw, ImageOps, ImageEnhance
from waveshare_epd import epd7in3f


def display(path, brightness, method="fit"):
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

    image = Image.open(path)
    if method == "fit":
        image = ImageOps.fit(image, (800, 480))
    elif method == "pad":
        image = ImageOps.pad(image, (800, 480), color=(255, 255, 255))

    image = image.convert("RGB")

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
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process an image file.")
    parser.add_argument("filename", type=str, help="Path to the image file")
    parser.add_argument(
        "--brightness", type=float, default=1, help="Adjust the brightness level"
    )
    parser.add_argument(
        "--method", type=str, default="fit", help="Method for processing the image"
    )

    args = parser.parse_args()

    print("Showing image...")
    display(args.filename, args.brightness, args.method)
