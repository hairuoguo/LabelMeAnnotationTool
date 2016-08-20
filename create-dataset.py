'''
Output json dict format:
    dict
        folder:
            state:
                [annotation:
                    name
                    img_num (face of cube)
                    x_min
                    x_max
                    y_min
                    y_max
                ]
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

    annotations = glob.glob(ANNO_DIR + "*/*.xml")
    data_dict = {}    
    annos_count = 0
    for annotation in annotations:
        tree = ET.parse(annotation)
        root = tree.getroot()
        folder = root.find('folder').text
        if folder == "practice" or folder == "example_folder":
            continue
        if folder not in data_dict.keys():
            data_dict[folder] = {}
        img = root.find('filename').text.replace('.jpg', '')
        state = img.split('_')[0]
        if state not in data_dict[folder].keys():
            data_dict[folder][state] = []
        anno_objects = root.findall('object')
        for anno_object in anno_objects:
            if int(anno_object.find('deleted').text) == 1:
                continue
            annos_count += 1
            anno_dict = {}
            anno_dict['img_num'] = int(img.split('_')[1]) 
            anno_name = anno_object.find('name').text
            anno_name = anno_name.lower().replace('proposed_', '')
            anno_dict['name'] = anno_name
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
    labels_set = Set()
    for folder in data_dict:
        data_dict[folder]['labels'] = []
        for state in data_dict[folder]:
            if state == 'labels':
                continue
            labels = [n['name'] for n in data_dict[folder][state]]
            labels_set.update(labels)
    for label in labels_set:
        biggest_size = 0
        biggest_state = None
        for state in data_dict[folder]:
            if state == 'labels':
                continue
            bbox_areas = [(n['max_x'] - n['min_x'])*(n['max_y'] - n['min_y']) for n in data_dict[folder][state] if n['name'] == label]
            if len(bbox_areas) != 0:
                size = sum(bbox_areas)
            else:
                size = 0
            if size > biggest_size:
                biggest_size = size
                biggest_state = state
        data_dict[folder]['labels'].append({label: biggest_state})
    with open('dataset_annos.json', 'w') as outfile:
        json.dump([data_dict, annos_count], outfile)  
 


if __name__ == "__main__":
    main()


