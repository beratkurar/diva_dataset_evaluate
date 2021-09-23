import os
from glob import glob
import cv2
import numpy as np
from tqdm import tqdm
from xml.etree import ElementTree as ET

_ns = {'p': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}
dataset_folder='CB55/'
ground_folder='CB55_ground_image/'
output_folder='crop_cb55_ground/'
os.makedirs('crop_cb55_ground')
resize_ratio=None

def get_page_filename(image_filename: str) -> str:
    return os.path.join(os.path.dirname(image_filename),
                        'page',
                        '{}.xml'.format(os.path.basename(image_filename)[:-4]))

def get_ground_filename(image_filename: str) -> str:
    return os.path.join(ground_folder,
                        '{}_gt.png'.format(os.path.basename(image_filename)[:-4]))

def get_basename(image_filename: str) -> str:
    directory, basename = os.path.split(image_filename)
    return '{}'.format( basename.split('.')[0])


def save_and_resize(img: np.array, filename: str, size=None) -> None:
    if size is not None:
        h, w = img.shape[:2]
        resized = cv2.resize(img, (int(w*size), int(h*size)),
                             interpolation=cv2.INTER_LINEAR)
        cv2.imwrite(filename, resized)
    else:
        cv2.imwrite(filename, img)


def xml_to_coordinates(t):
    result = []
    for p in t.split(' '):
        values = p.split(',')
        assert len(values) == 2
        x, y = int(float(values[0])), int(float(values[1]))
        result.append((x,y))
    result=np.array(result)
    return result

image_filenames_list = glob('{}*.jpg'.format(dataset_folder))

for image_filename in tqdm(image_filenames_list):
    
    ground_filename=get_ground_filename(image_filename)
    print (ground_filename)
    img = cv2.imread(ground_filename)
    page_filename = get_page_filename(image_filename)
    xml_page = ET.parse(page_filename)
    page_elements = xml_page.find('p:Page', _ns)
    regions= page_elements.findall('p:TextRegion', _ns)
    for region in regions:
        coords=region.find('p:Coords', _ns)
        points = coords.attrib['points']
        cnt=xml_to_coordinates(points)
        (x,y,w,h) = cv2.boundingRect(cnt)
        crop_img = img[y:y+h, x:x+w]
        save_name=get_basename(image_filename)+'.png'
        print(save_name)
        save_and_resize(crop_img, output_folder+save_name, resize_ratio)


