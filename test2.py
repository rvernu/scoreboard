'''
import json

import requests

import gpxpy
import gpxpy.gpx

import math
from datetime import timedelta


import osmnx as ox
from geopy.distance import geodesic

# 트랙 데이터 출력
def extract_track_data(gpx_data):
    for track in gpx_data.tracks:
        for segment in track.segments:
            prev_point = None
            i = 0
            for point in segment.points:
                latitude = point.latitude
                longitude = point.longitude
                elevation = point.elevation
                time = point.time
                
                # 각 트랙 포인트 출력
                print(f"Point {i}: Latitude: {latitude}, Longitude: {longitude}, Elevation: {elevation}, Time: {time}")
                if prev_point != None:
                    print(f"Speed from {i-1} -> {i}: {calculate_speed(prev_point, point)} km/h")
                
                prev_point = point
                i += 1

# 위도, 경도 정보로 도로 위치를 반환하는 함수
def request_road_data(latitude: float, longitude: float):
    url = "http://overpass-api.de/api/interpreter"

    # Overpass QL 쿼리, 반경 20미터 내의 모든 도로 정보를 가져온다
    overpass_query = f"""
    [out:json];
    way["highway"](around:20, {latitude}, {longitude});
    out body;
    """

    params = {
        "data": overpass_query
    }

    response = requests.get(url, params=params)
    return response.json()

# 정보 출력하기
def print_road_data(data):
    for element in data['elements']:
        if 'tags' in element and 'highway' in element['tags']:
            print(f"도로 정보: {json.dumps(element, indent=4)}")
            # print(f"도로 ID: {element['id']}, 도로 종류: {element['tags']['highway']}")
            # print("도로 태그:", element['tags'])
'''
