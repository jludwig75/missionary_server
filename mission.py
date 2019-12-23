import cherrypy
from datetime import datetime, timedelta
import pytz
from weather import Weather
import timeformat

class Mission(object):
    def __init__(self, settings):
        self._settings = settings

    @property
    def _weather(self):
        return Weather(self._settings.get_setting('open_weather_map_key'), self._settings.get_setting('location'), float(self._settings.get_setting('latitude')), float(self._settings.get_setting('longitude')))

    @property
    def _missionary_tz(self):
        return pytz.timezone(self._settings.get_setting('timezone'))

    def _mission_time(self, t=None):
        utc_now = pytz.utc.localize(datetime.utcnow() if t == None else t)
        return utc_now.astimezone(self._missionary_tz)

    @cherrypy.expose
    def name(self):
        return self._settings.get_setting('mission_name')

    @cherrypy.expose
    def time(self):
        return timeformat.user_time_format(self._mission_time())

    @cherrypy.expose
    def date(self):
        return timeformat.user_date_format(self._mission_time())
    
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
    def conditions(self):
        try:
            cc = self._weather.current_conditions()
            return cc['weather'][0]['description']
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

    @cherrypy.expose
    def center_lat(self):
        return str(self._settings.get_setting('mission_center_lat'))

    @cherrypy.expose
    def center_lon(self):
        return str(self._settings.get_setting('mission_center_lon'))

    @cherrypy.expose
    def map_zoom(self):
        return str(self._settings.get_setting('mission_map_zoom'))

