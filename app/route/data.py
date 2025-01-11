import random
import time

from flask import Blueprint, render_template, request
from werkzeug.utils import secure_filename

import cross_detection
import human_detection
import lane_detection

data_route = Blueprint('data', __name__, url_prefix='/data')

@data_route.route('/', methods=['POST'])
def upload_image():
    try:
        longitude = request.form['longitude']
        latitude = request.form['latitude']
        f = request.files['image']

        result = {}
        result['cross_detection_result'] = cross_detection.is_crosswalk(f)
        result['human_detection_result'] = human_detection.is_human(f)
        result['lane_detection_result'] = lane_detection.is_rightmost(f)

        file_hash = str(hash(f))[:3] + str(int(time.time())) + str(random.randint(0, 10000))
        f.save("./tmp/" + secure_filename(file_hash))
        return result
    except Exception as e:
        print(e)
        return 'Error uploading image'