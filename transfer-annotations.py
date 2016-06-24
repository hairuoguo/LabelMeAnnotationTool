from flask import Flask
import glob, datetime
from lxml import etree as ET
app = Flask(__name__)

@app.route("/transfer_annotations")
def transfer_annotations(x_points, y_points, name, folder):
    matches = glob.glob("Homographies/" + folder + "/*" + name + "*.jpg")
    for match in matches:
        boundaries_list, H = parse_file(match)
        img1_max_x = boundaries_list[0]
        img1_min_x = boundaries_list[1]
        img1_max_y = boundaries_list[2]
        img1_min_y = boundaries_list[3]
    

        img2_max_x = boundaries_list[4]
        img2_min_x = boundaries_list[5]
        img2_max_y = boundaries_list[6]
        img2_min_y = boundaries_list[7]

        outliers_x = filter(lambda x: x > img1_max_x or x < img1_min_x, xPoints)
        outliers_y = filter(lambda y: y > img1_max_y or y < img1_min_y, yPoints)
        if len(outliers_x) == 0 and len(outliers_y) == 0:
            x_points = np.array(x_points)
            y_points = np.array(y_points)
            ones = np.ones(x_points.size)
            points_matrix = np.matrix(np.vstack((x_points, y_points, ones)))
            transposed_points = np.asarray(points_matrix*H)
            transposed_points = transposed_points/transposed_points[2, 0]
            transposed_x = transposed_points[0, :]
            transposed_y = transposed_points[1, :]
            transposed_points = []
            for x, y in transposed_x, transposed_y:
                if x < img2_max_x and x > img2_min_x and y < img2_max_y and y > img2_min_y:
                      transposed_points.append((x, y))
            if len(transposed_points) > 2:
                write_to_xml(image2, transposed_points, anno_name)
            
               
         
            

def parse_file(filename, image_name):
    with open(filename) as f:
        content = f.readlines()
    line_1 = [int(x) for x in content[0].strip([" ", "\n"]).split(" ")]
    line_2 = [int(x) for x in content[1].strip([" ", "\n"]).split(" ")]
    line_3 = [int(x) for x in content[2].strip([" ", "\n"]).split(" ")]

    H = np.array([line_1, line_2, line_3])
    
    image1 = content[3].strip([" ", "\n"]).split(".")[0] + ".JPG"
    image2 = content[7].strip([" ", "\n"]).split(".")[0] + ".JPG"

    boundaries_list = []
    for line in content[3:-1]:
        corner = line.strip([" ", "\n"]).split(" ")[1] 
        boundaries_list.append(corner)

    if image2 == image_name:
        H = np.linalg.inv(H)
    
       
    f.close()
    return boundaries_list, np.matrix(H)       

def write_to_xml(image_name, folder, points, anno_name):
    proposed_name = "PROPOSED" + anno_name
    if os.ispath("Annotations/" + filename):
        xml = ET.parse("Annotations/" + filename)
    else:
        xml = ET.parse("annotationCache/XMLTemplates/labelme.xml")
        xml.get("annotation").set("filename", image_name)
        xml.get("annotation").set("folder", folder)
        anno_object = ET.Element("object")
        
    name_element = anno_object.append(ET.Element("name"))
    name_element.text = anno_name 
    deleted_element = anno_object.append(ET.Element("deleted"))
    verified_element = anno_object.append(ET.Element("verified"))
    date_element = anno_object.append(ET.Element("date"))
    date_element.text = str(datetime.now().strftime("%d-%b-%Y %H:%M:%S")) 
    id_element = anno_object.append(ET.Element("id")) 
    id_element = xml.xpath('count(//object)')  
    parts_element = anno_object.append(ET.Element("parts"))
    parts_element.append(ET.Element("hasparts"))
    parts_element.append(ET.Element("ispartof"))
    polygon_element = anno_object.append(ET.Element("polygon"))
    polygon_element.append(ET.Element("username"))
    for point in points:
        pt = ET.element("pt")
        x = ET.element("x")
        x.text = point[0]
        y = ET.element("y")
        y.text = point[1]
        pt.append(x)
        pt.append(y)
        polygon_element.append(pt) 
    xml_tree = ET.ElementTree(xml)
    xml_tree.write("Annotations/" + filename, pretty_print=True) 
    
if __name__ == "__main__":
    app.run()
