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
        msg = """
        <html>
            <body>
            <p>%s</p>
            <h2>Upload New Photos</h2>
                <form action="upload" method="post" enctype="multipart/form-data">
                    <input value="Select Photos" type="file" name="myFiles" accept="image/*" multiple/><br />
                    <input value="Upload" type="submit" />
                </form>
                <a href="/">Home</a>
            </body>
        </html>
        """ % upload_message
        if self.UPLOAD_MSG_KEY in cherrypy.session:
            del cherrypy.session[self.UPLOAD_MSG_KEY]
        return msg

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

        cherrypy.session[self.UPLOAD_MSG_KEY] = '%u of %u files successfully uploaded' % (files_sent, files_uploaded)
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