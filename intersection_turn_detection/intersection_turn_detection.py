import json
import math
import requests


def correct_coords(coordinates):
    url = "https://api.mapbox.com/matching/v5/mapbox/driving"
    access_token = "pk.eyJ1IjoiaHl1bnNlb25nMzAyMCIsImEiOiJjbTVzYWhpMngwanZ0MmpvYXZudTg1b2t4In0.DrAUsAGLpbkhSqUo2PgtZA"

    coordinate_list = [f"{coordinate.longitude},{coordinate.latitude}" for coordinate in coordinates]
    formatted_coords = ";".join(coordinate_list)

    data = {
        'coordinates': formatted_coords
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(f"{url}?access_token={access_token}", data=data, headers=headers)

    if response.status_code == 200:
        tracepoints = response.json()["tracepoints"]

        result = []
        for tracepoint in tracepoints:
            if tracepoint["alternatives_count"] == 0:
                result.append(tracepoint["location"])

        return result
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")


intersections = json.load(open('crossroadMapInfo.json', 'r', encoding='utf-8'))

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

# 가장 가까운 교차점을 탐색
def find_nearest_intersection(lat, lon):
    min_distance = 50/1000  # 50m
    nearest_intersection = None

    for intersection in intersections:
        distance = haversine(lat, lon, intersection['mapCtptIntLat'], intersection['mapCtptIntLot'])
        if distance < min_distance:
            min_distance = distance
            nearest_intersection = intersection

    return nearest_intersection if nearest_intersection != 5/1000 else None


# 수평경로와 수직경로, 시간차를 이용해서 속도를 계산
def calculate_speed(points):
    point1, point2 = points
    latlng_distance = haversine(point1.latitude, point1.longitude, point2.latitude, point2.longitude) # km
    # final_distance = math.sqrt(latlng_distance ** 2 + ((point1.elevation - point2.elevation) / 1000) ** 2) # km
    time = float(point2.timestamp - point1.timestamp) / 3600 # hour
    if time > 0:
        return round(latlng_distance / time, 4) # km/h
    else:
        return 0

# 특정 방향으로의 진행에서의 각도 차이를 계산
def calculate_angle(points):
    point1, point2, point3 = points

    lat1, lon1 = math.radians(point1.latitude), math.radians(point1.longitude)
    lat2, lon2 = math.radians(point2.latitude), math.radians(point2.longitude)
    lat3, lon3 = math.radians(point3.latitude), math.radians(point3.longitude)

    vec1_lat = lat1 - lat2
    vec1_lon = lon1 - lon2
    vec2_lat = lat3 - lat2
    vec2_lon = lon3 - lon2

    dot_product = (vec1_lat * vec2_lat) + (vec1_lon * vec2_lon)
    magnitude1 = math.sqrt(vec1_lat**2 + vec1_lon**2)
    magnitude2 = math.sqrt(vec2_lat**2 + vec2_lon**2)

    if magnitude1 == 0 or magnitude2 == 0:
        raise ValueError("Magnitude of one of the vectors is zero. Points must be distinct.")

    cos_angle = dot_product / (magnitude1 * magnitude2)
    cos_angle = max(-1.0, min(1.0, cos_angle))

    angle_rad = math.acos(cos_angle)
    angle_deg = math.degrees(angle_rad)

    return angle_deg - 180

# 급격한 가속도를 탐지
# def detect_rapid_acceleration(points):
#     REF = 5
#     speed = [calculate_speed([points[i], points[i + 1]]) for i in range(len(points) - 1)]
#     acceleration = [(speed[i] - speed[i - 1]) / ((points[i].timestamp - points[i-1].timestamp)/3600) for i in range(1, len(speed))]
#
#     rapid_acceleration = [points[i] for i in range(1, len(acceleration)) if acceleration[i] > REF]
#     return rapid_acceleration

def detect_wrong_intersection(points):
    on_intersections = [find_nearest_intersection(point.latitude, point.longitude) for point in points]
    start, end = 0, 0
    last = None
    pairs = []
    for end in range(len(on_intersections)):
        if on_intersections[end].get('mapCtptIntId') != last:
            if start != end & on_intersections[start] is not None:
                pairs.append((start, end))
            start = end
            last = on_intersections[end].get('mapCtptIntId')

    result = []
    for pair in pairs:
        if not is_turncorrectly(points[pair[0]:pair[1]], velocity_threshold=10):
            result.append(pair)

    return result


# 회전이 올바른지를 탐지
def is_turncorrectly(gps_datas, velocity_threshold=15, angle_threshold=45): # km/h, degree
    velocities = [calculate_speed(coord_datas) for coord_datas in list(zip(gps_datas, gps_datas[1:]))]
    mean_velocities = [(velocity_datas[0] + velocity_datas[1])/2 for velocity_datas in list(zip(velocities, velocities[1:]))]
    angles = [calculate_angle(coord_datas) for coord_datas in list(zip(gps_datas, gps_datas[1:], gps_datas[2:]))]

    result = 0
    for datas in list(zip(mean_velocities, angles)):
        if datas[0] >= velocity_threshold:
            result += angles

    return abs(result) >= angle_threshold


if __name__ == "__main__":
    intersection = find_nearest_intersection(37.50292, 127.0427)
    print(f"가장 가까운 교차로 위치: {intersection}")

    class GPSData:
        def __init__(self, latitude, longitude, timestamp):
            self.latitude = latitude
            self.longitude = longitude
            self.timestamp = timestamp

    gps_datas = [ # [lat,lng,sec]
        GPSData(37.56967206298715, 126.98305472675337, 0),
        GPSData(37.56997165247484, 126.98311408642932, 1),
        GPSData(37.5702734944059, 126.98317344607365, 2),
        GPSData(37.57035681947376, 126.98305457161894, 3),
        GPSData(37.570379288071585, 126.98266687040835, 4),
        GPSData(37.57036571048112, 126.98224521872721, 5),
        GPSData(37.57037237795481, 126.98165659827269, 6)
    ]

    detect_wrong_intersection(gps_datas)

    # print(correct_coords(gps_datas))
