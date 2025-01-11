# https://github.com/jahongir7174/YOLOv8-human?tab=readme-ov-file

import torch
# import yaml
import cv2
import numpy as np

# from nets import nn
from utils import util

@torch.no_grad()
def is_human(path, x_limit, y_limit):
    # Load model
    model = torch.load('./weights/best.pt', map_location='cpu')['model'].float()
    model.eval()
    input_size = 640

    image = cv2.imread(path)
    shape = image.shape[:2]

    r = input_size / max(shape[0], shape[1])
    if r != 1:
        resample = cv2.INTER_LINEAR if r > 1 else cv2.INTER_AREA
        image = cv2.resize(image, dsize=(int(shape[1] * r), int(shape[0] * r)), interpolation=resample)

    height, width = image.shape[:2]

    r = min(1.0, input_size / height, input_size / width)

    pad = int(round(width * r)), int(round(height * r))
    w = np.mod((input_size - pad[0]), 32) / 2
    h = np.mod((input_size - pad[1]), 32) / 2

    if (width, height) != pad:
        image = cv2.resize(image, pad, interpolation=cv2.INTER_LINEAR)

    top, bottom = int(round(h - 0.1)), int(round(h + 0.1))
    left, right = int(round(w - 0.1)), int(round(w + 0.1))
    image = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT)

    # Convert HWC to CHW, BGR to RGB
    x = image.transpose((2, 0, 1))[::-1]  # BGR to RGB
    x = np.ascontiguousarray(x)
    x = torch.from_numpy(x)
    x = x.unsqueeze(dim=0)

    # Don't use CUDA, use CPU
    x = x.float()  # Change to float32 as we're on CPU
    x /= 255  # Normalize

    # Inference
    outputs = model(x)
    
    # NMS
    outputs = util.non_max_suppression(outputs, 0.25, 0.7)
    for output in outputs:
        output[:, [0, 2]] -= w  # x padding
        output[:, [1, 3]] -= h  # y padding
        output[:, :4] /= min(height / shape[0], width / shape[1])
        
        output[:, 0].clamp_(0, shape[1])  # x1
        output[:, 1].clamp_(0, shape[0])  # y1
        output[:, 2].clamp_(0, shape[1])  # x2
        output[:, 3].clamp_(0, shape[0])  # y2

        for box in output:
            box = box.cpu().numpy()
            x1, y1, x2, y2, score, index = box
            
            if abs(x1-x2) >=  x_limit * shape[0] and abs(y1-y2) > y_limit * shape[1]:
                return True
    
    return False

'''
def profile(params, input_size=640):
    model = nn.yolo_v8_n(len(params['names']))
    shape = (1, 3, input_size, input_size)

    model.eval()
    model(torch.zeros(shape))
    params = sum(p.numel() for p in model.parameters())
'''

if __name__ == "__main__":
    '''
    with open('utils/args.yaml', errors='ignore') as f:
        params = yaml.safe_load(f)

    util.setup_seed()
    util.setup_multi_processes()

    profile(params)
    '''

    print(is_human('test.jpg', 0.1, 0.2))
    print(is_human('test2.jpg', 0.1, 0.2))
    print(is_human('test3.jpg', 0.1, 0.2))
    print(is_human('test3.webp', 0.1, 0.2))
