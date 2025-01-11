import os

from app import create_app
import sys

sys.path.append("./cross_detection/")
sys.path.append("./cross_detection/utils")

sys.path.append("./human_detection/")
sys.path.append("./human_detection/human_utils")

sys.path.append("./lane_detection/")
sys.path.append("./lane_detection/ultrafastLaneDetector")

app = create_app()
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
if __name__ == '__main__':
    app.run(debug=True)
