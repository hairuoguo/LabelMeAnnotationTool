'''
Output json dict format:
    dict
        folder:
            state
                annotation:
                    name
                    img_num (face of cube)
                    x_min
                    x_max
                    y_min
                    y_max
            labels:
                label:
                    end_state
                
'''

import glob, json
from sets import Set
import xml.etree.ElementTree as ET

def main():
    IMG_DIR = "Images/"
    ANNO_DIR = "Annotations/"

    annotations = glob.glob(ANNO_DIR + "*/*.jpg")
    poly_dict = {}    

    for annotation in annotations:
        tree = ET.parse(annotation)
        root = tree.getroot()
        folder = root.find('folder').text
        if folder not in data_dict.keys():
            data_dict[folder] = {}
        img = root.find('filename').text
        state = img.split('_')[0]
        if state not in data_dict[folder].keys():
            data_dict[folder][state] = []
        anno_objects = root.findall('object')
        for anno_object in anno_objects:
            if int(anno_object.find('deleted').text) == 1:
                continue
            anno_dict = {}
            anno_dict['name'] = anno_name
            anno_dict['img_num'] = int(img.split('_')[1]) 
            anno_name = anno_object.find('name').text
            anno_name = anno_name.lower().replace('proposed_', '')
            polygon = anno_object.find('polygon')
            pts = polygon.findall('pt')
            x_set = Set()
            y_set = Set()
            for pt in pts:
                x_set.add(float(pt.find('x').text))
                y_set.add(float(pt.find('y').text))
            anno_dict['min_x'] = min(x_set)
            anno_dict['max_x'] = max(x_set)
            anno_dict['min_y'] = min(y_set)
            anno_dict['max_y'] = max(y_set) 
            data_dict[folder][state].append(anno_dict)
    for folder in data_dict:
        folder['labels'] = []
        labels_set = Set()
        for state in folder:
            labels = [data_dict[folder][n]['name'] for n in data_dict[folder]]
            labels_set.update(labels)
    for label in labels_set:
        biggest_size = 0
        biggest_state = None
        for state in folder:
            size = max([(n['max_x'] - n['min_x'])*(n['max_y'] - n['min_y']) if n['name'] == label for n in state])
            if size > biggest_size:
                biggest_size = size
                biggest_state = state
        folder['labels'].append({label: biggest_state})
    with open('dataset_annos.json', 'w') as outfile:
        json.dump(data_dict, outfile)  
 


if __name__ == "__main__":
    main()


