#!/usr/bin/env python3

import cherrypy
from datetime import datetime
import pytz
from weather import Weather
import json


SETTINGS_FILE_DATE_FORMAT = '%Y-%m-%d'

class MissionaryServer(object):
    def __init__(self, settings):
        self._missionary_name = settings['missionary_name']
        self._mission_name = settings['mission_name']
        self._missionary_tz = pytz.timezone(settings['timezone'])
        self._weather = Weather(settings['open_weather_map_key'], settings['location'])
        self._start_date = datetime.strptime(settings['start_date'], SETTINGS_FILE_DATE_FORMAT)
        self._release_date = datetime.strptime(settings['release_date'], SETTINGS_FILE_DATE_FORMAT)

    @property
    def _local_time(self):
        return datetime.now()

    def _mission_time(self, t=None):
        utc_now = pytz.utc.localize(datetime.utcnow() if t == None else t)
        return utc_now.astimezone(self._missionary_tz)

    @cherrypy.expose
    def index(self):
        return "Hello world!"

    @cherrypy.expose
    def missionary_name(self):
        return self._missionary_name

    @cherrypy.expose
    def mission_name(self):
        return self._mission_name

    @cherrypy.expose
    def local_time(self):
        now = self._local_time
        return now.strftime('%I:%M %p').lstrip("0").replace(" 0", " ")

    @cherrypy.expose
    def local_date(self):
        now = self._local_time
        return now.strftime('%a, %b %d, %Y').lstrip("0").replace(" 0", " ")

    @cherrypy.expose
    def mission_time(self):
        pht_now = self._mission_time()
        return pht_now.strftime('%I:%M %p').lstrip("0").replace(" 0", " ")

    @cherrypy.expose
    def mission_date(self):
        pht_now = self._mission_time()
        return pht_now.strftime('%a, %b %d, %Y').lstrip("0").replace(" 0", " ")
    
    @cherrypy.expose
    def mission_temp(self):
        try:
            cc = self._weather.current_conditions()
            temp = '%.1f' % cc['main']['temp']
        except:
            temp = 'unavailable'
        return temp
    
    @cherrypy.expose
    def mission_humidity(self):
        try:
            cc = self._weather.current_conditions()
            humidity = str(cc['main']['humidity'])
        except:
            humidity = 'unavailable'
        return humidity
    
    @cherrypy.expose
    def mission_sunrise(self):
        try:
            cc = self._weather.current_conditions()
            sunrise = int(cc['sys']['sunrise'])
            dt = datetime.fromtimestamp(sunrise, self._missionary_tz)
            sunrise = dt.strftime('%I:%M %p').lstrip("0").replace(" 0", " ")
        except:
            sunrise = 'unavailable'
        return sunrise
    
    @cherrypy.expose
    def mission_sunset(self):
        try:
            cc = self._weather.current_conditions()
            sunset = int(cc['sys']['sunset'])
            dt = datetime.fromtimestamp(sunset, self._missionary_tz)
            sunset = dt.strftime('%I:%M %p').lstrip("0").replace(" 0", " ")
        except:
            sunset = 'unavailable'
        return sunset

    @cherrypy.expose
    def days_served(self):
        duration = datetime.now() - self._start_date
        print(type(duration))
        return str(duration.days)

    @cherrypy.expose
    def days_remaining(self):
        duration = self._release_date - datetime.now()
        print(type(duration))
        return str(duration.days)

if __name__ == '__main__':
    with open('settings.json') as f:
        settings = json.loads(f.read())
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.quickstart(MissionaryServer(settings))
    