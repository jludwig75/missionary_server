#!/usr/bin/env python3
import sys
import os
from PIL import Image, ExifTags


TARGET_WIDTH_TO_HEIGHT_RATIO = 4.0 / 3.0
IMAGE_FILE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'tif', 'tiff']

class IMG_ORIENTATION:
    Landscape = 1
    LandscapeUpsideDown = 3
    PortraitRight = 6
    PortraitLeft = 8
    Unknown = 99

def get_image_orientation(img):
    key_names = [ExifTags.TAGS[key] for key in ExifTags.TAGS.keys()]
    for key in ExifTags.TAGS.keys():
        if ExifTags.TAGS[key] == 'Orientation':
            break
    try:
        exif=dict(img._getexif().items())
    except:
        # If there is no EXIF data, go by the width to height of the image
        return IMG_ORIENTATION.Landscape if img.width >= img.height else IMG_ORIENTATION.PortraitRight
    orientation = exif[key]
    return orientation

def correct_image_rotation(img, orientation):
    if orientation == IMG_ORIENTATION.PortraitRight:
        print('  rotating source image 270 degrees')
        img = img.rotate(270, expand=True)
    elif orientation == IMG_ORIENTATION.PortraitLeft:
        print('  rotating source image 90 degrees')
        img = img.rotate(90, expand=True)
    elif orientation == IMG_ORIENTATION.LandscapeUpsideDown:
        print('  rotating source image 180 degrees')
        img = img.rotate(180, expand=True)
    return img

def pad_image_to_landscape(img):
    if img.width > img.height:
        return img
    print('  padding image to landscape')
    target_width = int(TARGET_WIDTH_TO_HEIGHT_RATIO * img.height)
    new_image = Image.new('RGBA', (target_width, img.height), (0, 0, 0, 0))

    offset = int((target_width - img.width) / 2)
    new_image.paste(img, (offset, 0))
    return new_image

def save_image(img, image_file_path, delete_original=True):
    file_name, extension = os.path.splitext(image_file_path)
    if extension.lower() == '.png':
        file_name = file_name + '_adjusted'
        extension = 'png'
    else:
        extension = 'png'
    new_file_path = '%s.%s' % (file_name, extension)
    print('  saving image %s as %s' % (image_file_path, new_file_path))
    img.save(new_file_path)
    if delete_original:
        os.unlink(image_file_path)
    return new_file_path

def adjust_image(image_file_path):
    print('adjusting image %s' % image_file_path)
    img = Image.open(image_file_path)
    orientation = get_image_orientation(img)

    if orientation == IMG_ORIENTATION.Landscape:
        # nothing to do
        print('  no adjustments needed to %s' % image_file_path)
        return
    
    # correct the rotation
    file_name = image_file_path.split('/')[-1]
    if not file_name.startswith('FB_IMG_'):
        img = correct_image_rotation(img, orientation)
    
    # pad to landscape
    if orientation in [IMG_ORIENTATION.PortraitLeft, IMG_ORIENTATION.PortraitRight]:
        img = pad_image_to_landscape(img)

    # save image
    save_image(img, image_file_path)

def adjust_images(image_dir_path):
    file_names = os.listdir(image_dir_path)
    for file_name in file_names:
        extension = file_name.split('.')[-1]
        if extension.lower() in IMAGE_FILE_EXTENSIONS:
            adjust_image(os.path.join(image_dir_path, file_name))

def rotate_image(image_file_name, degrees, delete_original):
    img = Image.open(image_file_name)
    img = img.rotate(degrees, expand=True)
    if img.height > img.width:
        img = pad_image_to_landscape(img)
    return save_image(img, image_file_name, delete_original)
