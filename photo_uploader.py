#!/usr/bin/env python3

import os
import os.path

import cherrypy
from cherrypy.lib import static

localDir = os.path.dirname(__file__)
absDir = os.path.join(os.getcwd(), localDir)


class PhotoUploader(object):
    UPLOAD_MSG_KEY = 'upload_message'
    def __init__(self, upload_dir):
        self._upload_dir = upload_dir

    @cherrypy.expose
    def index(self):
        upload_message = cherrypy.session[self.UPLOAD_MSG_KEY] if self.UPLOAD_MSG_KEY in cherrypy.session else ''
        if self.UPLOAD_MSG_KEY in cherrypy.session:
            del cherrypy.session[self.UPLOAD_MSG_KEY]
        with open('photos.html') as f:
            html = f.read()
        return html.replace('<<UPLOAD_MESSAGE>>', upload_message)

    @cherrypy.expose
    def upload(self, myFiles):
        files_sent = len(myFiles)
        files_uploaded = 0

        for myFile in myFiles:
            upload_path = os.path.join(self._upload_dir, myFile.filename)
            with open(upload_path, 'wb') as output_file:
                size = 0
                while True:
                    data = myFile.file.read(8192)
                    if not data:
                        break
                    size += len(data)
                    output_file.write(data)

            files_uploaded += 1

        cherrypy.session[self.UPLOAD_MSG_KEY] = '<p>%u of %u files successfully uploaded</p>' % (files_sent, files_uploaded)
        raise cherrypy.HTTPRedirect(cherrypy.url('.'))

if __name__ == '__main__':
    # CherryPy always starts with app.root when trying to map request URIs
    # to objects, so we need to mount a request handler root. A request
    # to '/' will be mapped to HelloWorld().index().
    conf = {
        '/': {
            'tools.sessions.on': True
        }
    }
    cherrypy.quickstart(PhotoUploader(absDir), '/files', conf)