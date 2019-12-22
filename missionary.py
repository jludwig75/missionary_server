import cherrypy
from datetime import datetime, timedelta
import pytz
from weather import Weather
import timeformat

USER_DATE_FORMAT = '%a, %b %d, %Y'  # Thu, Dec 12, 2019
USER_TIME_FORMAT = '%I:%M %p' # 6:42 AM
SETTINGS_FILE_DATE_FORMAT = '%Y-%m-%d' # 2019-10-30

class Gender:
    Male = 0
    Female = 1

class Missionary(object):
    def __init__(self, settings):
        self._missionary_name = settings['missionary_name']
        self._coords = ((float(settings['latitude']), float(settings['longitude'])))
        self._assigned_area = settings['current_area']

        gender = settings['missionary_gender'].upper()
        if gender == 'M':
            self._gender = Gender.Male
        else:
            assert gender == 'F'
            self._gender = Gender.Female

        try:
            self._start_date = timeformat.format_date_time(settings['start_date'])
        except:
            self._start_date = datetime.now()

        try:
            self._release_date = timeformat.format_date_time(settings['release_date'])
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
        return timeformat.user_date_format(self._start_date)

    @cherrypy.expose
    def release_date(self):
        return timeformat.user_date_format(self._release_date)

    @cherrypy.expose
    def days_served(self):
        print(self._start_date)
        if datetime.now() < self._start_date:
            return '0'
        duration = datetime.now() - self._start_date
        return str(duration.days)

    @cherrypy.expose
    def days_remaining(self):
        print(self._release_date)
        if self._release_date < datetime.now():
            return '0'
        duration = self._release_date - datetime.now()
        return str(duration.days)

    @cherrypy.expose
    def latitude(self):
        return str(self._coords[0])

    @cherrypy.expose
    def longitude(self):
        return str(self._coords[1])

    @cherrypy.expose
    def assigned_area(self):
        return self._assigned_area

