#!/usr/bin/env python3

import cherrypy
from datetime import datetime
import pytz
from weather import Weather
import json


class MissionaryServer(object):
    def __init__(self, timezone_name, open_weather_map_key, weather_location):
        self._missionary_tz = pytz.timezone(timezone_name)
        self._weather = Weather(open_weather_map_key, weather_location)

    @property
    def _local_time(self):
        return datetime.now()

    @property
    def _pht_time(self):
        utc_now = pytz.utc.localize(datetime.utcnow())
        return utc_now.astimezone(self._missionary_tz)

    @cherrypy.expose
    def index(self):
        return "Hello world!"

    @cherrypy.expose
    def local_time(self):
        now = self._local_time
        return now.strftime('%I:%M %p').lstrip("0").replace(" 0", " ")

    @cherrypy.expose
    def local_date(self):
        now = self._local_time
        return now.strftime('%a, %b %d, %Y').lstrip("0").replace(" 0", " ")

    @cherrypy.expose
    def missionary_time(self):
        pht_now = self._pht_time
        return pht_now.strftime('%I:%M %p').lstrip("0").replace(" 0", " ")

    @cherrypy.expose
    def missionary_date(self):
        pht_now = self._pht_time
        return pht_now.strftime('%a, %b %d, %Y').lstrip("0").replace(" 0", " ")


if __name__ == '__main__':
    with open('settings.json') as f:
        settings = json.loads(f.read())
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.quickstart(MissionaryServer(settings['timezone'], settings['open_weather_app_key'], settings['location']))
    