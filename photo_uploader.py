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

    def _splitext(self, path):
        name_parts = path.split('.')
        return '.'.join(name_parts[:-1]), name_parts[-1]

    _IMAGE_FILE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'tif', 'tiff']
    def _generate_image_list(self):
        image_list = []
        for file_name in os.listdir(self._upload_dir):
            filename, extension = self._splitext(file_name)
            if extension.lower() in self._IMAGE_FILE_EXTENSIONS:
                thumbnail_name = '%s_thumb.%s' % (filename, extension)
                thumbnail_path = os.path.join(self._upload_dir, 'thumbnails', thumbnail_name)
                if os.path.exists(thumbnail_path):
                    image_list.append(((file_name, thumbnail_name)))
        return image_list
                
    def _generate_image_selection_list(self, image_list):
        list_html = ''
        first_element = True
        for image in image_list:
            list_html += '<img id="%s" class="thumbnail%s" src="slides/thumbnails/%s" data-image-path="%s">' % (image[0].split('.')[0], ' thumbnail_selected' if first_element else '', image[1], image[0])
            first_element = False
        return list_html

    def _get_image_list_index(self, image_file_name):
        image_list_length = len(cherrypy.session[self.IMAGE_LIST_KEY])
        if image_list_length == 0:
            return -1
        print(image_file_name)
        print(cherrypy.session[self.IMAGE_LIST_KEY])
        return next(i for i, x in enumerate(cherrypy.session[self.IMAGE_LIST_KEY]) if x[0] == image_file_name)

    def _get_image_num(self, i):
        return cherrypy.session[self.IMAGE_LIST_KEY][i][0]
        
    def _num_images(self):
        return len(cherrypy.session[self.IMAGE_LIST_KEY])

    IMAGE_LIST_KEY = 'image_list'
    @cherrypy.expose
    def index(self):
        image_list = self._generate_image_list()
        cherrypy.session[self.IMAGE_LIST_KEY] = image_list
        image_selection_html = self._generate_image_selection_list(image_list)
        upload_message = cherrypy.session[self.UPLOAD_MSG_KEY] if self.UPLOAD_MSG_KEY in cherrypy.session else ''
        if self.UPLOAD_MSG_KEY in cherrypy.session:
            del cherrypy.session[self.UPLOAD_MSG_KEY]
        with open('photos.html') as f:
            html = f.read()
        return html.replace('<<UPLOAD_MESSAGE>>', upload_message). \
                replace('<<IMAGE_SELECTION_LIST>>', image_selection_html). \
                replace('<<SELECTED_IMAGE_PATH>>', 'slides/%s' % image_list[0][0] if len(image_list) > 0 else ''). \
                replace('<<SELECTED_IMAGE_FILE_NAME>>', image_list[0][0] if len(image_list) > 0 else '')

    @cherrypy.expose
    def next(self, image_file_name):
        i = self._get_image_list_index(image_file_name)
        i += 1
        if i >= self._num_images():
            i = 0
        return self._get_image_num(i)

    @cherrypy.expose
    def previous(self, image_file_name):
        i = self._get_image_list_index(image_file_name)
        i -= 1
        if i < 0:
            i = self._num_images() - 1
        return self._get_image_num(i)

    @cherrypy.expose
    def upload(self, myFiles):
        if not isinstance(myFiles, (list, tuple)):
            myFiles = [myFiles]
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

    @cherrypy.expose
    def delete(self, image_file_name):
        if cherrypy.request.method != 'DELETE':
            raise cherrypy.HTTPError(405)
        try:
            file_path = os.path.join(self._upload_dir, image_file_name)
            print('deleting %s' % file_path)
            os.unlink(file_path)
            # Remove the image file name from the session image list
            cherrypy.session[self.IMAGE_LIST_KEY] = [x for x in cherrypy.session[self.IMAGE_LIST_KEY] if x[0] != image_file_name]
        except Exception as e:
            raise cherrypy.HTTPError(500, str(e))

    @cherrypy.expose
    def resize_images(self):
        if cherrypy.request.method != 'PUT':
            raise cherrypy.HTTPError(405)
        # TODO: Make this more sophisticated
        ret = os.system('./resize-images slides')
        if ret != 0:
            raise cherrypy.HTTPError(500)

    @cherrypy.expose
    def adjust_images(self):
        if cherrypy.request.method != 'PUT':
            raise cherrypy.HTTPError(405)
        # TODO: Make this more sophisticated
        ret = os.system('./adjust-images slides')
        if ret != 0:
            raise cherrypy.HTTPError(500)

    @cherrypy.expose
    def make_thumbnails(self):
        if cherrypy.request.method != 'PUT':
            raise cherrypy.HTTPError(405)
        # TODO: Make this more sophisticated
        ret = os.system('./make-thumbnails slides slides/thumbnails')
        if ret != 0:
            raise cherrypy.HTTPError(500)

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