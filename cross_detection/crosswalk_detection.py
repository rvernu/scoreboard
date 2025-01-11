# https://github.com/kairess/crosswalk-traffic-light-detection-yolov5
import torch
import numpy as np
import cv2
from utils.datasets import letterbox
from utils.general import non_max_suppression, scale_coords

# 횡단보도,신호등 모델
MODEL_PATH = 'weights/best.pt'

img_size = 640
conf_thres = 0.5  # confidence threshold
iou_thres = 0.45  # NMS IOU threshold
max_det = 1000  # maximum detections per image
classes = None  # filter by class
agnostic_nms = False  # class-agnostic NMS

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
ckpt = torch.load(MODEL_PATH, map_location=device)
model = ckpt['ema' if ckpt.get('ema') else 'model'].float().fuse().eval()
class_names = ['crosswalk', 'redlight', 'greenlight'] # model.names
stride = int(model.stride.max())

net = cv2.dnn.readNetFromDarknet('weights/yolov4-ANPR.cfg', 'weights/yolov4-ANPR.weights')

def is_crosswalk(path):
    img = cv2.imread(path)

    # preprocess
    img_input = letterbox(img, img_size, stride=stride)[0]
    img_input = img_input.transpose((2, 0, 1))[::-1]
    img_input = np.ascontiguousarray(img_input)
    img_input = torch.from_numpy(img_input).to(device)
    img_input = img_input.float()
    img_input /= 255.
    img_input = img_input.unsqueeze(0)

    # inference 횡단보도,신호등
    pred = model(img_input, augment=False, visualize=False)[0]

    # postprocess
    pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)[0]

    pred = pred.cpu().numpy()

    pred[:, :4] = scale_coords(img_input.shape[2:], pred[:, :4], img.shape).round()

    for p in pred:
        '''
        class_name = class_names[int(p[5])]
        x1, y1, x2, y2 = p[:4]
        '''

        return True
    return False

if __name__ == "__main__":
    print(is_crosswalk("test.jpg"))
    print(is_crosswalk("test2.webp"))
    print(is_crosswalk("test3.jpg"))
