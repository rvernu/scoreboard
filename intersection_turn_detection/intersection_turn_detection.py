import json

import requests

import gpxpy
import gpxpy.gpx

import math
from datetime import timedelta

import osmnx as ox
from geopy.distance import geodesic


# 위도, 경도를 하버사인 공식을 이용해서 거리로 변환
def haversine(lat1, lon1, lat2, lon2):
    R = 6371

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance


# 수평경로와 수직경로, 시간차를 이용해서 속도를 계산
def calculate_speed(point1, point2):
    latlng_distance = haversine(point1.latitude, point1.longitude, point2.latitude, point2.longitude)  # km
    final_distance = math.sqrt(latlng_distance ** 2 + ((point1.elevation - point2.elevation) / 1000) ** 2)  # km
    time = (point2.time - point1.time).total_seconds() / 3600  # hour
    if time > 0:
        return round(final_distance / time, 4)  # km/h
    else:
        return 0


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

def find_nearest_intersection(lat, lon):
    G = ox.graph_from_point((lat, lon), dist=50, network_type='drive')
    nearest_node = ox.distance.nearest_nodes(G, lon, lat)
    node_location = (G.nodes[nearest_node]['y'], G.nodes[nearest_node]['x'])
    return node_location

if __name__ == "__main__":
    intersection = find_nearest_intersection(37.50292, 127.0427)
    print(f"가장 가까운 교차로 위치: {intersection}")