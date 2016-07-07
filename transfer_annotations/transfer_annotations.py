#!/usr/bin/python
from __future__ import print_function
import threading
from OpenSSL import SSL
from flask import Flask, request, current_app, make_response
from flask_cors import CORS, cross_origin
import glob, datetime, json, os, time, random
import numpy as np
from datetime import datetime, timedelta
from functools import update_wrapper
from lxml import etree as ET
from OpenSSL import SSL
import sys


app = Flask(__name__)
lock = threading.Lock()
def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

def merge_xmls(folder, name):
    main_xml_file = "Annotations/" + folder + "/" + name.replace("jpg", "xml")
    if not os.path.isfile(main_xml_file):
        return str(False)
    main_xml = ET.parse(main_xml_file)
    main_root = main_xml.getroot()
    object_files = glob.glob(main_xml_file + ".[0-9]*")
    for object_file in object_files:
        object_xml = ET.parse(object_file)
        object_xml.find('id').text = str(main_xml.xpath('count(//object)'))
        object_root = object_xml.getroot()
        main_root.append(object_root)
        os.remove(object_file)
    main_xml.write(main_xml_file, pretty_print=True)
         
        


@app.route("/add_lock", methods=['POST'])
def add_lock():
    global lock
    lock.acquire()
    json_request = request.get_json(force=True) 
    name = json_request["name"]
    folder = json_request['folder']
    merge_xmls(folder, name)
    '''
    lock_file = open("Images/" + folder + "/" + name + ".lock", "w")
    all_lock_files = glob.glob("Images/" + folder + "/" + "*.lock") 
    for lock_file in all_lock_files:
        modified_time = os.path.getmtime(lock_file)
        delta = datetime.now() - datetime.fromtimestamp(modified_time)
        if delta.seconds > 5400:
            lock_name = os.path.basename(lock_file)
            merge_xmls(folder, lock_name)
            os.remove(lock_file)
    '''
    lock.release()
    
    return str(True)
            
@app.route("/remove_lock", methods=['POST'])
def remove_lock():
    global lock
    lock.acquire()
    json_request = request.get_json(force=True)
    name = json_request["name"]
    folder = json_request['folder']
    #merge_xmls(folder, name)
    #os.remove("Images/" + folder + "/" + name + ".lock")
    lock.release() 
    return str(True)
        
        

@app.route("/transfer_annotations", methods=['POST'])
def transfer_annotations():
    global lock
    lock.acquire()
    json_request = request.get_json(force=True)
    x_points = json_request['x_points']
    y_points = json_request['y_points']
    name = json_request['name']
    folder = json_request['folder']
    anno_name = json_request['anno_name']
    name = name.replace(".jpg", "")
    with open("Homographies/" + folder + '/' + name.replace(".jpg", "") + "_matches.json") as json_file:
        data = json.load(json_file)
        matches = data["matches"] 
    for match in matches:
        
        width = int(match["width"])
        height = int(match["height"])

        H = np.array(match["H"])
        img2_name = match["that"].replace(".JPG", ".jpg")
        x_points = np.array(x_points)
        y_points = np.array(y_points)
        ones = np.ones(x_points.size)
        points_matrix = np.matrix(np.vstack((x_points, y_points, ones)))
        transposed_points = np.asarray(np.matrix(H)*points_matrix)
        s = transposed_points[2, 0]
        transposed_x = transposed_points[0, :]/s
        transposed_y = transposed_points[1, :]/s
        transposed_points = []
        corners_matrix = np.matrix(np.hstack((np.array([0, 0, 1]).reshape((3, 1)), np.array([width, height, 1]).reshape((3, 1)))))
        corners = np.asarray(np.matrix(H)*corners_matrix)
        corners = corners/corners[2, 0]
        outliers_x = filter(lambda x: x > corners[0, 1] or x < corners[0, 0] or x < 0 or x > width, transposed_x)
        outliers_y = filter(lambda y: y > corners[1, 1] or y < corners[1, 0] or y < 0 or y > height, transposed_y)
        if len(outliers_x) == 0 and len(outliers_y) == 0:
            for x, y, in zip(transposed_x, transposed_y): 
                transposed_points.append((x, y))
            write_to_xml(img2_name, folder, transposed_points, anno_name)
    lock.release() 
    return str(True) 
           
         
            
def create_append_assign(anno_object, new_tag, text):
    new_element = ET.Element(new_tag)
    if text != "":
        new_element.text = text
    anno_object.append(new_element)
    return new_element

def write_to_xml(image_name, folder, points, anno_name):
    proposed_name = "PROPOSED" + anno_name
    filename = folder + "/" + image_name.replace(".jpg", ".xml")
    if os.path.exists("Annotations/" + filename):
        xml = ET.parse("Annotations/" + filename)
    else:
        xml = ET.parse("annotationCache/XMLTemplates/labelme.xml")
        xml.find("filename").text = image_name 
        xml.find("folder").text = folder
    
    anno_object = ET.Element("object")
    create_append_assign(anno_object, "name", anno_name)
    create_append_assign(anno_object, "deleted", str(0))
    create_append_assign(anno_object, "verified", str(0))
    create_append_assign(anno_object, "date", datetime.now().strftime("%d-%b-%Y %H:%M:%S"))
    create_append_assign(anno_object, "id", str(xml.xpath('count(//object)')))
    create_append_assign(anno_object, "occluded", "n")
    attributes_element = create_append_assign(anno_object, "attributes", "")
    parts_element = create_append_assign(anno_object, 'parts', "")
    parts_element.append(ET.Element("hasparts"))
    parts_element.append(ET.Element("ispartof"))
    attributes_element.append(parts_element)
    polygon_element = create_append_assign(anno_object, 'polygon', "")
    create_append_assign(polygon_element, 'username', 'transfer_bot')
    for point in points:
        pt = ET.Element("pt")
        x = ET.Element("x")
        x.text = str(point[0])
        y = ET.Element("y")
        y.text = str(point[1])
        pt.append(x)
        pt.append(y)
        polygon_element.append(pt)
    root = xml.getroot()
    root.append(anno_object)
    '''
    if not os.path.isfile("Images/" + folder + "/" + image_name + ".lock"): 
        xml.write("Annotations/" + filename, pretty_print=True)
    else:
        iobject_tree = ET.ElementTree(anno_object) 
        filename = filename + "." + str(random.randint(100000, 999999))
        object_tree.write("Annotations/" + filename, pretty_print=True)
    '''
    if os.path.isfile("Annotations/" + filename):
        object_tree = ET.ElementTree(anno_object) 
        filename = filename + "." + str(random.randint(100000, 999999))
        object_tree.write("Annotations/" + filename, pretty_print=True)  
    else:
        xml.write("Annotations/" + filename, pretty_print=True) 
        
@app.route("/")
def hello_world():
    return "Hello world!"
    
    
if __name__ == "__main__":
   app.run(threaded=True)
