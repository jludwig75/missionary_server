import cherrypy
import os
import json
import random
from PIL import Image, ExifTags
from threading import Lock

_ROTATION_MAP = { 1: 'landscape', 6: 'portrait_right', 8: 'portrait_left', 3: 'upside'}

def _get_image_orientation(image_file_name):
    #print(image_file_name)
    with Image.open(image_file_name) as img:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                break
        try:
            exif=dict(img._getexif().items())
        except:
            # If there is no EXIF data, go by the width to height of the image
            return 'landscape' if img.width >= img.height else 'portrait_right'
        #print(exif[orientation])
        #print('W=%u, H=%u' % (img.width, img.height))
        return _ROTATION_MAP[exif[orientation]] if exif[orientation] in _ROTATION_MAP else "unknown"
    return "unknown"

class SlideShow(object):
    _SLIDESHOW_FILE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'tif', 'tiff']
    _IMAGE_LIST_KEY = 'image_list'
    def __init__(self, image_dir_path):
        self._image_dir_path = image_dir_path
        self._lock = Lock()

    # call with self._lock held
    def _generate_image_list(self):
        cherrypy.session['image_list'] = []
        for file_name in os.listdir(self._image_dir_path):
            extension = file_name.split('.')[-1]
            if extension.lower() in self._SLIDESHOW_FILE_EXTENSIONS:
                cherrypy.session['image_list'].append('slides/' + file_name)

    # call with self._lock held
    def _get_image_list(self):
        if not self._IMAGE_LIST_KEY in cherrypy.session or len(cherrypy.session[self._IMAGE_LIST_KEY]) == 0:
            self._generate_image_list()
        return cherrypy.session[self._IMAGE_LIST_KEY]

    # call with self._lock held
    def _remove_image_from_list(self, image_file_name):
        cherrypy.session[self._IMAGE_LIST_KEY].remove(image_file_name)

    @cherrypy.expose
    def next(self):
        with self._lock:
            file_name = random.choice(self._get_image_list())
            self._remove_image_from_list(file_name)
            # print('selected "%s" left: %s' % (file_name, str(cherrypy.session['image_list'])))
        ret = {'file_name': file_name, 'orientation': _get_image_orientation(file_name)}
        return json.dumps(ret)
