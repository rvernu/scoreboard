import os
import random
import traceback

from flask import Blueprint, request

import cross_detection
import human_detection
import lane_detection
import gps_detection

data_route = Blueprint('data', __name__, url_prefix='/data')

route_count = {}
route_gps = {}
route_crosswalk = {}
route_human = {}
route_lane = {}

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

        cross_detection_result = cross_detection.is_crosswalk(file_path)
        human_detection_result = human_detection.is_human(file_path, 0.1, 0.2)
        lane_detection_result = lane_detection.is_rightmost(file_path)

        if cross_detection_result:
            route_crosswalk[route_id].append(timestamp)
        if human_detection_result:
            route_human[route_id].append(timestamp)
        if lane_detection_result:
            route_lane[route_id].append(timestamp)
        return {
            'cross_detection_result': cross_detection_result,
            'human_detection_result': human_detection_result,
            'lane_detection_result': lane_detection_result
        }
    except Exception as e:
        print(e)
        return 'Error uploading image'

@data_route.route('/image', methods=['POST'])
def upload_image():
    try:
        route_id = request.form['route_id']
        f = request.files['image']
        timestamp = request.form['timestamp']

        file_path = f"./tmp/{route_id}/{route_count[route_id]}"
        f.save(file_path)

        cross_detection_result = cross_detection.is_crosswalk(file_path)
        human_detection_result = human_detection.is_human(file_path, 0.1, 0.2)
        lane_detection_result = lane_detection.is_rightmost(file_path)

        if cross_detection_result:
            route_crosswalk[route_id].append(timestamp)
        if human_detection_result:
            route_human[route_id].append(timestamp)
        if lane_detection_result:
            route_lane[route_id].append(timestamp)
        return {
            'cross_detection_result': cross_detection_result,
            'human_detection_result': human_detection_result,
            'lane_detection_result': lane_detection_result
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

        route_gps[route_id].append({'longitude': float(longitude), 'latitude': float(latitude), 'timestamp': int(timestamp)})
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
        route_crosswalk[route_id] = []
        route_human[route_id] = []
        route_lane[route_id] = []
        print(route_id)
        return {'route_id': route_id}
    except Exception as e:
        print(e)
        return 'Error starting route'

@data_route.route('/end', methods=['POST'])
def end():
    try:
        route_id = request.form['route_id']
    
        score = 100
        drive_log = []
        # wrong_intersection = detect_wrong_intersection(route_gps[route_id])
        
        print('asdf')

        accurate_path = route_gps[route_id] # gps_detection.get_accurate_path(route_gps[route_id])
        print('asdf.')
        # 차선 우측 통행 결과
        for timestamp in route_lane[route_id]:
            score -= 5
            drive_log.append([gps_detection.get_loc_from_timestamp(accurate_path, timestamp), "도로 우측 통행 미숙 -5"])
        print('asdf')
        wrong_turns = gps_detection.detect_wrong_turn(route_gps[route_id])
        correct_crosses, wrong_crosses = gps_detection.detect_wrong_cross(route_gps[route_id])
        correct_human, wrong_human = gps_detection.detect_wrong_human(route_gps[route_id])
        print('asdf')
        for wrong_turn in wrong_turns:
            score -= 5
            drive_log.append([accurate_path[wrong_turn[0]:wrong_turn[1]], "올바르지 않은 좌/우회전 -5"])
        print('asdf')
        for wrong_cross in wrong_crosses:
            score -= 5
            drive_log.append([accurate_path[wrong_cross[0]:wrong_cross[1]], "횡단보도에서 킥보드 주행 -5"])
        print('asdf')
        for correct_data in correct_human:
            score += 3
            drive_log.append([accurate_path[correct_data[0]:correct_data[1]], "주위에 사람이 있는 경우 감속 +3"])
        print('asdf')
        for wrong_data in wrong_human:
            score -= 5
            drive_log.append([accurate_path[wrong_data[0]:wrong_data[1]], "주위에 사람이 있는 경우 감속하지 않음 -5"])
        print('asdf')
        print(score, drive_log)
        print('asdf')
        return {'score': score, 'drive_log': drive_log}
    except Exception as e:
        traceback.print_exc()
        return 'Error ending route'
