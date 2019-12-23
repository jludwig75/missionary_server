#!/usr/bin/env python3

import cherrypy
import json
import os
from cherrypy.process.plugins import Daemonizer, PIDFile, DropPrivileges
import argparse
from photo_uploader import PhotoUploader
from local import Local
from mission import Mission
from missionary import Missionary
from slideshow import SlideShow
from settings import Settings

class Root(object):
    def __init__(self, settings):
        self._map_key = settings['maps_api_key']
    @cherrypy.expose
    def index(self):
        with open('index.html') as f:
            text = f.read()
        return text.replace('<<API_KEY>>', self._map_key)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Missionary webserver')
    parser.add_argument('-d', '--daemonize', action='store_true', help='run as a daemon')

    args = parser.parse_args()

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

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
        },
        '/': {
            'tools.sessions.on': True
        }
    }    

    if args.daemonize:
        d = Daemonizer(cherrypy.engine, stderr='/var/log/missionary_server.log')
        d.subscribe()
        PIDFile(cherrypy.engine, '/var/run/missionary_server.pid').subscribe()
        DropPrivileges(cherrypy.engine, uid=1000, gid=1000).subscribe()

    # cherrypy.config.update({'log.screen': False,
    #                         'log.access_file': '',
    #                         'log.error_file': ''})

    settings_obj = Settings('settings.json')
    cherrypy.tree.mount(Root(settings), '/', conf)
    cherrypy.tree.mount(SlideShow('./slides'), '/slideshow', conf)
    cherrypy.tree.mount(Local(settings), '/local')
    cherrypy.tree.mount(Missionary(settings_obj), '/missionary')
    cherrypy.tree.mount(PhotoUploader(os.path.abspath('./slides')), '/photos', conf)
    cherrypy.tree.mount(Settings('settings.json'), '/settings', conf)
    cherrypy.quickstart(Mission(settings), '/mission', conf)
