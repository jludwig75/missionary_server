#!/usr/bin/env python3

import cherrypy
from datetime import datetime, timedelta
import pytz
from weather import Weather
import json
import os
import random

USER_DATE_FORMAT = '%a, %b %d, %Y'  # Thu, Dec 12, 2019
USER_TIME_FORMAT = '%I:%M %p' # 6:42 AM
SETTINGS_FILE_DATE_FORMAT = '%Y-%m-%d' # 2019-10-30

class Gender:
    Male = 0
    Female = 1

class Test(object):
    @cherrypy.expose
    def message(self):
        return 'hello'


def _user_date_format(dt):
    # remove any leading pad 0's from date
    return dt.strftime(USER_DATE_FORMAT).lstrip("0").replace(" 0", " ")

def _user_time_format(dt):
    # remove any leading pad 0's from time (except after :'s)
    return dt.strftime(USER_TIME_FORMAT).lstrip("0").replace(" 0", " ")

class Local(object):
    def __init__(self, settings):
        pass

    def _local_time(self):
        return datetime.now()

    @cherrypy.expose
    def index(self):
        return "Hello world!"

    @cherrypy.expose
    def time(self):
        return _user_time_format(self._local_time())

    @cherrypy.expose
    def date(self):
        return _user_date_format(self._local_time())

class Missionary(object):
    def __init__(self, settings):
        self._missionary_name = settings['missionary_name']

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

    def _missionary_title(self):
        return 'Elder' if self._gender == Gender.Male else 'Sister'

    @cherrypy.expose
    def index(self):
        return "Hello world!"

    @cherrypy.expose
    def name(self, title=None):
        if title == None:
            return self._missionary_name
        return '%s %s' % (self._missionary_title(), self._missionary_name)

    @cherrypy.expose
    def start_date(self):
        return _user_date_format(self._start_date)

    @cherrypy.expose
    def release_date(self):
        return _user_date_format(self._release_date)

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

class Mission(object):
    def __init__(self, settings):
        self._mission_name = settings['mission_name']
        self._missionary_tz = pytz.timezone(settings['timezone'])
        self._weather = Weather(settings['open_weather_map_key'], settings['location'])

    def _mission_time(self, t=None):
        utc_now = pytz.utc.localize(datetime.utcnow() if t == None else t)
        return utc_now.astimezone(self._missionary_tz)

    @cherrypy.expose
    def index(self):
        return "Hello world!"

    @cherrypy.expose
    def name(self):
        return self._mission_name

    @cherrypy.expose
    def time(self):
        return _user_time_format(self._mission_time())

    @cherrypy.expose
    def date(self):
        return _user_date_format(self._mission_time())
    
    @cherrypy.expose
    def temperature(self):
        try:
            cc = self._weather.current_conditions()
            return '%.1f' % cc['main']['temp']
        except:
            return 'unavailable'
    
    @cherrypy.expose
    def humidity(self):
        try:
            cc = self._weather.current_conditions()
            return str(cc['main']['humidity'])
        except:
            return 'unavailable'
    
    @cherrypy.expose
    def sunrise(self):
        try:
            cc = self._weather.current_conditions()
            sunrise = int(cc['sys']['sunrise'])
            dt = datetime.fromtimestamp(sunrise, self._missionary_tz)
            return dt.strftime('%I:%M %p').lstrip("0").replace(" 0", " ")
        except:
            return 'unavailable'
    
    @cherrypy.expose
    def sunset(self):
        try:
            cc = self._weather.current_conditions()
            sunset = int(cc['sys']['sunset'])
            dt = datetime.fromtimestamp(sunset, self._missionary_tz)
            return dt.strftime('%I:%M %p').lstrip("0").replace(" 0", " ")
        except:
            return 'unavailable'

    @cherrypy.expose
    def time_of_day(self):
        try:
            cc = self._weather.current_conditions()
            sunrise = int(cc['sys']['sunrise'])
            sunset = int(cc['sys']['sunset'])
            now = int(cc['dt'])
            return "Daytime" if now >= sunrise and now <= sunset else "Night"
        except:
            return 'unavailable'

class Root(object):
    def __init__(self, settings):
        self._map_key = settings['maps_api_key']
    @cherrypy.expose
    def index(self):
        with open('index.html') as f:
            text = f.read()
        return text.replace('<<API_KEY>>', self._map_key)

class SlideShow(object):
    def __init__(self, image_dir_path):
        self._image_dir_path = image_dir_path

    @cherrypy.expose
    def next(self):
        file_names = []
        for file_name in os.listdir(self._image_dir_path):
            extension = file_name.split('.')[-1]
            if extension.lower() in ['jpg', 'png']:
                file_names.append('slides/' + file_name)
        return random.choice(file_names)

if __name__ == '__main__':
    with open('settings.json') as f:
        settings = json.loads(f.read())
    cherrypy.server.socket_host = '0.0.0.0'

    conf = {
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.abspath('./public')
        },
        '/slides': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.abspath('./slides')
        }
    }    

    cherrypy.tree.mount(Root(settings), '/', conf)
    cherrypy.tree.mount(SlideShow('./slides'), '/slideshow', conf)
    cherrypy.tree.mount(Local(settings), '/local')
    cherrypy.tree.mount(Missionary(settings), '/missionary')
    cherrypy.quickstart(Mission(settings), '/mission', conf)
