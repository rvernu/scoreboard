from app import create_app
import sys

sys.path.append("./cross_detection/")
sys.path.append("./human_detection/")
sys.path.append("./lane_detection/")

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
