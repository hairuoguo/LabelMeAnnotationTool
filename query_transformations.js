function send_transformation(LM_xml, annotation, image){
    xPoints = annotation.GetPtsX();
    yPoints = annotation.GetPtsY();
    imName = image.file_info.GetImName();
    folder = image.file_info.GetDirName();
    annoName =  
     
    
    
    $.ajax({
        type: 'POST',
        url: "transfer_annotations.py"
        data: {x_points: xPoints, y_points: yPoints, name: name, folder: folder}
        dataType: "text"
        
    })
}
