#!/usr/bin/env python3

import cherrypy
from datetime import datetime, timedelta
import pytz
from weather import Weather
import json

USER_DATE_FORMAT = '%a, %b %d, %Y'  # Thu, Dec 12, 2019
USER_TIME_FORMAT = '%I:%M %p' # 6:42 AM
SETTINGS_FILE_DATE_FORMAT = '%Y-%m-%d' # 2019-10-30

class Gender:
    Male = 0
    Female = 1

class MissionaryServer(object):
    def __init__(self, settings):
        self._missionary_name = settings['missionary_name']
        self._mission_name = settings['mission_name']
        self._missionary_tz = pytz.timezone(settings['timezone'])
        self._weather = Weather(settings['open_weather_map_key'], settings['location'])

        gender = settings['missionary_gender'].upper()
        if gender == 'M':
            self._gender = Gender.Male
        else:
            assert gender == 'F'
            self._gender = Gender.Female

        try:
            self._start_date = datetime.strptime(settings['start_date'], SETTINGS_FILE_DATE_FORMAT)
        except:
            self._start_date = datetime.now()

        try:
            self._release_date = datetime.strptime(settings['release_date'], SETTINGS_FILE_DATE_FORMAT)
        except:
            days = 2 * 365 if self._gender == Gender.Male else 365 + 365 / 2
            self._release_date = self._start_date + timedelta(days=days)

    def _local_time(self):
        return datetime.now()

    def _mission_time(self, t=None):
        utc_now = pytz.utc.localize(datetime.utcnow() if t == None else t)
        return utc_now.astimezone(self._missionary_tz)

    def _user_date_format(self, dt):
        # remove any leading pad 0's from date
        return dt.strftime(USER_DATE_FORMAT).lstrip("0").replace(" 0", " ")

    def _user_time_format(self, dt):
        # remove any leading pad 0's from time (except after :'s)
        return dt.strftime(USER_TIME_FORMAT).lstrip("0").replace(" 0", " ")

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
        return self._user_time_format(self._local_time())

    @cherrypy.expose
    def local_date(self):
        return self._user_date_format(self._local_time())

    @cherrypy.expose
    def mission_time(self):
        return self._user_time_format(self._mission_time())

    @cherrypy.expose
    def mission_date(self):
        return self._user_date_format(self._mission_time())
    
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
    def start_date(self):
        return self._user_date_format(self._start_date)

    @cherrypy.expose
    def release_date(self):
        return self._user_date_format(self._release_date)

    @cherrypy.expose
    def days_served(self):
        if datetime.now() < self._start_date:
            return '0'
        duration = datetime.now() - self._start_date
        print(type(duration))
        return str(duration.days)

    @cherrypy.expose
    def days_remaining(self):
        if self._release_date < datetime.now():
            return '0'
        duration = self._release_date - datetime.now()
        print(type(duration))
        return str(duration.days)

if __name__ == '__main__':
    with open('settings.json') as f:
        settings = json.loads(f.read())
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.quickstart(MissionaryServer(settings))
    