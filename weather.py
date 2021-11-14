from io import StringIO
from datetime import datetime, timedelta
import logging

import requests
from lxml import etree


def get_weather_direct(): 
    # Straight from the website itself
    url = "http://www.meteo.lt/lt/miestas?placeCode=Vilnius"
    # Or you can use "temperature" for shown temps          here  ---v
    path = './/div[contains(@class, "weather_info")]//span[@class="feelLike"]/text()'

    data = None
    while True:
        try:
            data = requests.get(url)
        except requests.exceptions.ConnectionError:
            time.sleep(10)
        if not data.ok:
            time.sleep(10)
        else:
            break

    html = data.content.decode("utf-8")
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(html), parser=parser)

    temperature = tree.xpath(path)[0]
    return float(temperature)

def get_weather():
    # Straight from the API, haas issues with current weather.
    url = 'https://api.meteo.lt/v1/places/vilnius/forecasts/long-term'
    weather_req = requests.get(url)
    rel_fcs = {}
    if weather_req.ok:
        data = weather_req.json()
        time = datetime.now()

        rel_fcs = []  # Relevant forecasts
        for entry in data['forecastTimestamps']:
            fc_time = datetime.strptime(entry['forecastTimeUtc'],
                                        '%Y-%m-%d %H:%M:%S')

            time_previous = time - timedelta(hours=12)
            time_future = time + timedelta(hours=12)
            if time_previous <= fc_time <= time_future:
                time_diff = abs(int((time - fc_time).total_seconds()))
                rel_entry = {
                    'fc_time': fc_time,
                    'time_diff': time_diff,
                    'temp': float(entry['airTemperature'])
                }
                rel_fcs.append(rel_entry)
    return rel_fcs

class Weather(object):
    def __init__(self, scheduler):
        self.temp_cur = None
        self.temp_min = None
        self.temp_max = None

        self.update()

        # Update weather every 15 minutes
        scheduler.add_job(self.update, 'cron', minute='*/15')

    def update(self):
        logging.info("Updating weather")

        try:
            self.temp_now = get_weather_direct()
            self.temp_min = None
            self.temp_max = None
            logging.debug("Got weather info: %s", self.temp_now)

            # rel_fcs = get_weather()
            # self.temp_now = min(rel_fcs, key=lambda x: x['time_diff'])['temp']
            # self.temp_min = min(rel_fcs, key=lambda x: x['temp'])['temp']
            # self.temp_max = max(rel_fcs, key=lambda x: x['temp'])['temp']
        except Exception as exc:
            logging.error("Could not get weather: %s", exc, exc_info=True)
