#!/usr/bin/env python3
import base64
import datetime
import io
import os
import random
import re
from pathlib import Path

import astral
import pytz
import requests
from astral import moon, sun
from openai import OpenAI
from PIL import Image, ImageOps

CURRENT_DIRECTORY = Path(__file__).parent
SETTINGS = {
    "mountains": "snow-capped mountains",
    "lake": "a lake surrounded by trees",
    "forest": "a dense forest",
    "meadow": "a meadow with wildflowers",
    "beach": "a beach with soft, white sand",
    "river": "a river flowing through the countryside",
    "garden": "a well-kept garden",
    "waterfall": "a waterfall in a tropical setting",
    "island": "a secluded island with clear blue waters",
    "canyon": "a vast canyon with a stunning view",
}


def slugify(text):
    return re.sub(r"([ \:\d\%/\-]+)", "-", text.lower()).strip("-")


def generate_image(prompt):
    client = OpenAI()

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        response_format="b64_json",
    )

    return base64.b64decode(response.data[0].b64_json)


def get_weather():
    r = requests.get(
        "https://api.openweathermap.org/data/3.0/onecall?lat=40.597215"
        f"&lon=22.950262&appid={os.getenv('OPENWEATHER_API_KEY')}"
        "&exclude=minutely,daily,hourly,alerts&units=metric"
    )
    return r.json()


def get_time_of_day():
    city = astral.LocationInfo("Thessaloniki", "Greece", "Europe/Athens", 40.6, 23)
    now = datetime.datetime.now(pytz.timezone(city.timezone))
    if (
        astral.sun.twilight(
            city.observer, tzinfo=city.timezone, direction=astral.SunDirection.RISING
        )[0]
        < now
        <= astral.sun.twilight(
            city.observer, tzinfo=city.timezone, direction=astral.SunDirection.RISING
        )[1]
    ):
        return "sunrise"
    elif (
        astral.sun.twilight(
            city.observer, tzinfo=city.timezone, direction=astral.SunDirection.SETTING
        )[0]
        < now
        <= astral.sun.twilight(
            city.observer, tzinfo=city.timezone, direction=astral.SunDirection.SETTING
        )[1]
    ):
        return "sunset"
    elif (
        astral.sun.daylight(city.observer, tzinfo=city.timezone)[0]
        < now
        <= astral.sun.daylight(city.observer, tzinfo=city.timezone)[1]
    ):
        return "day"
    else:
        # We're between two days, which means night.
        return "night"


def get_moon_phase():
    # We don't use this because DALL-E always returns a prominent full moon if we do.
    phase = astral.moon.phase()
    if phase < 7:
        return "new"
    elif phase < 14:
        return "waxing"
    elif phase < 21:
        return "full"
    else:
        return "waning"


def main():
    setting = random.choice(list(SETTINGS.keys()))

    weather = get_weather()["current"]["weather"][0]
    season = ["autumn", "winter", "spring", "summer"][
        (datetime.date.today().month // 3 + 1) % 4
    ]

    time_of_day = get_time_of_day()

    filename = f"{setting}-{season}-{slugify(time_of_day)}-{weather['description'].replace(' ', '-').replace('/', '-')}.jpg"
    path = CURRENT_DIRECTORY / "image_cache" / filename

    prompt = f"A calm, relaxing painting by Albert Bierstadt, of {SETTINGS[setting]} in the {season}, at {time_of_day}, with weather: {weather['description']}"
    print(prompt)

    if path.exists():
        print("Image already exists.")
    else:
        print("Generating image...")
        image = Image.open(io.BytesIO(generate_image(prompt)))
        image.save(path, "JPEG")

    image = Image.open(path)
    image = ImageOps.fit(image, (800, 480))
    image.show()


if __name__ == "__main__":
    main()