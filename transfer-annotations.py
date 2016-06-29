#!/usr/bin/python
from __future__ import print_function
from flask import Flask, request, current_app, make_response
from flask_cors import CORS, cross_origin
import glob, datetime, json, os
import numpy as np
from datetime import datetime, timedelta
from functools import update_wrapper
from lxml import etree as ET
from OpenSSL import SSL
import sys
app = Flask(__name__)
CORS(app)
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


@app.route("/transfer_annotations", methods=['POST'])
def transfer_annotations():
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
        img1_max_x = match["this_max_x"]
        img1_min_x = match["this_min_x"]
        img1_max_y = match["this_max_y"]
        img1_min_y = match["this_min_y"]
    

        img2_max_x = match["that_max_x"]
        img2_min_x = match["that_min_x"]
        img2_max_y = match["that_max_y"]
        img2_min_y = match["that_min_y"]

        H = np.array(match["H"])
        img2_name = match["that"].replace(".JPG", ".jpg")
        outliers_x = filter(lambda x: x > img1_max_x or x < img1_min_x, x_points)
        outliers_y = filter(lambda y: y > img1_max_y or y < img1_min_y, y_points)
        if len(outliers_x) == 0 and len(outliers_y) == 0:
            print("check", file=sys.stderr)
            x_points = np.array(x_points)
            y_points = np.array(y_points)
            ones = np.ones(x_points.size)
            points_matrix = np.matrix(np.vstack((x_points, y_points, ones)))
            transposed_points = np.asarray(H*points_matrix)
            s = transposed_points[2, 0]
            transposed_x = transposed_points[0, :]/s
            transposed_y = transposed_points[1, :]/s
            transposed_points = []
            for x, y in zip(transposed_x, transposed_y):
                if x < img2_max_x and x > img2_min_x and y < img2_max_y and y > img2_min_y:
                      transposed_points.append((x, y))
            if len(transposed_points) > 2:
                write_to_xml(img2_name, folder, transposed_points, anno_name)
    return str(True) 
               
         
            
'''
def parse_file(filename):
    with open(filename) as f:
        content = f.readlines()
        line_1 = [int(x) for x in content[0].strip([" ", "\n"]).split(" ")]
        line_2 = [int(x) for x in content[1].strip([" ", "\n"]).split(" ")]
        line_3 = [int(x) for x in content[2].strip([" ", "\n"]).split(" ")]

        H = np.array([line_1, line_2, line_3])
        
        image1 = content[3].strip([" ", "\n"]).split(".")[0] + ".jpg"
        image2 = content[7].strip([" ", "\n"]).split(".")[0] + ".jpg"

        boundaries_list = []
        for line in content[3:-1]:
            corner = line.strip([" ", "\n"]).split(" ")[1] 
            boundaries_list.append(corner)

        if image2 == image_name + ".jpg":
            H = np.linalg.inv(H)
        
           
        f.close()
    return boundaries_list, np.matrix(H), image2_name       
'''
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
    parts_element = create_append_assign(anno_object, 'parts', "")
    parts_element.append(ET.Element("hasparts"))
    parts_element.append(ET.Element("ispartof"))
    polygon_element = create_append_assign(anno_object, 'polygon', "")
    polygon_element.append(ET.Element("username"))
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
    xml.write("Annotations/" + filename, pretty_print=True) 
    
if __name__ == "__main__":
    app.run(host='0.0.0.0')
