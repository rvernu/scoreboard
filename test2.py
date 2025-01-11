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

if __name__ == "__main__":
    coordinates = [
        [-117.17282,32.71204],
        [-117.17288,32.71225],
        [-117.17293,32.71244],
        [-117.17292,32.71256],
        [-117.17298,32.712603],
        [-117.17314,32.71259],
        [-117.17334,32.71254]
    ]

    print(correct_coords(coordinates))
