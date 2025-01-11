import torch
import yaml
import cv2
import numpy as np

from nets import nn
from utils import util

def non_max_suppression(prediction, conf_thres=0.25, nms_thres=0.45, classes=None, agnostic=False, multi_label=False, max_det=300):
    # prediction: Tensor of shape (batch_size, num_predictions, 6) where 6 are [x, y, width, height, confidence, class]
    output = [None] * prediction.shape[0]
    for i, pred in enumerate(prediction):
        # Filter predictions by confidence
        pred = pred[pred[:, 4] > conf_thres]
        
        if len(pred) == 0:
            continue

        # Get class labels
        if classes is not None:
            pred = pred[(pred[:, 5:6] == classes).any(1)]

        # Perform non-max suppression for each class
        boxes = pred[:, :4]
        scores = pred[:, 4] * pred[:, 5]  # confidence * class score
        labels = pred[:, 5]

        keep = torch.ops.torchvision.nms(boxes, scores, nms_thres)
        output[i] = torch.cat((boxes[keep], scores[keep].unsqueeze(1), labels[keep].unsqueeze(1)), 1)

    return output

@torch.no_grad()
def is_human(path):
    # Load model
    model = torch.load('./weights/best.pt', map_location='cpu')['model'].float().eval()
    
    # Preprocess image
    image = cv2.imread(path)
    shape = image.shape[:2]
    r = 640 / max(shape)  # Resize ratio
    new_shape = (int(shape[1] * r), int(shape[0] * r))
    image = cv2.resize(image, new_shape, interpolation=cv2.INTER_LINEAR)
    
    # Padding to 640x640
    pad_w = (640 - new_shape[0]) % 32
    pad_h = (640 - new_shape[1]) % 32
    image = cv2.copyMakeBorder(image, 0, pad_h, 0, pad_w, cv2.BORDER_CONSTANT)

    # Convert to RGB, normalize, and prepare tensor
    x = image[..., ::-1].transpose(2, 0, 1)  # BGR to RGB and transpose to CHW
    x = np.ascontiguousarray(x)  # Ensure contiguous memory layout
    x = torch.from_numpy(x).float() / 255.0
    x = x.unsqueeze(0)  # Add batch dimension
    
    # Inference
    outputs = model(x)
    
    # NMS
    outputs = non_max_suppression(outputs, 0.25, 0.7)
    for output in outputs:
        if len(output) > 0:  # If there are detections
            return True
    
    return False

def profile(params, input_size=640):
    model = nn.yolo_v8_n(len(params['names']))
    shape = (1, 3, input_size, input_size)

    model.eval()
    model(torch.zeros(shape))
    params = sum(p.numel() for p in model.parameters())


if __name__ == "__main__":
    with open('utils/args.yaml', errors='ignore') as f:
        params = yaml.safe_load(f)

    util.setup_seed()
    util.setup_multi_processes()

    profile(params)
    print(is_human('test.jpg'))
