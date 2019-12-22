#!/usr/bin/env python3

import cherrypy
from cherrypy.lib import static


class Settings(object):
    def __init__(self):
        self._field_list = []
        self._add_field('first_name')
        self._add_field('last_name')
        self._add_field('city')
        self._add_field('zip_code')

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
        print('display name', display_name)
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

    def _setup_list(self):
        js = ''
        for field_name in self._field_list:
            js += 'setup_field_form("%s");\n' % field_name
        return js

    @cherrypy.expose
    def index(self):
        cherrypy.session['first_name'] = 'John'
        cherrypy.session['last_name'] = 'Smith'
        cherrypy.session['city'] = 'Provo'
        cherrypy.session['zip_code'] = '84601'
        with open('settings.html') as f:
            html = f.read()
        return html.replace('<<FIELD_LIST>>', self._field_list_html()).replace('<<FORM_SETUP_LIST>>', self._setup_list())

    @cherrypy.expose
    def first_name(self, first_name=None):
        if cherrypy.request.method == 'GET':
            return cherrypy.session['first_name']
        if cherrypy.request.method == 'POST':
            if first_name != None:
                cherrypy.session['first_name'] = first_name

    @cherrypy.expose
    def last_name(self, last_name=None):
        if cherrypy.request.method == 'GET':
            return cherrypy.session['last_name']
        if cherrypy.request.method == 'POST':
            if last_name != None:
                cherrypy.session['last_name'] = last_name

    @cherrypy.expose
    def city(self, city=None):
        if cherrypy.request.method == 'GET':
            return cherrypy.session['city']
        if cherrypy.request.method == 'POST':
            if city != None:
                cherrypy.session['city'] = city

    @cherrypy.expose
    def zip_code(self, zip_code=None):
        if cherrypy.request.method == 'GET':
            return cherrypy.session['zip_code']
        if cherrypy.request.method == 'POST':
            if zip_code != None:
                cherrypy.session['zip_code'] = zip_code

if __name__ == '__main__':
    # CherryPy always starts with app.root when trying to map request URIs
    # to objects, so we need to mount a request handler root. A request
    # to '/' will be mapped to HelloWorld().index().
    conf = {
        '/': {
            'tools.sessions.on': True
        }
    }
    cherrypy.quickstart(Settings(), '/settings', conf)