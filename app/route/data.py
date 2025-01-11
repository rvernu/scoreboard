import os
import random
import shutil

from flask import Blueprint, request

import cross_detection
import human_detection
import lane_detection
from intersection_turn_detection.intersection_turn_detection import detect_wrong_intersection

data_route = Blueprint('data', __name__, url_prefix='/data')

route_count = {}
route_gps = {}

@data_route.route('/', methods=['POST'])
def upload_image_and_gps():
    try:
        route_id = request.form['route_id']
        longitude = request.form['longitude']
        latitude = request.form['latitude']
        timestamp = request.form['timestamp']
        f = request.files['image']

        file_path = f"./tmp/{route_id}/{route_count[route_id]}"
        f.save(file_path)

        route_gps[route_id].append({'longitude': longitude, 'latitude': latitude, 'timestamp': timestamp})

        return {
            'cross_detection_result': cross_detection.is_crosswalk(file_path),
            'human_detection_result': human_detection.is_human(file_path, 0.1, 0.2),
            'lane_detection_result': lane_detection.is_rightmost(file_path)
        }
    except Exception as e:
        print(e)
        return 'Error uploading image'

@data_route.route('/image', methods=['POST'])
def upload_image():
    try:
        route_id = request.form['route_id']
        f = request.files['image']

        file_path = f"./tmp/{route_id}/{route_count[route_id]}"
        f.save(file_path)

        return {
            'cross_detection_result': cross_detection.is_crosswalk(file_path),
            'human_detection_result': human_detection.is_human(file_path, 0.1, 0.2),
            'lane_detection_result': lane_detection.is_rightmost(file_path)
        }
    except Exception as e:
        print(e)
        return 'Error uploading image'

@data_route.route('/gps', methods=['POST'])
def upload_gps():
    try:
        route_id = request.form['route_id']
        longitude = request.form['longitude']
        latitude = request.form['latitude']
        timestamp = request.form['timestamp']

        route_gps[route_id].append({'longitude': longitude, 'latitude': latitude, 'timestamp': timestamp})
        return "1"
    except Exception as e:
        print(e)
        return 'Error uploading gps'

@data_route.route('/start', methods=['POST'])
def start():
    try:
        route_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
        while os.path.exists(f'./tmp/{route_id}'):
            route_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
        os.mkdir(f'./tmp/{route_id}')
        route_count[route_id] = 0
        route_gps[route_id] = []
        return {'route_id': route_id}
    except Exception as e:
        print(e)
        return 'Error starting route'

@data_route.route('/end', methods=['POST'])
def end():
    try:
        route_id = request.form['route_id']

        wrong_intersection = detect_wrong_intersection(route_gps[route_id])

        shutil.rmtree(f'./tmp/{route_id}')
        del route_count[route_id]
        del route_gps[route_id]
        return "1"  # TODO: 결과 반환
    except Exception as e:
        print(e)
        return 'Error ending route'