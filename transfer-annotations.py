from flask import Flask
import glob
from lxml import etree
app = Flask(__name__)

@app.route("/transfer_annotations")
def transfer_annotations(x_points, y_points, name, folder):
    matches = glob.glob("Homographies/" + folder + "/*" + name + "*.jpg")
    for match in matches:
        boundaries_list, H = parse_file(match)
        outliers_x = filter(lambda x: x > max_x or x < min_x, xPoints)
        outliers_y = filter(lambda y: y > max_y or y < min_y, yPoints)
        if len(outliers_x) == 0 and len(outliers_y) == 0:
             
        #if all points within min/max 
            #transform points using H
            #check to see if all transformed points within bounds of second image
            

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
    return boundaries_list, H       

def write_to_xml(filename, xPoints, yPoints, anno_name):
   proposed_name = "PROPOSED" + anno_name 
    
if __name__ == "__main__":
    app.run()
