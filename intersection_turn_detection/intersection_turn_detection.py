import json
import math
import requests


def correct_coords(coordinates):
    url = "https://api.mapbox.com/matching/v5/mapbox/driving"
    access_token = "pk.eyJ1IjoiaHl1bnNlb25nMzAyMCIsImEiOiJjbTVzbGc4d2wwa2VpMmtxeDhmZDdtMms5In0.DKZrscTW4O3cvF0MI9L3Fw"

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
    last = on_intersections[end].get('itstId') if on_intersections[end] else None
    pairs = []
    for end in range(len(on_intersections)):
        if on_intersections[end]:
            if on_intersections[end].get('itstId') != last:
                if start != end and (on_intersections[start] is not None):
                    pairs.append([start, end])
                start = end
                last = on_intersections[end].get('itstId')
        elif last:
            if start != end and (on_intersections[start] is not None):
                pairs.append([start, end])
            start = end
            last = None
    if start != end and (on_intersections[start] is not None):
        pairs.append([start, end])
    
    result = []
    for pair in pairs:
        if not is_turncorrectly(points[pair[0]:pair[1]], velocity_threshold=10):
            result.append(pair)
    return result


# 회전이 올바른지를 탐지
def is_turncorrectly(gps_datas, velocity_threshold=15, angle_threshold=45): # km/h, degree
    if len(gps_datas) <= 2:
        return True

    velocities = [calculate_speed(coord_datas) for coord_datas in list(zip(gps_datas, gps_datas[1:]))]
    mean_velocities = [(velocity_datas[0] + velocity_datas[1])/2 for velocity_datas in list(zip(velocities, velocities[1:]))]
    angles = [calculate_angle(coord_datas) for coord_datas in list(zip(gps_datas, gps_datas[1:], gps_datas[2:]))]

    result = 0
    for datas in list(zip(mean_velocities, angles)):
        if datas[0] >= velocity_threshold:
            result += datas[1]

    return abs(result) <= angle_threshold

# 리스트를 앞 뒤가 일부 겹치게 자르기
def split_list_overlap(input_list, chunk_size=100, overlap=5):
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    chunks = []
    start = 0
    while start < len(input_list):
        end = start + chunk_size
        chunks.append(input_list[start:end])
        start += chunk_size - overlap

    return chunks

# 유저의 경로를 바탕으로 완벽히 정확한 경로를 반환
# TODO: 시간 정보 포함하기
def get_accurate_path(gps_datas, overlap=5):
    result = []
    
    for path_chunk in split_list_overlap(gps_datas):
        corrected_coords = correct_coords(path_chunk)
        if len(result) >= overlap and len(corrected_coords) >= overlap:
            overlap1 = result[-overlap:]
            overlap2 = corrected_coords[:overlap]
            
            averaged_overlap = [(x + y) / 2 for x, y in zip(overlap1, overlap2)]
            
            merged_list = result[:-overlap] + averaged_overlap + corrected_coords[overlap:]
            result = merged_list
        else:
            result.append(corrected_coords)
    
    result = result[:len(gps_datas)] # 혹시 예상하지 못한 길이 추가가 있다면 미연에 방지. 어차피 마지막 몇 개는 도착지점 부근이므로 크게 상관 없음
    timestamps = [datas.timestamp for datas in gps_datas]
    return list(zip(result, timestamps))

if __name__ == "__main__":
    class GPSData:
        def __init__(self, latitude, longitude, timestamp):
            self.latitude = latitude
            self.longitude = longitude
            self.timestamp = timestamp

    gps_data_straight = [ # [lat,lng,sec]
        GPSData(37.56999868840013, 126.98315652859004, 0),
        GPSData(37.57016763148278, 126.98320176879615, 1),
        GPSData(37.57033206353528, 126.98320456176337, 2),
        GPSData(37.57039286172259, 126.98307154284846, 3),
        GPSData(37.570397343049386, 126.98290740767071, 4),
        GPSData(37.570397314617075, 126.98271214462073, 5)
    ]

    # print(correct_coords(gps_data_straight))

    '''
    print(detect_wrong_intersection(gps_data_straight))

    gps_data_curve = [
        GPSData(37.56999868840013, 126.98315652859004, 0),
        GPSData(37.57017662973051, 126.98311969993564, 1),
        GPSData(37.57024869311873, 126.98300648792207, 2),
        GPSData(37.57033877261069, 126.98286780249536, 3),
        GPSData(37.570397314617075, 126.98271214462073, 4)
    ]
    print(detect_wrong_intersection(gps_data_curve))
    '''
    
    # print(correct_coords(gps_datas))
