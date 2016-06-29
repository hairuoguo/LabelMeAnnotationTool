function send_transformation(annoName, annotation, image){
    xPoints = annotation.GetPtsX();
    yPoints = annotation.GetPtsY();
    imName = image.file_info.GetImName();
    folder = image.file_info.GetDirName();
      
    $.ajax({
        type: 'POST',
        url: "transfer_annotations.py",
        data: {x_points: xPoints, y_points: yPoints, name: name, folder: folder},
        dataType: "text"
    });
}
