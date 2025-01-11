import requests

def correct_coords(coordinates):
    url = "https://api.mapbox.com/matching/v5/mapbox/driving"
    access_token = "pk.eyJ1IjoiaHl1bnNlb25nMzAyMCIsImEiOiJjbTVzYWhpMngwanZ0MmpvYXZudTg1b2t4In0.DrAUsAGLpbkhSqUo2PgtZA"

    coordinate_list = [f"{lon},{lat}" for lon, lat in coordinates]
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

import math

def calculate_angle(points):
    point1, point2, point3 = points

    lat1, lon1 = math.radians(point1[0]), math.radians(point1[1])
    lat2, lon2 = math.radians(point2[0]), math.radians(point2[1])
    lat3, lon3 = math.radians(point3[0]), math.radians(point3[1])

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
def calculate_speed(points):
    point1, point2 = points
    latlng_distance = haversine(point1[0], point1[1], point2[0], point2[1]) # km
    # final_distance = math.sqrt(latlng_distance ** 2 + ((point1.elevation - point2.elevation) / 1000) ** 2) # km
    time = float(point2[2] - point1[2]) / 3600 # hour
    if time > 0:
        return round(latlng_distance / time, 4) # km/h
    else:
        return 0

if __name__ == "__main__":
    gps_datas = [ # [lat,lng,sec]
        [-117.17282,32.71204,0],
        [-117.17288,32.71225,1],
        [-117.17293,32.71244,2],
        [-117.17292,32.71256,3],
        [-117.17298,32.712603,4],
        [-117.17314,32.71259,5],
        [-117.17334,32.71254,6]
    ]

    velocities = [calculate_speed(coord_datas) for coord_datas in list(zip(gps_datas, gps_datas[1:]))]
    angles = [calculate_angle(coord_datas) for coord_datas in list(zip(gps_datas, gps_datas[1:], gps_datas[2:]))]

    print(velocities)
    print(angles)

    # print(correct_coords(gps_datas))
