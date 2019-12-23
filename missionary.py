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
        self._settings = settings

    def _missionary_title(self):
        return 'Elder' if self._settings.get_setting('missionary_gender')[0].upper() == 'M' else 'Sister'

    @cherrypy.expose
    def index(self):
        return "Hello world!"

    @cherrypy.expose
    def name(self, title=None):
        if title == None:
            return self._settings.get_setting('missionary_name')
        return '%s %s' % (self._missionary_title(), self._settings.get_setting('missionary_name'))

    @cherrypy.expose
    def start_date(self):
        return timeformat.user_date_format(timeformat.parse_settings_date_time(self._settings.get_setting('start_date')))

    @cherrypy.expose
    def release_date(self):
        return timeformat.user_date_format(timeformat.parse_settings_date_time(self._settings.get_setting('release_date')))

    @cherrypy.expose
    def days_served(self):
        start_date = timeformat.parse_settings_date_time(self._settings.get_setting('start_date'))
        if datetime.now() < start_date:
            return '0'
        duration = datetime.now() - start_date
        return str(duration.days)

    @cherrypy.expose
    def days_remaining(self):
        release_date = timeformat.parse_settings_date_time(self._settings.get_setting('release_date'))
        if release_date < datetime.now():
            return '0'
        duration = release_date - datetime.now()
        return str(duration.days)

    @cherrypy.expose
    def latitude(self):
        return str(self._settings.get_setting('latitude'))

    @cherrypy.expose
    def longitude(self):
        return str(self._settings.get_setting('longitude'))

    @cherrypy.expose
    def assigned_area(self):
        print('assigned area handler')
        return self._settings.get_setting('current_area')

