import cv2
import numpy as np

from ultrafastLaneDetector import UltrafastLaneDetector, ModelType

model_path = "weights/tusimple_18.pth"
model_type = ModelType.TUSIMPLE
use_gpu = False

# Initialize lane detection model
lane_detector = UltrafastLaneDetector(model_path, model_type, use_gpu)

def is_rightmost(data):
    if isinstance(data, np.ndarray):
        return check_rightmost(data)
    elif isinstance(data, str):
        img = cv2.imread(data)
        return check_rightmost(img)
    else:
        raise Exception("Either image path or image itself must be given.")

def check_rightmost(img):
    return lane_detector.detect_lanes(img)

'''
def test(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)

    # Detect the lanes
    output_img = lane_detector.detect_lanes(img)

    # Draw estimated depth
    cv2.namedWindow("Detected lanes", cv2.WINDOW_NORMAL) 
    cv2.imshow("Detected lanes", output_img)
    cv2.waitKey(0)

    cv2.imwrite("output.jpg", output_img)
'''

if __name__ == "__main__":
    print(is_rightmost("../tmp/test1.jpg"))
