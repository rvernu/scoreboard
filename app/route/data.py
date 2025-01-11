import random
import time

from flask import Blueprint, render_template, request
from werkzeug.utils import secure_filename

data_route = Blueprint('data', __name__, url_prefix='/data')

@data_route.route('/', methods=['POST'])
def upload_image():
    try:
        longitude = request.form['longitude']
        latitude = request.form['latitude']
        f = request.files['image']
        file_hash = str(hash(f))[:3] + str(int(time.time())) + str(random.randint(0, 10000))
        f.save("./tmp/" + secure_filename(file_hash))
        return 'Image uploaded successfully'
    except Exception as e:
        print(e)
        return 'Error uploading image'