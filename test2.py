import requests

def get_turn_direction_osrm(start_coords, end_coords):
    """
    OSRM API를 사용하여 경로 계산 후 교차로에서 좌회전, 우회전, 유턴 정보 추출
    
    Parameters:
    - start_coords: 출발 지점 (위도, 경도) 튜플
    - end_coords: 도착 지점 (위도, 경도) 튜플
    
    Returns:
    - 교차로에서 가능한 좌회전, 우회전, 유턴 정보를 포함한 리스트
    """
    
    # OSRM API URL (OSRM Public API 사용)
    url = "http://router.project-osrm.org/route/v1/driving"
    
    # 경로를 요청할 좌표 (start_coords, end_coords)
    coordinates = f"{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}"
    
    # 요청 URL 완성
    request_url = f"{url}/{coordinates}?steps=true&alternatives=false&geometries=geojson"
    
    # API 요청
    response = requests.get(request_url)
    
    if response.status_code != 200:
        raise Exception(f"API 요청 실패: {response.status_code}")
    
    # 응답 데이터 분석
    directions = response.json()
    steps = directions['routes'][0]['legs'][0]['steps']
    
    # 회전 가능 여부를 기록할 리스트
    turn_info = []

    for step in steps:
        print(step)
        instruction = step['instruction'].lower()  # 교차로 지시사항
        if "turn right" in instruction:
            turn_info.append("우회전 가능")
        elif "turn left" in instruction:
            turn_info.append("좌회전 가능")
        elif "u-turn" in instruction:
            turn_info.append("유턴 가능")
    
    return turn_info

# 사용 예시
start_coords = (37.7749, -122.4194)  # 샌프란시스코 (위도, 경도)
end_coords = (37.8044, -122.2712)    # 오클랜드 (위도, 경도)

turn_directions = get_turn_direction_osrm(start_coords, end_coords)
print(turn_directions)
