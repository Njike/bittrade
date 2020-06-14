from datetime import datetime
import os
from app import app


def imageHandler(image, date=datetime.now()):
    """
        handles processing and saving images to the server
        @param image: request image from the form data
        @param date: date at which the image was uploaded
    """
    now = round(datetime.now().timestamp())
    fmt = image.filename.split('.')[1]
    filepath = os.path.join(f"{date.strftime('%Y/%m/%d')}", f"IMG-{now}.{fmt}" )
    path = os.path.join(app.config["UPLOADS"], f"{date.strftime('%Y/%m/%d')}")
    if not os.path.isdir(path):
        os.makedirs(path)

    else:
        print(f"Couldnt create directory {path}")
    print(path, os.getcwd())
    print(os.path.dirname(os.path.abspath(__file__)), "cwd")
    image.save(os.path.join(path, f"IMG-{now}.{fmt}"))
    filename = "/".join(path.split("/")[1:])
    print(filename)
    return filepath

# Helper functions
def allowed_image(filename):
    
    if not "." in filename:
        return False
    
    ext = filename.rsplit(".",1)[1]
    
    return ext.lower() in app.config['ALLOWED_IMAGE_EXTENTIONS']

