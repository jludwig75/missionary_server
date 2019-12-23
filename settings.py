#!/usr/bin/env python3

import cherrypy
from cherrypy.lib import static
import json
import inspect
from threading import Lock


class Settings(object):
    def __init__(self, settings_file_name):
        self._field_list = []
        self._find_fields()
        self._settings_file_name = settings_file_name
        self._settings = None
        self._settings_lock = Lock()
    
    # call with self._settings_lock held
    def _load_settings(self):
        with open(self._settings_file_name) as f:
            return json.loads(f.read())

    # call with self._settings_lock held
    def _save_settings(self, settings):
        with open(self._settings_file_name, 'wt') as f:
            text = json.dumps(settings)
            text = ',\n"'.join(text.split(', "'))
            f.write(text)

    def _get_setting(self, key):
        with self._settings_lock:
            try:
                settings = self._load_settings()
                if not key in settings:
                    return None
                return settings[key]
            except:
                return None
            
    # implemented as test-and-set
    def _update_setting(self, key, old_value, new_value):
        with self._settings_lock:
            try:
                settings = self._load_settings()
                # Don't allow adding new keys
                if not key in settings or settings[key] != old_value:
                    return False
                settings[key] = new_value
                self._save_settings(settings)
                print('Successfully saved settings')
                return True
            except Exception as e:
                print('Error saving settings: %s' % str(e))
                return False

    def _find_fields(self):
        class_functions = inspect.getmembers(Settings, predicate=inspect.isfunction)
        for function_name, function in class_functions:
            if hasattr(function, 'exposed') and function.exposed and function_name != 'index':#method[0] != 'index' and not method[0].startswith('_'):
                args = inspect.getargspec(function).args
                if len(args) == 2 and args[1] == function_name:
                    self._add_field(function_name)

    def _add_field(self, field_name):
        self._field_list.append(field_name)

    def _field_name_to_display_name(self, field_name):
        display_name = ''
        for c in field_name:
            if c == '_':
                display_name += ' '
            elif len(display_name) == 0 or display_name[-1] == ' ':
                display_name += c.upper()
            else:
                display_name += c
        return display_name

    def _generate_field_form(self, field_name):
        with open('field_form.html') as f:
            html = f.read()
        return html.replace('<<FIELD_NAME>>', field_name).replace('<<DISPLAY_NAME>>', self._field_name_to_display_name(field_name))

    def _field_list_html(self):
        html = ''
        for field_name in self._field_list:
            html += self._generate_field_form(field_name)
        return html

    @cherrypy.expose
    def index(self):
        with open('settings.html') as f:
            html = f.read()
        return html.replace('<<FIELD_LIST>>', self._field_list_html())

    def _setting_get(self, key):
        print(key)
        value = self._get_setting(key)
        cherrypy.session[key] = value
        print(key, value)
        return value

    def _setting_post(self, key, value):
        if value != None:
            print('updating %s to %s' % (key, value))
            if self._update_setting(key, cherrypy.session[key], value):
                cherrypy.session[key] = value

    def _setting_handler(self, key, new_value):
        print(cherrypy.request.method, key, new_value)
        if cherrypy.request.method == 'GET':
            return self._setting_get(key)
        if cherrypy.request.method == 'POST':
            self._setting_post(key, new_value)

    @cherrypy.expose
    def missionary_name(self, missionary_name=None):
        return self._setting_handler('missionary_name', missionary_name)

    @cherrypy.expose
    def missionary_gender(self, missionary_gender=None):
        return self._setting_handler('missionary_gender', missionary_gender)

    @cherrypy.expose
    def current_area(self, current_area=None):
        return self._setting_handler('current_area', current_area)

    @cherrypy.expose
    def current_area_latitude(self, current_area_latitude=None):
        return self._setting_handler('latitude', current_area_latitude)

    @cherrypy.expose
    def current_area_longitude(self, current_area_longitude=None):
        return self._setting_handler('longitude', current_area_longitude)

    @cherrypy.expose
    def mission_map_zoom_level(self, mission_map_zoom_level=None):
        return self._setting_handler('mission_map_zoom', mission_map_zoom_level)

    @cherrypy.expose
    def timezone(self, timezone=None):
        return self._setting_handler('timezone', timezone)

    @cherrypy.expose
    def weather_location(self, weather_location=None):
        return self._setting_handler('location', weather_location)

    @cherrypy.expose
    def start_date(self, start_date=None):
        return self._setting_handler('start_date', start_date)

    @cherrypy.expose
    def release_date(self, release_date=None):
        return self._setting_handler('release_date', release_date)

    @cherrypy.expose
    def mission_name(self, mission_name=None):
        return self._setting_handler('mission_name', mission_name)

    @cherrypy.expose
    def open_weather_map_key(self, open_weather_map_key=None):
        return self._setting_handler('open_weather_map_key', open_weather_map_key)

    @cherrypy.expose
    def google_maps_api_key(self, google_maps_api_key=None):
        return self._setting_handler('maps_api_key', google_maps_api_key)

    @cherrypy.expose
    def mission_center_latitude(self, mission_center_latitude=None):
        return self._setting_handler('mission_center_lat', mission_center_latitude)

    @cherrypy.expose
    def mission_center_longitude(self, mission_center_longitude=None):
        return self._setting_handler('mission_center_lon', mission_center_longitude)

    def get_setting(self, key):
        with self._settings_lock:
            settings = self._load_settings()
            if not key in settings:
                return None
            return settings[key]

if __name__ == '__main__':
    # CherryPy always starts with app.root when trying to map request URIs
    # to objects, so we need to mount a request handler root. A request
    # to '/' will be mapped to HelloWorld().index().
    conf = {
        '/': {
            'tools.sessions.on': True
        }
    }
    cherrypy.quickstart(Settings('settings.json'), '/settings', conf)