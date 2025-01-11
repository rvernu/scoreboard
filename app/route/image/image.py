import random
import time

from flask import Blueprint, render_template, request
from werkzeug.utils import secure_filename

image_route = Blueprint('image', __name__, url_prefix='/image')

@image_route.route('/', methods=['POST'])
def upload_image():
    try:
        # Get the image from the request
        f = request.files['image']
        file_hash = str(hash(f))[:3] + str(int(time.time())) + str(random.randint(0, 10000))
        f.save("./tmp/" + secure_filename(file_hash))
        return 'Image uploaded successfully'
    except Exception as e:
        print(e)
        return 'Error uploading image'