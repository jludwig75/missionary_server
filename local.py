import cherrypy
from datetime import datetime
import timeformat


class Local(object):
    def _local_time(self):
        return datetime.now()

    @cherrypy.expose
    def index(self):
        return "Hello world!"

    @cherrypy.expose
    def time(self):
        return timeformat.user_time_format(self._local_time())

    @cherrypy.expose
    def date(self):
        return timeformat.user_date_format(self._local_time())

