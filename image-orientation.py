#!/usr/bin/env python3
from PIL import Image, ExifTags
import sys

def get_image_orientation(image_file_name):
    print(image_file_name)
    with Image.open(image_file_name) as img:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                break
        exif=dict(img._getexif().items())
        print(exif[orientation])
        print('W=%u, H=%u' % (img.width, img.height))
        return "portrait" if exif[orientation] in [6, 8] else "landscape"
    return "unknown"

print(get_image_orientation(sys.argv[1]))